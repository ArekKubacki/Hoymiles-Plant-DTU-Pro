"""Hoymiles Modbus client."""

from typing import TYPE_CHECKING

from ._modbus_tcp_client import create_modbus_tcp_client
from .datatypes import CommunicationParams, InverterData, PlantData, _serial_number_t

if TYPE_CHECKING:  # pragma: no cover
    from pymodbus.client import ModbusTcpClient


class HoymilesModbusTCP:
    """Hoymiles Modbus TCP client.

    Gather data from photovoltaic installation based on Hoymiles inverters managed by Hoymiles DTU (like DTU-pro).
    The client communicates with DTU via Modbus TCP protocol.

    """

    _MAX_INVERTER_COUNT = 100
    _NULL_INVERTER = '000000000000'

    def __init__(self, host: str, port: int = 502, unit_id: int = 1, dtu_type: int = 0) -> None:
        """Initialize the object.

        Arguments:
            host: DTU address
            port: target DTU modbus TCP port
            unit_id: Modbus unit ID

        """
        self._host: str = host
        self._port: int = port
        self._dtu_serial_number: str = ''
        self._unit_id = unit_id
        self._comm_params: 'CommunicationParams' = CommunicationParams()
        self._dtu_type: int = dtu_type

    @property
    def comm_params(self) -> CommunicationParams:
        """Low level communication parameters."""
        return self._comm_params

    def _get_client(self) -> "ModbusTcpClient":
        return create_modbus_tcp_client(self._host, self._port, self.comm_params)

    @staticmethod
    def _read_registers(client: 'ModbusTcpClient', start_address: int, count: int, unit_id: int):
        result = client.read_holding_registers(start_address, count=count, slave=unit_id)
        if result.isError():
            raise RuntimeError(f'Received error response {result}')
        return result

    @property
    def inverters(self) -> list[InverterData]:
        """Status data from all inverters.

        Each `get` is a new request and data from the installation.

        """
        data: list[InverterData] = []
        with self._get_client() as client:
            for i in range(self._MAX_INVERTER_COUNT):
                if self._dtu_type == 1:
                    start_address = i * 20 + 0x1000
                    result = self._read_registers(client, start_address, 20, self._unit_id)
                    data_to_unpack = result.encode()[1:41]
                elif self._dtu_type == 2:
                    start_address = i * 40 + 0x1000
                    result = self._read_registers(client, start_address, 40, self._unit_id)
                    data_to_unpack = result.encode()[1:81]
                else:
                    start_address = i * 40 + 0x1000
                    result = self._read_registers(client, start_address, 20, self._unit_id)
                    data_to_unpack = result.encode()[1:41]
                if i < 1 and len(data_to_unpack) < 1:
                    raise RuntimeError("Inverters not mapped yet.")
                inverter_data = InverterData.unpack(data_to_unpack)
                if inverter_data.serial_number == self._NULL_INVERTER:
                    break
                data.append(inverter_data)
        return data

    @property
    def dtu(self) -> str:
        """DTU serial number."""
        if not self._dtu_serial_number:
            with self._get_client() as client:
                if self._dtu_type == 2:
                    result = self._read_registers(client, 0x2000, 3, self._unit_id)
                    self._dtu_serial_number = _serial_number_t2.unpack(result.encode()[1::])
                else:
                    result = self._read_registers(client, 0x2000, 3, self._unit_id)
                    self._dtu_serial_number = _serial_number_t.unpack(result.encode()[1::])         
        return self._dtu_serial_number

    @property
    def plant_data(self) -> PlantData:
        """Plant status data.

        Each `get` is a new request and data from the installation.

        """
        inverters = self.inverters
        data = PlantData(self.dtu, inverters=inverters)
        for inverter in inverters:
            # calculate plant data from inverters
            # only active inverters are included
            if inverter.link_status:
                data.pv_power += inverter.pv_power
                data.today_production += inverter.today_production
                data.total_production += inverter.total_production
                if inverter.alarm_code:
                    data.alarm_flag = True
        return data
