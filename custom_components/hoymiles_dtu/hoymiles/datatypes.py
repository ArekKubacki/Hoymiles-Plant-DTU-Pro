"""Data structures."""

from binascii import hexlify
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from plum.array import ArrayX
from plum.bigendian import uint8, uint16, uint32
from plum.bytes import BytesX
from plum.decimal import DecimalX
from plum.dump import Record
from plum.structure import Structure, member


class _SerialNumberX(BytesX):
    """Datatype for decoding serial number."""

    def __unpack__(  # type: ignore[override]
        self,
        buffer: bytes,
        offset: int,
        dump: Optional[Record] = None,
        nbytes: Optional[int] = None,
    ) -> tuple[str, int]:
        """Unpack."""
        data, offset = super().__unpack__(buffer, offset, dump, nbytes)
        serial_bytes = hexlify(data)
        return serial_bytes.decode('ascii'), offset

    def __pack__(
        self,
        value: Union[bytes, bytearray],
        pieces: list[bytes],
        dump: Optional[Record] = None,
    ) -> None:
        """Pack."""
        raise NotImplementedError


_udec16p1 = DecimalX(name='udec16p1', nbytes=2, precision=1, byteorder='big', signed=False)
_sdec16p1 = DecimalX(name='sdec16p1', nbytes=2, precision=1, byteorder='big', signed=True)
_udec16p2 = DecimalX(name='udec16p2', nbytes=2, precision=2, byteorder='big', signed=False)

_udec32p1 = DecimalX(name='udec32p1', nbytes=4, precision=1, byteorder='big', signed=False)
_sdec32p1 = DecimalX(name='sdec32p1', nbytes=4, precision=1, byteorder='big', signed=True)
_udec32p2 = DecimalX(name='udec32p2', nbytes=4, precision=2, byteorder='big', signed=False)

_serial_number_t = _SerialNumberX(name='serial_number_t', nbytes=6)
_serial_number_t2 = _SerialNumberX(name='serial_number_t2', nbytes=12)
_reserved = ArrayX(name='reserved', fmt=uint8)
_reserved2 = ArrayX(name='reserved', fmt=uint16)

class _PVCurrentType(Enum):
    """PV current datatype depending on inverter type."""

    MI = _udec16p2
    """MI series."""
    HM = _udec16p2
    """HM series."""
    MIDTU = _udec32p2
    """MI series."""
    HMDTU = _udec32p2
    """HM series."""


def _pv_current_type(serial: str) -> DecimalX:
    if serial.startswith('10'):
        current_type = _PVCurrentType.MI.value
    elif serial.startswith('11'):
        current_type = _PVCurrentType.HM.value
    elif serial == '000000000000':
        # all zero serial number means empty inverter data
        # in this case type of current value is not important
        current_type = _PVCurrentType.MI.value
    else:
        raise ValueError(f"Couldn't detect inverter type for serial {serial}. Please report an issue.")
    return current_type

def _pv_current_typeDTU(serial: str) -> DecimalX:
    if serial.startswith('10'):
        current_type = _PVCurrentType.MIDTU.value
    elif serial.startswith('11'):
        current_type = _PVCurrentType.HMDTU.value
    elif serial == '000000000000':
        # all zero serial number means empty inverter data
        # in this case type of current value is not important
        current_type = _PVCurrentType.MIDTU.value
    else:
        raise ValueError(f"Couldn't detect inverter type for serial {serial}. Please report an issue.")
    return current_type

class InverterData(Structure):  # type: ignore[misc]
    """Inverter data structure."""

    data_type: int = member(fmt=uint8)
    serial_number: str = member(fmt=_serial_number_t)
    """Inverter serial number."""
    port_number: int = member(fmt=uint8)
    """Port number."""
    pv_voltage: Decimal = member(fmt=_udec16p1)
    """PV voltage [V]."""
    pv_current: Decimal = member(fmt=_pv_current_type, fmt_arg=serial_number)  # type: ignore[arg-type]
    """PV current [A]."""
    grid_voltage: Decimal = member(fmt=_udec16p1)
    """Grid voltage [V]."""
    grid_frequency: Decimal = member(fmt=_udec16p2)
    """Grid frequency [Hz]."""
    pv_power: Decimal = member(fmt=_udec16p1)
    """PV power [W]."""
    today_production: int = member(fmt=uint16)
    """Today production [Wh]."""
    total_production: int = member(fmt=uint32)
    """Total production [Wh]."""
    temperature: Decimal = member(fmt=_sdec16p1)
    """Inverter temperature [°C]."""
    operating_status: int = member(fmt=uint16)
    """Operating status."""
    alarm_code: int = member(fmt=uint16)
    """Alarm code."""
    alarm_count: int = member(fmt=uint16)
    """Alarm count."""
    link_status: int = member(fmt=uint8)
    """Link status."""
    reserved: list[int] = member(fmt=_reserved)

class InverterDataOpenDTU(Structure):  # type: ignore[misc]
    """Inverter data structure."""

    data_type: int = member(fmt=uint16)
    serial_number: str = member(fmt=_serial_number_t2)
    """serial_number2: str = member(fmt=_serial_number_t2)"""
    """Inverter serial number."""
    port_number: int = member(fmt=uint16)
    """Port number."""
    pv_voltage: Decimal = member(fmt=_udec32p1)
    """PV voltage [V]."""
    pv_current: Decimal = member(fmt=_pv_current_typeDTU, fmt_arg=serial_number)  # type: ignore[arg-type]
    """PV current [A]."""
    grid_voltage: Decimal = member(fmt=_udec32p1)
    """Grid voltage [V]."""
    grid_frequency: Decimal = member(fmt=_udec32p2)
    """Grid frequency [Hz]."""
    pv_power: Decimal = member(fmt=_udec32p1)
    """PV power [W]."""
    today_production: int = member(fmt=uint32)
    """Today production [Wh]."""
    total_production: int = member(fmt=uint32)
	
    total_production2: int = member(fmt=uint32)
    """Total production [Wh]."""
    temperature: Decimal = member(fmt=_sdec32p1)
    """Inverter temperature [°C]."""
    operating_status: int = member(fmt=uint32)
    """Operating status."""
    alarm_code: int = member(fmt=uint32)
    """Alarm code."""
    alarm_count: int = member(fmt=uint32)
    """Alarm count."""
    link_status: int = member(fmt=uint16)
    """Link status."""
    reserved2: list[int] = member(fmt=_reserved)
@dataclass
class PlantData:
    """Data structure for the whole plant."""

    dtu: str
    """DTU serial number."""
    pv_power: Decimal = Decimal(0)
    """Current production [W]."""
    today_production: int = 0
    """Today production [Wh]."""
    total_production: int = 0
    """Total production [Wh]."""
    alarm_flag: bool = False
    """Alarm indicator. True means that at least one inverter reported an alarm."""
    inverters: list[InverterData] = field(default_factory=list)
    """Data for each inverter."""


@dataclass
class CommunicationParams:
    """Low level pymodbus communication parameters."""

    timeout: float = 5
    """Timeout for a connection request, in seconds."""
    retries: int = 5
    """Max number of retries per request."""
    reconnect_delay: float = 0
    """Minimum delay in seconds.milliseconds before reconnecting.
    Doubles automatically with each unsuccessful connect, from
    **reconnect_delay** to **reconnect_delay_max**.

    Default is 0 which means that reconnecting is disabled."""
    reconnect_delay_max: float = 300
    """Maximum delay in seconds.milliseconds before reconnecting."""
