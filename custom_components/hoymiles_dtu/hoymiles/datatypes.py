"""Data structures."""

from binascii import hexlify
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional, Tuple, Union

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
    ) -> Tuple[str, int]:
        """Unpack."""
        data, offset = super().__unpack__(buffer, offset, dump, nbytes)
        serial_bytes = hexlify(data)
        return serial_bytes.decode('ascii'), offset

    def __pack__(
        self,
        value: Union[bytes, bytearray],
        pieces: List[bytes],
        dump: Optional[Record] = None,
    ) -> None:
        """Pack."""
        raise NotImplementedError


_udec16p1 = DecimalX(name='udec16p1', nbytes=2, precision=1, byteorder='big', signed=False)
_sdec16p1 = DecimalX(name='sdec16p1', nbytes=2, precision=1, byteorder='big', signed=True)
_udec16p2 = DecimalX(name='udec16p2', nbytes=2, precision=2, byteorder='big', signed=False)

_serial_number_t = _SerialNumberX(name='serial_number_t', nbytes=6)
_reserved = ArrayX(name='reserved', fmt=uint8)


class MicroinverterType(Enum):
    """Microinverter type."""

    MI = auto()
    """MI series."""
    HM = auto()
    """HM series."""


class MISeriesMicroinverterData(Structure):
    """MI series microinverter status data structure."""

    data_type: int = member(fmt=uint8)
    serial_number: str = member(fmt=_serial_number_t, doc='Microinverter serial number.')
    port_number: int = member(fmt=uint8, doc='Port number.')
    pv_voltage: Decimal = member(fmt=_udec16p1, doc='PV voltage [V].')
    pv_current: Decimal = member(fmt=_udec16p1, doc='PV current [A].')
    grid_voltage: Decimal = member(fmt=_udec16p1, doc='Grid voltage [V].')
    grid_frequency: Decimal = member(fmt=_udec16p2, doc='Grid frequency [Hz].')
    pv_power: Decimal = member(fmt=_udec16p1, doc='PV power [W].')
    today_production: int = member(fmt=uint16, doc='Today production [Wh].')
    total_production: int = member(fmt=uint32, doc='Total production [Wh].')
    temperature: Decimal = member(fmt=_sdec16p1, doc='Microinverter temperature [°C].')
    operating_status: int = member(fmt=uint16, doc='Operating status.')
    alarm_code: int = member(fmt=uint16, doc='Alarm code.')
    alarm_count: int = member(fmt=uint16, doc='Alarm count.')
    link_status: int = member(fmt=uint8, doc='Link status.')
    reserved: List[int] = member(fmt=_reserved)


class HMSeriesMicroinverterData(MISeriesMicroinverterData):
    """HM series microinverter status data structure."""

    pv_current: Decimal = member(fmt=_udec16p2, doc='PV current [A].')


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
    """Alarm indicator. True means that at least one microinverter reported an alarm."""
    microinverter_data: List[Union[MISeriesMicroinverterData, HMSeriesMicroinverterData]] = field(default_factory=list)
    """Data for each microinverter."""
