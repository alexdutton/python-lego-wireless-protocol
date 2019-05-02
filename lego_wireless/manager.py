import gatt


class HubManager(gatt.DeviceManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_devices = set()
        self.trains = []

    def make_device(self, mac_address):
        return Hub(mac_address=mac_address, manager=self)

    def device_discovered(self, device: gatt.Device):
        if device.mac_address in self.seen_devices:
            return
        self.seen_devices.add(device.mac_address)
#        device.connect()
        print(device)
        print(device.services_resolved())
        #print(device.services)

    def hub_discovered(self, train):
        self.trains.append(train)
        print("Train discovered", train)
        train.connect()

    def run(self):
        self.start_discovery()
        super().run()
