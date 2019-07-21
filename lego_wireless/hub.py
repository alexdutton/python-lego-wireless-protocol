import logging
import struct

import gatt

from lego_wireless import signals
from lego_wireless.constants import CHARACTERISTIC_UUID
from lego_wireless.enums import (
    HubAttachedIOEvent,
    MessageType,
    HubProperty,
    HubPropertyOperation,
)
from lego_wireless.hub_io import TrainMotor, HubIO, LEDLight, RGBLight
from lego_wireless.messages import HubAttachedIO, HubProperties

logger = logging.getLogger(__name__)


class Hub(gatt.Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ports = {}
        self.hub_characteristic = None
        self._battery_level = None

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def train_motor(self):
        for hub_io in self.ports.values():
            if isinstance(hub_io, TrainMotor):
                return hub_io

    @property
    def led_light(self):
        for hub_io in self.ports.values():
            if isinstance(hub_io, LEDLight):
                return hub_io

    @property
    def rgb_light(self):
        for hub_io in self.ports.values():
            if isinstance(hub_io, RGBLight):
                return hub_io

    def connect_succeeded(self):
        super().connect_succeeded()
        self.manager.hubs.add(self)
        signals.hub_connected.send(self.manager, hub=self)
        logger.info("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        logger.warning("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnected_succeeded(self):
        super().disconnect_succeeded()
        signals.hub_disconnected.send(self.manager, hub=self)

    def characteristic_enable_notification_succeeded(self, *args, **kwargs):
        super().characteristic_enable_notification_succeeded(*args, **kwargs)
        logger.info(
            "[%s] Characteristic enable notification_succeeded: %s %s"
            % (self.mac_address, str(args), str(kwargs))
        )

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
        logger.debug("[%s] Message received: %r", self.mac_address, value)
        message = self.parse_message(value)
        if isinstance(message, HubAttachedIO):
            if message.event in (
                HubAttachedIOEvent.AttachedIO,
                HubAttachedIOEvent.AttachedVirtualIO,
            ):
                if message.io_type in HubIO.registry:
                    self.ports[message.port] = HubIO.registry[message.io_type](
                        self, message.port
                    )
                    logger.info("New IO on port %d: %s", message.port, message.io_type)
                    signals.hub_io_connected.send(self, hub_io=self.ports[message.port])
                    self.hub_io_connected(self.ports[message.port])
                else:
                    logger.warning(
                        "Unimplemented IOType on port %d: %s",
                        message.port,
                        message.io_type,
                    )
            else:
                if message.port in self.ports:
                    logger.debug(
                        "Removed IO on port %d: %s",
                        message.port,
                        self.ports[message.port].io_type,
                    )
                    signals.hub_io_disconnected.send(
                        self, hub_io=self.ports[message.port]
                    )
                    self.hub_io_disconnected(self.ports[message.port])
                    del self.ports[message.port]
        elif (
            isinstance(message, HubProperties)
            and message.property == HubProperty.BatteryVoltage
            and message.operation == HubPropertyOperation.Update
        ):
            self._battery_level = int(message.payload[0])
            logger.debug(
                "[%s] Hub battery level: %d%%", self.mac_address, self._battery_level
            )
            signals.hub_battery_level.send(self, battery_level=self._battery_level)
        else:
            logger.warning("Unexpected message: %s", message)

    def hub_io_connected(self, hub_io):
        pass

    def hub_io_disconnected(self, hub_io):
        pass

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
        elif message_type == MessageType.HubProperties:
            return HubProperties.from_bytes(message[3:])
        else:
            logger.warning("Unexpected message type: %s %r", message_type, message)

    def services_resolved(self):
        logger.debug("Services resolved for %s", self.mac_address)
        super().services_resolved()

        for service in self.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid) == CHARACTERISTIC_UUID:

                    self.hub_characteristic = characteristic
                    self.hub_characteristic.enable_notifications()

                    self.send_message(
                        struct.pack(
                            "BBB",
                            MessageType.HubProperties,
                            HubProperty.BatteryVoltage,
                            HubPropertyOperation.EnableUpdates,
                        )
                    )
                    self.send_message(
                        struct.pack(
                            "BBB",
                            MessageType.HubProperties,
                            HubProperty.Button,
                            HubPropertyOperation.EnableUpdates,
                        )
                    )
                    return
        logger.debug("Device %s is not a LWP Hub", self.mac_address)
