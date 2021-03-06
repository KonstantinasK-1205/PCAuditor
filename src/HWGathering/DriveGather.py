import re
import subprocess


class DiskChecker:
    def __init__(self):
        self.lsblk_output = eval(self.get_init_info())
        self.drives = dict()
        self.drives['Drives'] = dict()
        self.drives['Devices'] = dict()
        self.is_cdrom_present = False

        self.drive_no = 0
        self.cdrom_no = 0

    # Master information - Loads all blocks
    @staticmethod
    def get_init_info(_timeout=60):
        try:
            info = subprocess.check_output(
                'lsblk -J -o PATH,SERIAL,MODEL,LABEL,TRAN,SIZE | grep -vE "PCAuditor|usb" | grep -vE "sd.[0-9]+|mmcblk[0-9](boot|p)[0-9]|nvme[0-9](boot|p)[0-9]|loop[0-9]"',
                shell=True, bufsize=4096, timeout=_timeout).decode('utf-8', errors='ignore')
            info = info.replace('null', '"null"')
        except subprocess.TimeoutExpired:
            info = None
        return info

    # Master information - Gathering function
    @staticmethod
    def get_main_information(_command, _block=None, _timeout=60):
        # Loads information gathered from _command
        if _command == 'sentinel':
            _command = "/usr/bin/sentinel -dev " + _block + " -dump"
        elif _command == 'hdparm':
            _command = "hdparm -I " + _block
        elif _command == 'smartctl':
            _command = "smartctl -i " + _block
        try:
            info = subprocess.check_output(_command, shell=True, bufsize=4096,
                                           timeout=_timeout).decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired or subprocess.CalledProcessError:
            info = None
        return info

    @staticmethod
    def grab_information(_source, _pattern, _default_value='', _flags=None):
        try:
            if not _flags:
                info = re.search(_pattern, _source)
            else:
                info = re.search(_pattern, _source, flags=re.MULTILINE)

            if info:
                info = info.group(1).lstrip().replace('\n', ' ').rstrip()
                if _flags:
                    info = re.sub(' +', ' ', info)
            else:
                info = _default_value
        except TypeError:
            info = _default_value
        return info

    @staticmethod
    def convert_size_to_bytes(_number, _si=None):
        lowercase_si = _si.lower()
        _number = int(_number.split()[0])
        if lowercase_si == "pb" or lowercase_si == "p":
            _number = _number * (1024 ** 5)
        elif lowercase_si == "tb" or lowercase_si == "t":
            _number = _number * (1024 ** 4)
        elif lowercase_si == "gb" or lowercase_si == "g":
            _number = _number * (1024 ** 3)
        elif lowercase_si == "mb" or lowercase_si == "m":
            _number = _number * (1024 ** 2)
        elif lowercase_si == "kb" or lowercase_si == "k":
            _number = _number * (1024 ** 1)
        elif lowercase_si == "b":
            _number = _number
        return _number

    @staticmethod
    def convert_size_to_gb(_number):
        return str(int(_number) / (1000 ** 3)).split('.')[0] + " GB"

    def get_disk_drives(self):
        if not self.lsblk_output:
            self.lsblk_output = eval(self.get_init_info())

        self.drives = dict()
        self.drives['Drives'] = dict()
        self.drives['Devices'] = dict()
        self.drive_no = 0
        self.cdrom_no = 0

        for _device in self.lsblk_output["blockdevices"]:
            block = _device["path"]
            serial = _device["serial"]
            if _device['model'] == "null":
                _device['model'] = "Unknown"

            info = dict()
            if 'sd' in block or 'mmcblk' in block or 'nvme' in block:
                self.drive_no += 1
                keyword = str(self.drive_no) + ' Drive'
                info[keyword] = {}
                info[keyword]["Serial"] = serial
                info[keyword]["Block"] = block

                if 'sd' in block:
                    sentinel = self.get_main_information('sentinel', block)
                    hdparm = self.get_main_information('hdparm', block)
                    self.get_disk_info(info[keyword], sentinel, hdparm, None)

                elif 'mmcblk' in block:
                    info[keyword]["Manufacturer"] = "Unknown"
                    info[keyword]["Model"] = _device["model"]
                    info[keyword]["Capacity"] = _device["size"]
                    info[keyword]["Interface"] = "eMMC/MMC"
                    info[keyword]["FFactor"] = "eMMC/MMC"
                    info[keyword]["Type"] = 'SSD'
                    info[keyword]["Rotation Speed"] = '-1'
                    info[keyword]["Health"] = "-1"
                    info[keyword]["Description"] = ""

                elif 'nvme' in block:
                    info[keyword]["Manufacturer"] = "WIP"
                    info[keyword]["Model"] = _device["model"]
                    info[keyword]["Capacity"] = _device["size"]
                    info[keyword]["Interface"] = 'NVMe'
                    info[keyword]["FFactor"] = 'NVMe'
                    info[keyword]["Type"] = 'SSD'
                    info[keyword]["Rotation Speed"] = '-1'
                    info[keyword]["Health"] = "WIP"
                    info[keyword]["Description"] = "WIP"
                self.drives['Drives'].update(info)

            elif 'sr' in block:
                self.cdrom_no += 1
                keyword = str(self.cdrom_no) + ' Device'
                info[keyword] = {}
                info[keyword]["Serial"] = serial
                info[keyword]["Block"] = block
                self.is_cdrom_present = True

                if not _device["label"] == 'null':
                    is_empty = False
                else:
                    is_empty = True

                info[keyword]["Empty"] = is_empty
                info[keyword]["Model"] = _device["model"]
                self.drives['Devices'].update(info)
        self.drives['Drives']["Amount"] = self.drive_no
        self.drives['Devices']["Amount"] = self.cdrom_no
        self.lsblk_output = None
        return self.drives

    def get_disk_info(self, _info, _sentinel, _hdparm=None, _smartctl=None):
        # Drive Identification
        _info["Manufacturer"] = self.grab_information(_sentinel, "Manufacturer.*: (.*)")
        if 'Hitachi' in _info["Manufacturer"]:
            _info["Manufacturer"] = "Hitachi"

        _info["Family"] = self.grab_information(_sentinel, "Disk Family.*: (.*)")
        _info["Model"] = self.grab_information(_sentinel, "Hard Disk Model ID.*: (.*)")
        if 'mSATA' in _info["Model"]:
            _info["Model"] = _info["Model"].replace("mSATA ", '')
            _info["Type"] = "SSD"
            _info["Interface"] = "mSATA"
            _info["Rotation Speed"] = "-1"
        if 'SSD' in _info["Model"]:
            _info["Model"] = _info["Model"].replace("SSD ", '')
        if 'HGST' in _info["Model"]:
            _info["Model"] = _info["Model"].replace("HGST ", '')

        if 'LITEONIT' in _info["Model"]:
            _info["Model"] = _info["Model"].replace('LITEONIT ', '')
            if not _info["Manufacturer"]:
                _info["Manufacturer"] = 'LITEONIT'

        if 'SAMSUNG' in _info["Model"].upper():
            _info["Model"] = _info["Model"].replace('SAMSUNG ', '')
            if not _info["Manufacturer"]:
                _info["Manufacturer"] = 'Samsung'

        capacity = self.grab_information(_sentinel, "Unformatted Capacity.*: (.*)")
        si = 'mb'
        if not capacity:
            capacity = self.grab_information(_smartctl, "User Capacity: +(.* (?=bytes))").replace(',', '')
            si = 'b'

        if capacity:
            capacity = capacity.replace(',', '')
            _info["Capacity"] = self.convert_size_to_gb(self.convert_size_to_bytes(capacity, si))
        else:
            _info["Capacity"] = 'Unknown'

        #
        _info["Locked"] = self.grab_information(_sentinel, "Security Locked.* (.*)", 'Unknown')

        #
        rpm = self.grab_information(_sentinel, "Nominal Media Rotation Rate.*: (.*)")
        if not rpm:
            rpm = self.grab_information(_sentinel, "Rotational Speed.*: (.*)")
            if not rpm:
                rpm = self.grab_information(_smartctl, "Rotation Rate: +(.*)")

        if rpm:
            if 'ssd' in rpm.lower() or 'solid' in rpm.lower():
                if not _info.get("Type", ''): _info["Type"] = "SSD"
                if not _info.get("Rotation Speed", ''): _info["Rotation Speed"] = "-1"
            elif 'rpm' in rpm.lower():
                if not _info.get("Type", ''): _info["Type"] = "HDD"
                if not _info.get("Rotation Speed", ''): _info["Rotation Speed"] = rpm.replace(" RPM", '')
            else:
                if not _info.get("Type", ''): _info["Type"] = "Unknown"
                if not _info.get("Rotation Speed", ''): _info["Rotation Speed"] = "-1"
        else:
            if not _info.get("Type", ''): _info["Type"] = "Unknown"
            if not _info.get("Rotation Speed", ''): _info["Rotation Speed"] = "-1"

        #
        _info["FFactor"] = self.grab_information(_sentinel, "Form Factor.*: (.* (?=inch))")
        if not _info["FFactor"]:
            _info["FFactor"] = self.grab_information(_sentinel, "Form Factor.*: (.*)\"")
            if not _info["FFactor"]:
                _info["FFactor"] = self.grab_information(_smartctl, "Form Factor: +(.*(?=inches))")
                if not _info["FFactor"]:
                    _info["FFactor"] = "Unknown"

        #
        _info["Health"] = self.grab_information(_sentinel, "Health.* ([0-9]{1,} %)").replace(' ', '')
        _info["Power On"] = self.grab_information(_sentinel, "Power On Time.*: (.*)", '1').split(' ')[0]

        #
        interface = self.grab_information(_sentinel, "Disk Interface.*: (.*)")
        if interface:
            if "150" in interface:
                interface = "SATA1 (1.5Gbps)"
            elif "300" in interface:
                interface = "SATA2 ( 3Gbps )"
            elif "600" in interface:
                interface = "SATA3 ( 6Gbps )"
        _info["Interface"] = interface

        # Disk Drive Dimensions
        _info["Width"] = self.grab_information(_sentinel, "Width.*: (.*) mm")
        _info["Height"] = self.grab_information(_sentinel, "Height.*: (.*) mm")
        _info["Length"] = self.grab_information(_sentinel, "Depth.*: (.*) mm")
        _info["Weight"] = self.grab_information(_sentinel, "Weight.*: (.*) grams")
        # Disk Drive Consumption
        _info["Power Spin"] = self.grab_information(_sentinel, r"Required Power For Spinup.*: (.*)")
        _info["Power Seek"] = self.grab_information(_sentinel, r"Power Required \(seek\).*: (.*)")
        _info["Power Idle"] = self.grab_information(_sentinel, r"Power Required \(idle\).*: (.*)")
        _info["Power Standby"] = self.grab_information(_sentinel, r"Power Required \(standby\).*: (.*)")
        # Drive S.M.A.R.T.
        _info["Description"] = self.grab_information(_sentinel, r"Performance.*[\s](^$[\s\S]+?^$)", '', 'Multiline')
        _info["Total Writes"] = self.grab_information(_sentinel, "Lifetime Writes.*: (.*)", "N/A")
        _info["Notes"] = ''  # WIP

    # Quickly cleans partition table of disk drive
    @staticmethod
    def clean_disk(_block):
        try:
            subprocess.check_output('shred ' + _block + ' -f -s 3M -n 1 -v', shell=True,
                                    bufsize=4096, timeout=60).decode('utf-8', errors='ignore')
            subprocess.check_output('wipefs -af ' + _block, shell=True,
                                    bufsize=4096, timeout=60).decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            print("Command timeout has expired! Something went wrong with " + str(_block))


disk_check = DiskChecker()
