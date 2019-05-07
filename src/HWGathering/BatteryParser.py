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

    # Check this code segment, for unknown reasons,
    # it took pretty long time to execute
    def update_battery(self):
        path = self.path
        for _battery in self.batteries["Names"]:
            bat_dict = {"Name": _battery,
                        "Serial": self.get_serial(path, _battery),
                        "Model": self.get_model(path, _battery),
                        "Status": self.get_status(path, _battery),
                        "Manufacturer": self.get_manufacturer(path, _battery),
                        "Min Voltage": self.get_minimal_voltage(path, _battery)}
            bat_dict["Current Use"] = self.get_current_use(path, _battery, bat_dict["Min Voltage"])
            bat_dict["Current Wh"] = self.get_current_cap(path, _battery, bat_dict["Min Voltage"])
            bat_dict["Maximum Wh"] = self.get_maximum_cap(path, _battery, bat_dict["Min Voltage"])
            bat_dict["Factory Wh"] = self.get_factory_cap(path, _battery, bat_dict["Min Voltage"])
            bat_dict["Wear Level"] = self.get_wearlevel(bat_dict["Factory Wh"], bat_dict["Maximum Wh"])
            bat_dict["Estimated"] = self.get_estimated_time(bat_dict["Wear Level"], bat_dict["Maximum Wh"])

            bat_dict["Current Use"] = str(bat_dict["Current Use"]) + " Wh"
            bat_dict["Current Wh"] = str(bat_dict["Current Wh"]) + " Wh"
            bat_dict["Maximum Wh"] = str(bat_dict["Maximum Wh"]) + " Wh"
            bat_dict["Factory Wh"] = str(bat_dict["Factory Wh"]) + " Wh"
            bat_dict["Wear Level"] = str(bat_dict["Wear Level"]) + "%"

            # Loading battery backup information from uevent
            bat_bckp = self.init_battery_uevent(path, _battery)
            if not bat_dict["Serial"]:
                bat_dict["Serial"] = bat_bckp["Serial"]
            if not bat_dict["Model"]:
                bat_dict["Model"] = bat_bckp["Model"]
            if not bat_dict["Status"]:
                bat_dict["Status"] = bat_bckp["Status"]
            if not bat_dict["Manufacturer"]:
                bat_dict["Manufacturer"] = bat_bckp["Manufacturer"]
            if not bat_dict["Min Voltage"]:
                bat_dict["Min Voltage"] = bat_bckp["Min Voltage"]
            if not bat_dict["Current Use"]:
                bat_dict["Current Use"] = bat_bckp["Current Use"]
            if not bat_dict["Current Wh"]:
                bat_dict["Current Wh"] = bat_bckp["Current Wh"]
            if not bat_dict["Maximum Wh"]:
                bat_dict["Maximum Wh"] = bat_bckp["Maximum Wh"]
            if not bat_dict["Factory Wh"]:
                bat_dict["Factory Wh"] = bat_bckp["Factory Wh"]
            if not bat_dict["Wear Level"]:
                bat_dict["Wear Level"] = bat_bckp["Wear Level"]
            if not bat_dict["Estimated"]:
                bat_dict["Estimated"] = bat_bckp["Estimated"]

            self.batteries.update({_battery: bat_dict})

    # TODO: Review and launch function below
    #   Function should act as backup in case
    #   power_supply/* files couldn't be readed
    def init_battery_uevent(self, _path, _battery):
        bat_dict = {}
        _uevent = self.read_file(_path, _battery, 'uevent')
        for line in _uevent.splitlines():
            if '_STATUS' in line:
                bat_dict["Status"] = self.get_status(_path, _battery)
            elif '_VOLTAGE_MIN_DESIGN' in line:
                bat_dict["Min Voltage"] = round(float(line.split('=')[1]) / 1000 / 1000, 2)
            elif '_CURRENT_NOW' in line:
                bat_dict["Current Wh"] = round(float(line.split('=')[1]) * (bat_dict["Min Voltage"] / 1000 / 1000), 2)
            elif '_CHARGE_FULL_DESIGN' in line:
                bat_dict["Factory Wh"] = round(float(line.split('=')[1]) * (bat_dict["Min Voltage"] / 1000 / 1000), 2)
            elif '_CHARGE_FULL' in line:
                bat_dict["Maximum Wh"] = round(float(line.split('=')[1]) * (bat_dict["Min Voltage"] / 1000 / 1000), 2)
            elif '_CHARGE_NOW' in line:
                bat_dict["Current Wh"] = round(float(line.split('=')[1]) * (bat_dict["Min Voltage"] / 1000 / 1000), 2)
            elif '_MODEL_NAME' in line:
                bat_dict["Model"] = line.split('=')[1]
            elif '_MANUFACTURER' in line:
                bat_dict["Manufacturer"] = line.split('=')[1]
            elif '_SERIAL' in line:
                bat_dict["Serial"] = line.split('=')[1]
        bat_dict["Wear Level"] = round(float(self.get_wearlevel(bat_dict["Factory Wh"], bat_dict["Maximum Wh"])), 2)
        bat_dict["Estimated"] = self.get_estimated_time(bat_dict["Wear Level"], bat_dict["Maximum Wh"])
        return bat_dict

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
        min_voltage = cls.read_file(_path, _battery, 'voltage_min_design')
        if min_voltage and not min_voltage == 0:
            min_voltage = round(float(min_voltage) / pow(1000, 2), 2)
        else:
            min_voltage = 0
        return min_voltage

    @classmethod
    def get_current_use(cls, _path, _battery, _voltage):
        current_use = cls.read_file(_path, _battery, 'current_now')
        if current_use and not current_use == 0:
            current_use = round(float(current_use) / pow(1000, 2) * _voltage, 2)
        else:
            current_use = 0
        return current_use

    @classmethod
    def get_current_cap(cls, _path, _battery, _voltage):
        current_cap = cls.read_file(_path, _battery, 'charge_now')
        if current_cap and not current_cap == 0:
            current_cap = round(float(current_cap) / pow(1000, 2) * _voltage, 2)
        else:
            current_cap = 0
        return current_cap

    @classmethod
    def get_maximum_cap(cls, _path, _battery, _voltage):
        maximum = cls.read_file(_path, _battery, 'charge_full')
        if maximum and not maximum == 0:
            maximum = round(float(maximum) / pow(1000, 2) * _voltage, 2)
        else:
            maximum = 0
        return maximum

    @classmethod
    def get_factory_cap(cls, _path, _battery, _voltage):
        factory = cls.read_file(_path, _battery, 'charge_full_design')
        if factory and not factory == 0:
            factory = round(float(factory) / pow(1000, 2) * _voltage, 2)
        else:
            factory = 0
        return factory

    @staticmethod
    def get_wearlevel(_factory_capacity, _maximum_capacity):
        if _factory_capacity == 0:
            _factory_capacity = 1
        if _maximum_capacity == 0:
            _maximum_capacity = 1

        capacity = _maximum_capacity / _factory_capacity * 100
        wearlevel = round((100.00 - capacity), 2)
        return wearlevel

    @staticmethod
    def get_estimated_time(_wearlevel, _maximum_capacity):
        if _wearlevel == 0 and _maximum_capacity == 0:
            estimated = "Battery may be broken or unsupported"
        elif _wearlevel < 35:
            estimated = "Approx. 1 h."
        elif _wearlevel < 60:
            estimated = "Approx. 40 min."
        elif _wearlevel <= 90:
            estimated = "Approx. 30 min."
        elif _wearlevel > 90:
            estimated = "Does not hold charge."
        else:
            estimated = "Cannot determinate expected time."
        return estimated

    @staticmethod
    def read_file(_path, _battery, _file):
        file_location = _path + _battery + '/' + _file
        if os.path.exists(file_location):
            with open(file_location, 'r') as tmp:
                try:
                    content = tmp.read()
                    if content:
                        content = content.rstrip()
                except OSError:
                    content = ''
                return content


win = BatteryParser()
