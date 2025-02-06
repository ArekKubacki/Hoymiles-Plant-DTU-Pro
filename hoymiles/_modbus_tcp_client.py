from dataclasses import asdict
from typing import TYPE_CHECKING

from pymodbus.client import ModbusTcpClient
from pymodbus.pdu.register_message import ReadHoldingRegistersResponse

if TYPE_CHECKING:  # pragma: no cover
    from .datatypes import CommunicationParams


class _CustomReadHoldingRegistersResponse(ReadHoldingRegistersResponse):

    @staticmethod
    def _data_size_fixer(packet: bytes):
        fixed_packet = list(packet)
        fixed_packet[0] = len(fixed_packet[1:])  # calculate new data size
        return bytes(fixed_packet)

    def decode(self, data: bytes):
        fixed = self._data_size_fixer(data)
        return super().decode(fixed)


def create_modbus_tcp_client(host: str, port: int, comm_params: 'CommunicationParams') -> ModbusTcpClient:
    """Create an instance of Modbus TCP client.

    Arguments:
        host: Host IP address or host name
        port: port number
        comm_params: communication parameters

    """
    client = ModbusTcpClient(
        host=host,
        port=port,
        **asdict(comm_params),
    )

    # Register custom PDU class which fixes data size in a response from DTU
    # (some DTUs send responses with wrong data size byte)
    client.framer.decoder.register(_CustomReadHoldingRegistersResponse)

    return client
