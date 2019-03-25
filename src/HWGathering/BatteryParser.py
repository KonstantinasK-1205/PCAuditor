import os


class BatteryParser:

    def __init__(self, _path='/sys/class/power_supply/'):
        self.lastFunctionTime = ''

        self.path = _path
        self.batteries = {"Names": []}

    def get_battery_dict(self):
        return self.batteries

    def get_batteries(self):
        dirs = os.listdir(self.path)
        for _dir in dirs:
            if 'BAT' in _dir or 'CMB' in _dir:
                self.batteries["Names"].append(_dir)

    # Check this code segment, for unknown reasons, it took pretty long time to execute
    def update_battery(self):
        _path = self.path
        for _battery in self.batteries["Names"]:
            _dict = {"Name": _battery,
                     "Serial": self.get_serial(_path, _battery),
                     "Model": self.get_model(_path, _battery),
                     "Status": self.get_status(_path, _battery),
                     "Manufacturer": self.get_manufacturer(_path, _battery),
                     "Min Voltage": self.get_minimal_voltage(_path, _battery)}
            _dict["Current Use"] = self.get_current_use(_path, _battery, _dict["Min Voltage"])
            _dict["Current Wh"] = self.get_current_cap(_path, _battery, _dict["Min Voltage"])
            _dict["Maximum Wh"] = self.get_maximum_cap(_path, _battery, _dict["Min Voltage"])
            _dict["Factory Wh"] = self.get_factory_cap(_path, _battery, _dict["Min Voltage"])
            _dict["Wear Level"] = self.get_wearlevel(_dict["Factory Wh"], _dict["Maximum Wh"])
            _dict["Estimated"] = self.get_estimated_time(_dict["Wear Level"], _dict["Maximum Wh"])

            _dict["Current Use"] = str(_dict["Current Use"]) + " Wh"
            _dict["Current Wh"] = str(_dict["Current Wh"]) + " Wh"
            _dict["Maximum Wh"] = str(_dict["Maximum Wh"]) + " Wh"
            _dict["Factory Wh"] = str(_dict["Factory Wh"]) + " Wh"
            _dict["Wear Level"] = str(_dict["Wear Level"]) + " %"
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
                    _dict["Min Voltage"] = round(float(line.split('=')[1]) / 1000 / 1000, 2)
                elif '_CURRENT_NOW' in line:
                    _dict["Current Use"] = round(line.split('=')[1] * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_CHARGE_FULL_DESIGN' in line:
                    _dict["Factory Cap"] = round(line.split('=')[1] * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_CHARGE_FULL' in line:
                    _dict["Maximum Cap"] = round(line.split('=')[1] * (_dict["Min Voltage"] / 1000 / 1000), 2)
                elif '_CHARGE_NOW' in line:
                    _dict["Current Cap"] = round(line.split('=')[1] * (_dict["Min Voltage"] / 1000 / 1000), 2)
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
        _voltage = cls.read_file(_path, _battery, 'voltage_min_design')
        if _voltage and not _voltage == 0:
            _voltage = round(float(_voltage) / pow(1000, 2), 2)
        else:
            _voltage = 0
        return _voltage

    @classmethod
    def get_current_use(cls, _path, _battery, _voltage):
        _current = cls.read_file(_path, _battery, 'current_now')
        if _current and not _current == 0:
            _current = round(float(_current) / pow(1000, 2) * _voltage, 2)
        else:
            _current = 0
        return _current

    @classmethod
    def get_current_cap(cls, _path, _battery, _voltage):
        _current = cls.read_file(_path, _battery, 'charge_now')
        if _current and not _current == 0:
            _current = round(float(_current) / pow(1000, 2) * _voltage, 2)
        else:
            _current = 0
        return _current

    @classmethod
    def get_maximum_cap(cls, _path, _battery, _voltage):
        _maximum = cls.read_file(_path, _battery, 'charge_full')
        if _maximum and not _maximum == 0:
            _maximum = round(float(_maximum) / pow(1000, 2) * _voltage, 2)
        else:
            _maximum = 0
        return _maximum

    @classmethod
    def get_factory_cap(cls, _path, _battery, _voltage):
        _factory = cls.read_file(_path, _battery, 'charge_full_design')
        if _factory and not _factory == 0:
            _factory = round(float(_factory) / pow(1000, 2) * _voltage, 2)
        else:
            _factory = 0
        return _factory

    @staticmethod
    def get_wearlevel(_factory_capacity, _maximum_capacity):
        if _factory_capacity == 0: _factory_capacity = 1
        if _maximum_capacity == 0: _maximum_capacity = 1

        capacity = _maximum_capacity / _factory_capacity * 100
        wearlevel = round((100.00 - capacity), 2)
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
                try:
                    _temp = tmp.read().rstrip()
                except OSError:
                    _temp = ''
                return _temp


win = BatteryParser()
