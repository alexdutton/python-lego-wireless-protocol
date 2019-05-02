import logging

import gatt

from lego_wireless.constants import CHARACTERISTIC_UUID
from lego_wireless.enums import HubAttachedIOEvent, MessageType
from lego_wireless.hub_io import TrainMotor, HubIO
from lego_wireless.messages import HubAttachedIO

logger = logging.getLogger(__name__)


class Hub(gatt.Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ports = {}
        self.hub_characteristic = None

    @property
    def train_motor(self):
        for hub_io in self.ports.values():
            if isinstance(hub_io, TrainMotor):
                return hub_io

    def connect_succeeded(self):
        super().connect_succeeded()
        logger.info("[%s] Connected" % (self.mac_address))
        self.hub_characteristic.enable_notifications()

    def connect_failed(self, error):
        super().connect_failed(error)
        logger.warning("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def characteristic_enable_notification_succeeded(self, *args, **kwargs):
        super().characteristic_enable_notification_succeeded(*args, **kwargs)
        logger.info("[%s] Characteristic enable notification_succeeded: %s %s" % (self.mac_address, str(args), str(kwargs)))

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
        message = self.parse_message(value)
        if isinstance(message, HubAttachedIO):
            if message.event in (HubAttachedIOEvent.AttachedIO, HubAttachedIOEvent.AttachedVirtualIO):
                if message.io_type in HubIO.registry:
                    self.ports[message.port] = HubIO.registry[message.io_type](self, message.port)
                else:
                    logger.warning("Unimplemented IOType on port %d: %s", message.port, message.io_type)
            else:
                self.ports.pop(message.port, None)

    def send_message(self, message):
        length = len(message) + 2
        message = bytes([length, 0x00]) + message
        logger.info("Sending message: %r", message)
        self.hub_characteristic.write_value(message)

    def parse_message(self, message):
        length = message[0]
        if not len(message) == length:
            logger.warning("Unexpected message length: %r", message)
            return
        message_type = MessageType(message[2])
        if message_type == MessageType.HubAttachedIO:
            return HubAttachedIO.from_bytes(message[3:])

    def services_resolved(self):
        super().services_resolved()

        for service in self.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid) == CHARACTERISTIC_UUID:
                    self.hub_characteristic = characteristic
                    self.manager.hub_discovered(self)
