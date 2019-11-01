import embr_survey.pygatt as gatt
import struct
from time import sleep
import logging

logging.basicConfig()
gatt_log = logging.getLogger('pygatt')


class EmbrVal(object):
    # enum-like class
    # Some of these are read only/write only, and we don't
    # currently enforce any of that
    FIRMWARE_VERSION = ('4001', '<I')  # uint32_t
    DEVICE_ID = ('4002', '<HI')  # uint32_t?? But it sends 6 bytes...
    BEACON = ('4003', '<?')  # bool (write only)
    LEVEL = ('4005', '<b')  # int8_t
    STATE = ('4006', '<B')  # uint8_t
    MANAGEMENT_MODE = ('4007', '<?')
    STOP = ('4008', '<I')  # only useful if writing [0x00, 0x00, 0x00, 0x20]?
    LED_DISABLE = ('4009', '<B')
    BATTERY_CHARGE = ('400A', '<B')
    MODE = ('400B', '<II')  # MODE/DURATION are a little more complicated (depends on mode)
    DURATION = ('400C', '<I')  # TODO: not quite correct name?
    # DFU = '400D' # not implementing in this interface
    COOL_WARM_ONLY = ('400E', '<B')


# generally 800ms between commands
try:
    gatt_ble = gatt.BGAPIBackend()
    gatt_ble.start()
except gatt.exceptions.NotConnectedError:
    gatt_ble = None


class PreEmbr(object):
    # non-bonding version
    def __init__(self):
        self.adapter = gatt_ble
        self.scan()

    def scan(self):
        devs = self.adapter.scan()
        self.addrs = [d['address'] for d in devs if d['name'] == 'EmbrWave']

    def blink(self, addr):
        dev = self.adapter.connect(address=addr, timeout=5,
                                   address_type='BLEAddressType.public',
                                   interval_min=15, interval_max=30,
                                   supervision_timeout=400, latency=0)
        for i in range(3):
            self._blink(dev)
        dev.disconnect()

    def _blink(self, dev):
        dev.char_write('00004003-1112-efde-1523-725a2aab0123', bytearray(b'\x01'))


class DummyPreEmbr(object):
    def __init__(self):
        self.scan()

    def scan(self):
        self.addrs = ['None (no BLE adapter)']

    def blink(self, addr):
        pass

# Callback for receiving battery level number from device
def handle_battery(handle, value):
    battery = struct.unpack('<B',value)[0]
    print("******Battery: %s" % battery)

def handle_device_state(handle, value):
    device_state = struct.unpack('<B',value)[0]
    print("******State: %s" % device_state)

class EmbrWave(object):
    def __init__(self, addr=None):
        # I don't think using atexit w/ the context manager is *completely* redundant,
        # and this keeps us from getting superfluous errors on normal exit
        self.on = True
        self.name = 'EmbrWave'
        self.adapter = gatt_ble

        if not addr:
            devs = self.adapter.scan()
            addr = next(d['address'] for d in devs if d['name'] == 'EmbrWave')
        self.addr = addr
        self.device = self.adapter.connect(address=addr, timeout=5,
                                           address_type='BLEAddressType.public',
                                           interval_min=15, interval_max=30,
                                           supervision_timeout=400, latency=0)
        try:
            self.blink()
            self.blink()
            self.device.bond()
            self.disable_leds()  # for debugging, comment this out
            sleep(1)
            self.device.subscribe("0000400A-1112-efde-1523-725a2aab0123", callback = handle_battery)
            sleep(1)
            self.device.subscribe("00004006-1112-efde-1523-725a2aab0123", callback = handle_device_state)
            sleep(1)
            # set warming/cooling to be rather long (we'll end up turning them off manually)
            self.write(EmbrVal.COOL_WARM_ONLY, 0)
            for val in [6, 7]:  # heating, cooling respectively
                # Blah, this takes awhile?
                # pass
                self.write(EmbrVal.MODE, (val, 1))  # indicate we want to change duration
                self.write(EmbrVal.DURATION, 129)  # extended mode
                #self.write(EmbrVal.DURATION, 60) # custom duration (60s)
                # self.write(EmbrVal.MODE, (val, 2))  # within custom mode, can change the ramp rate
            # self.write(EmbrVal.DURATION, 1)  # ramp up at 1C/s
        except Exception as e:
            self.device.disconnect()
            raise e

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        # called at the end of the task
        if self.on:
            self.on = False
            self.stop()
            self.write(EmbrVal.MODE, (6, 1))
            self.write(EmbrVal.DURATION, 131)  # set back to "standard" mode
            self.write(EmbrVal.MODE, (7, 1))
            self.write(EmbrVal.DURATION, 131)
            self.enable_leds()
            self.device.disconnect()
            self.adapter.stop()

    def write(self, uuid, value):
        # converts to bytes, *then* write for real
        try:  # convert non-iterables to iterables
            x = iter(value)
        except TypeError:
            value = [value]
        new_val = struct.pack(uuid[1], *value)
        self._write(uuid, new_val)
        sleep(2)  # TODO: check if this should be longer/shorter

    def _write(self, uuid, value):
        self.device.char_write('0000%s-1112-efde-1523-725a2aab0123' % uuid[0], bytearray(value))

    def read(self, uuid):
        res = self.device.char_read('0000%s-1112-efde-1523-725a2aab0123' % uuid[0])
        sleep(0.2)  # TODO: check if this should be longer/shorter
        return struct.unpack(uuid[1], res)[0]

    @property
    def level(self):
        return self.read(EmbrVal.LEVEL)

    @level.setter
    def level(self, value):
        self.blink()
        sleep(1)
        self.stop()
        sleep(1)
        self.write(EmbrVal.LEVEL, value)

    @property
    def battery_charge(self):
        return self.read(EmbrVal.BATTERY_CHARGE)

    @property
    def firmware_version(self):
        return self.read(EmbrVal.FIRMWARE_VERSION)

    @property
    def device_id(self):
        return self.read(EmbrVal.DEVICE_ID)

    def blink(self):
        self._write(EmbrVal.BEACON, [0x01])

    def stop(self):
        self._write(EmbrVal.STOP, [0x00, 0x00, 0x00, 0x20])

    def disable_leds(self):
        # turn off all LEDs
        self._write(EmbrVal.LED_DISABLE, [0x01])

    def enable_leds(self):
        self._write(EmbrVal.LED_DISABLE, [0x00])

    @property
    def state(self):
        # ends up being less than useful (unless I was using it wrong)
        # 1 if currently heating/cooling (even once it has peaked)
        # 0 if stopped
        return self.read(EmbrVal.STATE)


class DummyWave(object):
    def __init__(self):
        self.name = 'DummyWave'
        self.level = -1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def close(self):
        pass

    def write(self, uuid, value):
        pass

    def read(self, uuid):
        return -1

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value

    @property
    def battery_charge(self):
        return -1

    @property
    def firmware_version(self):
        return -1

    @property
    def device_id(self):
        return -1

    def blink(self):
        pass

    def stop(self):
        pass

    def enable_leds(self):
        pass

    def disable_leds(self):
        pass

    @property
    def state(self):
        return -1


if __name__ == '__main__':
    # device already needs to be in pairing mode!
    try:
        embr = EmbrWave()  # TODO: explicitly pass in address?
    except Exception as e:
        embr = DummyWave()

    with embr:
        print(embr.device_id)
        print(embr.firmware_version)
        print(embr.battery_charge)
        for i in range(2):
            embr.blink()
        sleep(2)
        embr.level = 7
        sleep(60)
        # print(embr.level)
        #embr.level = -9
        # print('bump')
        #embr.level = -9
        # print('bump')
        # sleep(5)
        #print('now warming')
        #embr.level = 9
        # sleep(60)
        print(embr.level)
