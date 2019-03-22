import os


class BatteryParser:

    def __init__(self, _path='/sys/class/power_supply/'):
        self.lastFunctionTime = ''

        self.path = _path
        self.batteries = dict()
        self.batteries["Names"] = []

    def get_battery_dict(self):
        return self.batteries

    def get_batteries(self):
        dirs = os.listdir(self.path)
        for _dir in dirs:
            if 'BAT' in _dir or 'CMB' in _dir:
                self.batteries["Names"].append(_dir)

    # Check this code segment, for unknown reasons, it took pretty long time to execute
    def update_battery(self):
        for _battery in self.batteries["Names"]:
            _dict = {}
            _dict["Name"] = _battery
            _dict["Serial"] = self.get_serial(self.path, _battery)
            _dict["Model"] = self.get_model(self.path, _battery)
            _dict["Status"] = self.get_status(self.path, _battery)
            _dict["Manufacturer"] = self.get_manufacturer(self.path, _battery)
            _dict["Min Voltage"] = round(float(self.get_minimal_voltage(self.path, _battery)) / 1000 / 1000 / 1000, 4)
            _dict["Current Use"] = str(
                round((float(self.get_current_use(self.path, _battery)) / 1000) * _dict["Min Voltage"], 2)) + " Wh"
            _dict["Current Wh"] = str(
                round((float(self.get_current_cap(self.path, _battery)) / 1000) * _dict["Min Voltage"], 2)) + " Wh"
            _dict["Maximum Wh"] = str(
                round((float(self.get_maximum_cap(self.path, _battery)) / 1000) * _dict["Min Voltage"], 2)) + " Wh"
            _dict["Factory Wh"] = str(
                round((float(self.get_factory_cap(self.path, _battery)) / 1000) * _dict["Min Voltage"], 2)) + " Wh"
            _dict["Wear Level"] = str(
                round(float(self.get_wearlevel(_dict["Factory Wh"].split(' ')[0], _dict["Maximum Wh"].split(' ')[0])),
                      2)) + " %"
            _dict["Estimated"] = self.get_estimated_time(float(_dict["Wear Level"].split(' ')[0]),
                                                         _dict["Maximum Wh"].split(' ')[0])
            self.batteries[_battery] = _dict

    def init_battery_uevent(self, _dict, _path):
        for _battery in range(0, _dict["Amount"]):
            _uevent = self.read_file(_path, _battery, 'uevent')
            for line in _uevent.splitlines():
                if '_NAME' in line:
                    _dict["Name"] = "BAT" + str(_battery)
                elif '_STATUS' in line:
                    _dict["Status"] = self.get_status(_path, _battery)
                elif '_VOLTAGE_MIN_DESIGN' in line:
                    _dict["Min Voltage"] = round(float(10800000) / 1000 / 1000, 2)
                elif '_CURRENT_NOW' in line:
                    _dict["Current Use"] = round(3115000 * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_CHARGE_FULL_DESIGN' in line:
                    _dict["Factory Cap"] = round(3665000 * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_CHARGE_FULL' in line:
                    _dict["Maximum Cap"] = round(3665000 * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_CHARGE_NOW' in line:
                    _dict["Current Cap"] = round(623000 * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_MODEL_NAME' in line:
                    _dict["Model"] = line.split('=')[1]
                elif '_MANUFACTURER' in line:
                    _dict["Manufacturer"] = line.split('=')[1]
                elif '_SERIAL' in line:
                    _dict["Serial"] = line.split('=')[1]
            _dict["Wear level"] = round(float(self.get_wearlevel(_dict["Factory Cap"], _dict["Maximum Cap"])), 2)
            _dict["Estimated"] = self.get_estimated_time(_dict["Wear level"], _dict["Maximum Cap"])

    @classmethod
    def get_serial(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'serial_number')

    @classmethod
    def get_model(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'model_name')

    @classmethod
    def get_manufacturer(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'manufacturer')

    @classmethod
    def get_status(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'status')

    @classmethod
    def get_minimal_voltage(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'voltage_min_design')

    @classmethod
    def get_current_use(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'current_now')

    @classmethod
    def get_current_cap(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'charge_now')

    @classmethod
    def get_maximum_cap(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'charge_full')

    @classmethod
    def get_factory_cap(cls, _path, _battery):
        return cls.read_file(_path, _battery, 'charge_full_design')

    @staticmethod
    def get_wearlevel(_factory_capacity, _maximum_capacity):
        capacity = (float(_maximum_capacity) / float(_factory_capacity)) * 100
        wearlevel = format((100.00 - capacity), '.2f')
        return wearlevel

    @staticmethod
    def get_estimated_time(_wearlevel, _maximum_capacity):
        if _wearlevel == 0 and _maximum_capacity == 0:
            _estimated = "Battery may be broken or unsupported"
        elif _wearlevel < 35:
            _estimated = "Approx. 1 h."
        elif _wearlevel < 60:
            _estimated = "Approx. 40 min."
        elif _wearlevel <= 90:
            _estimated = "Approx. 30 min."
        elif _wearlevel > 90:
            _estimated = "Does not hold charge."
        else:
            _estimated = "Cannot determine expected time."
        return _estimated

    @staticmethod
    def read_file(_path, _battery, _file):
        _file_location = _path + _battery + '/' + _file
        if os.path.exists(_file_location):
            with open(_file_location, 'r') as tmp:
                return tmp.read().rstrip()


win = BatteryParser()
