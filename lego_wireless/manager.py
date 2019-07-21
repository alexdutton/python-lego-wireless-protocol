import gatt

from .constants import SERVICE_UUID
from .hub import Hub
from . import signals


class HubManager(gatt.DeviceManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hubs = set()

    def make_device(self, mac_address):
        return Hub(mac_address=mac_address, manager=self)

    def device_discovered(self, device: gatt.Device):
        super().device_discovered(device)
        if SERVICE_UUID in map(
            str, device._properties.Get("org.bluez.Device1", "UUIDs")
        ):
            signals.hub_discovered.send(self, hub=device)

    def start_discovery(self):
        return super().start_discovery([SERVICE_UUID])

    def stop(self):
        for hub in self.hubs:
            hub.disconnect()
        super().stop()
