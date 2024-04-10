"""Hoymiles Modbus client."""

from dataclasses import asdict, dataclass
from typing import List, Type, Union

from pymodbus.client import ModbusTcpClient
from pymodbus.framer.socket_framer import ModbusSocketFramer

from .datatypes import (
    HMSeriesMicroinverterData,
    MicroinverterType,
    MISeriesMicroinverterData,
    PlantData,
    _serial_number_t,
)


@dataclass
class CommunicationParams:
    """Low level pymodbus communication parameters."""

    timeout: int = 5
    """Request timeout."""
    retries: int = 5
    """Max number of retries per request."""
    retry_on_empty: bool = True
    """Retry if received an empty response."""
    close_comm_on_error: bool = False
    """Close connection on error"""
    strict: bool = True
    """Strict timing, 1.5 character between requests."""
    reconnect_delay: int = 60000 * 5
    """Delay in milliseconds before reconnecting."""


class _CustomSocketFramer(ModbusSocketFramer):
    """Custom framer for fixing data length in received modbus packets."""

    @staticmethod
    def _data_length_fixer(packet):  # pragma: no cover
        fixed_packet = list(packet)
        if len(packet) > 9:
            fixed_packet[8] = len(fixed_packet[9:])
        return bytes(fixed_packet)

    def processIncomingPacket(self, data, callback, unit, **kwargs):
        fixed_data = self._data_length_fixer(data)
        return super().processIncomingPacket(fixed_data, callback, unit, **kwargs)


class HoymilesModbusTCP:
    """Hoymiles Modbus TCP client.

    Gather data from photovoltaic installation based on Hoymiles microinverters managed by Hoymiles DTU (like DTU-pro).
    The client communicates with DTU via Modbus TCP protocol.

    """

    _MAX_MICROINVERTER_COUNT = 100
    _NULL_MICROINVERTER = '000000000000'

    def __init__(
        self, host: str, port: int = 502, microinverter_type: MicroinverterType = MicroinverterType.MI, unit_id: int = 1, dtu_type: int = 0
    ) -> None:
        """Initialize the object.

        Arguments:
            host: DTU address
            port: target DTU modbus TCP port
            microinverter_type: Microinverter type, applies to all microinverters
            unit_id: Modbus unit ID

        """
        self._host: str = host
        self._port: int = port
        self._dtu_serial_number: str = ''
        self._microinverter_data_struct: Type[Union[MISeriesMicroinverterData, HMSeriesMicroinverterData]]
        if microinverter_type == MicroinverterType.MI:
            self._microinverter_data_struct = MISeriesMicroinverterData
        elif microinverter_type == MicroinverterType.HM:
            self._microinverter_data_struct = HMSeriesMicroinverterData
        else:
            raise ValueError('Unsupported microinverter type:', microinverter_type)
        self._unit_id = unit_id
        self._comm_params: CommunicationParams = CommunicationParams()
        self._dtu_type: int = dtu_type

    @property
    def comm_params(self) -> CommunicationParams:
        """Low level communication parameters."""
        return self._comm_params

    def _get_client(self) -> ModbusTcpClient:
        return ModbusTcpClient(self._host, self._port, framer=_CustomSocketFramer, **asdict(self.comm_params))

    @staticmethod
    def _read_registers(client: ModbusTcpClient, start_address, count, unit_id):
        result = client.read_holding_registers(start_address, count, slave=unit_id)
        if result.isError():
            raise result
        return result

    @property
    def microinverter_data(self) -> List[Union[MISeriesMicroinverterData, HMSeriesMicroinverterData]]:
        """Status data from all microinverters.

        Each `get` is a new request and data from the installation.

        """
        data: List[Union[MISeriesMicroinverterData, HMSeriesMicroinverterData]] = []
        with self._get_client() as client:
            for i in range(self._MAX_MICROINVERTER_COUNT):
                if self._dtu_type == 1:
                    start_address = i * 20 + 0x1000
                else:
                    start_address = i * 40 + 0x1000
                result = self._read_registers(client, start_address, 20, self._unit_id)
                microinverter_data = self._microinverter_data_struct.unpack(result.encode()[1:41])
                if microinverter_data.serial_number == self._NULL_MICROINVERTER:
                    break
                data.append(microinverter_data)
        return data

    @property
    def dtu(self) -> str:
        """DTU serial number."""
        if not self._dtu_serial_number:
            with self._get_client() as client:
                result = self._read_registers(client, 0x2000, 3, self._unit_id)
                self._dtu_serial_number = _serial_number_t.unpack(result.encode()[1::])
        return self._dtu_serial_number

    @property
    def plant_data(self) -> PlantData:
        """Plant status data.

        Each `get` is a new request and data from the installation.

        """
        microinverter_data = self.microinverter_data
        data = PlantData(self.dtu, microinverter_data=microinverter_data)
        for microinverter in microinverter_data:
            if microinverter.link_status:
                data.pv_power += microinverter.pv_power
                data.today_production += microinverter.today_production
                data.total_production += microinverter.total_production
                if microinverter.alarm_code:
                    data.alarm_flag = True
        return data
