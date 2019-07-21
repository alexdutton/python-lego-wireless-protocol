import atexit
import logging
import threading

from lego_wireless.hub_io import TrainMotor, LEDLight
from .manager import HubManager
from . import signals

hubs_seen = set()


def hub_discovered(sender, hub):
    if hub not in hubs_seen:
        hubs_seen.add(hub)
        print("Connecting Hub IO, %s", hub.mac_address)
        signals.hub_io_connected.connect(hub_io_connected, sender=hub)
        hub.connect()


def hub_io_connected(sender, hub_io):
    print("Let's go!")
    if isinstance(hub_io, TrainMotor):
        hub_io.set_speed(100)
    if isinstance(hub_io, LEDLight):
        hub_io.set_brightness(100)


def main():
    hub_manager = HubManager("hci0")
    atexit.register(hub_manager.stop)

    signals.hub_discovered.connect(hub_discovered, sender=hub_manager)

    hub_manager_thread = threading.Thread(target=hub_manager.run)
    hub_manager_thread.start()
    hub_manager.start_discovery()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
