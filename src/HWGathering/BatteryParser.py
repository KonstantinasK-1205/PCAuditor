import os


class BatteryParser:

    def __init__(self, _path='/sys/class/power_supply/'):
        self.lastFunctionTime = 0
        self.path = _path
        self.batteries = {"Names": []}
        self.bat_attributes = {"Min Voltage": ["voltage_min_design", ""],
                               "Current Use": ["current_now", "power_now"],
                               "Current Cap": ["charge_now", "energy_now"],
                               "Maximum Cap": ["charge_full", "energy_full"],
                               "Factory Cap": ["charge_full_design", "energy_full_design"]}

    def get_battery_dict(self):
        return self.batteries

    def get_batteries(self):
        for _dir in os.listdir(self.path):
            if 'BAT' in _dir or 'CMB' in _dir:
                self.batteries["Names"].append(_dir)

    def update_battery(self):
        for _battery in self.batteries["Names"]:
            bat_path = self.path + _battery + '/'
            bat_dict = {"Name": _battery,
                        "Serial": self.read_file(bat_path, 'serial_number'),
                        "Model": self.read_file(bat_path, 'model_name'),
                        "Status": self.read_file(bat_path, 'manufacturer'),
                        "Manufacturer": self.read_file(bat_path, 'status'),
                        "Min Voltage": self.establish_value(bat_path, None, "Min Voltage")}
            bat_dict["Current Use"] = self.establish_value(bat_path, bat_dict["Min Voltage"], "Current Use")
            bat_dict["Current Wh"] = self.establish_value(bat_path, bat_dict["Min Voltage"], "Current Cap")
            bat_dict["Maximum Wh"] = self.establish_value(bat_path, bat_dict["Min Voltage"], "Maximum Cap")
            bat_dict["Factory Wh"] = self.establish_value(bat_path, bat_dict["Min Voltage"], "Factory Cap")

            # Loading battery backup information from uevent
            bat_uevent = self.init_battery_uevent(bat_path, bat_dict["Min Voltage"])
            for _key in bat_dict.keys():
                if _key in bat_uevent and (not bat_dict[_key] or bat_dict[_key] == 0.0):
                    bat_dict[_key] = bat_uevent[_key]

            # Small Check, because some batteries has inverted Max Design Wh and Current Max Wh
            if bat_dict["Maximum Wh"] > bat_dict["Factory Wh"]:
                bat_dict["Factory Wh"], bat_dict["Maximum Wh"] = bat_dict["Maximum Wh"], bat_dict["Factory Wh"]

            # Calculate wear level and estimated time
            bat_dict["Wear Level"] = self.get_wearlevel(bat_dict["Factory Wh"], bat_dict["Maximum Wh"])
            bat_dict["Estimated"] = self.get_estimated_time(bat_dict["Wear Level"], bat_dict["Maximum Wh"])

            # Format values to have correspondent suffix and push to dict
            bat_dict["Current Use"] = str(bat_dict["Current Use"]) + " Wh"
            bat_dict["Current Wh"] = str(bat_dict["Current Wh"]) + " Wh"
            bat_dict["Maximum Wh"] = str(bat_dict["Maximum Wh"]) + " Wh"
            bat_dict["Factory Wh"] = str(bat_dict["Factory Wh"]) + " Wh"
            bat_dict["Wear Level"] = str(bat_dict["Wear Level"]) + "%"
            self.batteries.update({_battery: bat_dict})

    def init_battery_uevent(self, _path, _voltage):
        bat_dict = {}
        for line in self.read_file(_path, 'uevent').splitlines():
            value = line.split('=')[1]
            if '_SERIAL' in line:
                bat_dict["Serial"] = value
            elif '_MANUFACTURER' in line:
                bat_dict["Manufacturer"] = value
            elif '_MODEL_NAME' in line:
                bat_dict["Model"] = value
            elif '_STATUS' in line:
                bat_dict["Status"] = value
            elif '_VOLTAGE_MIN_DESIGN' in line:
                if not _voltage or _voltage == 0.0:
                    _voltage = round(float(value) / 1000 / 1000, 2)
                    if _voltage == 0.0: _voltage = 1
                bat_dict["Min Voltage"] = _voltage
            elif '_CURRENT_NOW' in line or '_POWER_NOW' in line:
                bat_dict["Current Use"] = self.value_converter(value, _voltage)
            elif '_CHARGE_FULL_DESIGN' in line or '_ENERGY_FULL_DESIGN' in line:
                bat_dict["Factory Wh"] = self.value_converter(value, _voltage)
            elif '_CHARGE_FULL' in line or '_ENERGY_FULL' in line:
                bat_dict["Maximum Wh"] = self.value_converter(value, _voltage)
            elif '_CHARGE_NOW' in line or '_ENERGY_NOW' in line:
                bat_dict["Current Wh"] = self.value_converter(value, _voltage)
            return bat_dict

    def establish_value(self, _path, _voltage, _attribute):
        attributes = self.bat_attributes
        if _attribute in attributes:
            attribute = attributes[_attribute]
            value = self.read_file(_path, attribute[0])
            if not value: value = self.read_file(_path, attribute[1])

            if value and not value == 0:
                value = self.value_converter(value, _voltage)
            else:
                value = 0.0
            return value

    @staticmethod
    def get_wearlevel(_factory_capacity, _maximum_capacity):
        if _factory_capacity == 0: _factory_capacity = 1
        if _maximum_capacity == 0: _maximum_capacity = 1

        capacity = _maximum_capacity / _factory_capacity * 100
        wearlevel = round((100.00 - capacity) * 2) / 2
        return wearlevel

    @staticmethod
    def get_estimated_time(_wearlevel, _maximum_capacity):
        if _wearlevel < 0 or _wearlevel == 0 and _maximum_capacity == 0:
            estimated = "Battery may be broken or unsupported"
        elif _wearlevel < 35:
            estimated = "Approx. 1 h."
        elif _wearlevel < 60:
            estimated = "Approx. 40 min."
        elif _wearlevel < 80:
            estimated = "Approx. 30 min."
        elif _wearlevel <= 90:
            estimated = "Approx. 15 min."
        elif _wearlevel > 90:
            estimated = "Does not hold charge."
        else:
            estimated = "Cannot determinate expected time."
        return estimated

    @staticmethod
    def value_converter(_value, _voltage):
        if len(_value) < 8 and _voltage:
            local_val = round((float(_value) * (float(_voltage) / 1000 / 1000)) * 2) / 2
        else:
            local_val = round((float(_value) / 1000 / 1000) * 2) / 2
        return local_val

    @staticmethod
    def read_file(_path, _file):
        file_location = _path + _file
        if os.path.exists(file_location):
            with open(file_location, 'r') as tmp:
                try:
                    content = tmp.read()
                    if content: content = content.rstrip().lstrip()
                except OSError:
                    content = ''
        else:
            content = None
        return content


BatteryParser()
