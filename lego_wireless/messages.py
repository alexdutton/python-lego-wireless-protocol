import collections
import struct

from .enums import HubAttachedIOEvent, IOType


class HubAttachedIO(
    collections.namedtuple("HubAttachedIO", ("port", "event", "io_type"))
):
    @classmethod
    def from_bytes(cls, value):
        port, event = struct.unpack("BB", value[:2])
        event = HubAttachedIOEvent(event)
        if event in (
            HubAttachedIOEvent.AttachedIO,
            HubAttachedIOEvent.AttachedVirtualIO,
        ):
            io_type = IOType(struct.unpack("<H", value[2:4])[0])
        else:
            io_type = None
        return cls(port=port, event=event, io_type=io_type)
