import datetime
import getopt
import os
import re
import subprocess
import sys
import warnings

from Server import *

warnings.simplefilter("ignore")


class InfoCollector:
    manufacturer_replacements = [("asus", "ASUS"),
                                 ("Asus", "ASUS"),
                                 ("ASUS.", "ASUS"),
                                 ("ASUSTeK Computer", "ASUS"),
                                 ("Advanced Micro Devices", "AMD"),
                                 ("[AMD]", ""),
                                 ("lenovo", "Lenovo"),
                                 ("Lenovo", "Lenovo"),
                                 ("LENOVO", "Lenovo"),
                                 ("msi", "MSI"),
                                 ("Micro-Star International", "MSI"),
                                 ("hp", "HP"),
                                 ("Hp", "HP"),
                                 ("Hewlett-Packard", "HP"),
                                 ("samsung", "Samsung"),
                                 ("SAMSUNG ELECTRONICS", "Samsung"),
                                 ("pb", "Packard Bell"),
                                 ("Pakard Bell", "Packard Bell"),
                                 ("Sony Corporation", "Sony"),
                                 ("Co., Ltd.", ""),
                                 ("CO., LTD.", ""),
                                 ("Corp.", ""),
                                 ("Chassis Manufacturer", ""),
                                 ("Inc.", ""),
                                 ("INC.", ""),
                                 ("vendor:", ""),
                                 ("To Be Filled By O.E.M.", ""),
                                 ("To Be Filled by O.E.M.", ""),
                                 ("To Be filled by O.E.M.", ""),
                                 ("To be filled by O.E.M.", ""),
                                 ("OEM Chassis Manufacturer", ""),
                                 ("OEM", "")]
    system_models_replacement = [("(*)", ""),
                                 ("To Be Filled By O.E.M.", ""),
                                 ("To Be filled by O.E.M.", ""),
                                 ("To be filled by O.E.M.", ""),
                                 ("vendor:", ""),
                                 ("product:", ""),
                                 ("Corp.", ""),
                                 ("ASUS", ""),
                                 ("Aspire", ""),
                                 ("SAMSUNG SENS Series", ""),
                                 ("Dell", ""),
                                 # ("Latitude"                                  , ""),
                                 ("HP", ""),
                                 # ("EliteBook"                                 , ""),
                                 # ("Pavilion"                                  , ""),
                                 # ("ProBook"                                   , ""),
                                 # ("EasyNote"                                  , ""),
                                 # ("LIFEBOOK"                                  , ""),
                                 ("Lenovo", ""),
                                 # ("ThinkPad"                                  , ""),
                                 # ("ThinkCentre"                               , ""),
                                 ("Micro-Star International", ""),
                                 ("MSI", ""),
                                 ("non-vPro", ""),
                                 ("vPro", ""),
                                 ("non-v", ""),
                                 ("Business System", ""),
                                 ("Notebook", ""),
                                 ("PC", ""),
                                 ("Small Form Factor", "SFF"),
                                 ("( ", "("),
                                 (" )", ")"),
                                 ("Notebook", ""),
                                 ("System", ""),
                                 ("SKUNumber", ""),
                                 ("-SKU", ""),
                                 ("SKU", ""),
                                 ("Type1Sku0", ""),
                                 ("(123456789)", ""),
                                 ("012345678912345678912345678", ""),
                                 ("0000000000000000", ""),
                                 ("N/A", ""),
                                 ("Co., Ltd.", ""),
                                 ("( )", ""),
                                 ("()", ""),
                                 ("product:", ""),
                                 ("version:", ""),
                                 ("*", "")]
    cpu_model_replacements = [("(R)", ""),
                              ("(TM)", ""),
                              ("(tm)", ""),
                              ("@", ""),
                              (",", ""),
                              (", 10", ""),
                              ("Dual-Core", ""),
                              ("Triple-Core", ""),
                              ("Quad-Core", ""),
                              ("Dual", ""),
                              ("Triple", ""),
                              ("APU with Radeon", ""),
                              ("APU", ""),
                              ("R2", ""),
                              ("R4", ""),
                              ("R5", ""),
                              ("R6", ""),
                              ("Compute Cores 4C+6G", ""),
                              ("Intel", ""),
                              ("AMD", ""),
                              ("Advanced Micro Devices", ""),
                              ("HD Graphics", ""),
                              ("HD", ""),
                              ("Radeon", ""),
                              ("Graphics", ""),
                              ("CPU", ""),
                              ("Processor", ""),
                              ("Core(TM)", ""),
                              ("Mobile", ""),
                              ("with", ""),
                              ("2 Solo", ""),
                              ("2 Duo", ""),
                              ("2 Extreme", ""),
                              ("2 Quad", ""),
                              ("Celeron", ""),
                              ("Core", ""),
                              ("vendor:", ""),
                              ("product:", ""),
                              ("[", ""),
                              ("]", ""),
                              ("Pentium", "")]
    gpu_model_replacements = [("[AMD]", "AMD"),
                              ("Nvidia", "NVIDIA"),
                              (",", ""),
                              (",", ""),
                              ("ASUSTek Computer Inc.", ""),
                              ("ASUSTeK Computer Inc.", ""),
                              ("Acer Incorporated", ""),
                              ("[ALI]", ""),
                              ("CardExpert Technology", ""),
                              ("Dell Latitude", ""),
                              ("Dell Precision", ""),
                              ("Dell", ""),
                              ("Integrated Graphics", ""),
                              ("Fujitsu Limited.", ""),
                              ("Fujitsu Limited.", ""),
                              ("Hewlett-Packard Company", ""),
                              ("Mobile 4", ""),
                              ("Mobility", ""),
                              ("Series Chipset", ""),
                              ("Series Graphics", ""),
                              ("Processor Family", ""),
                              ("Processor Family", ""),
                              ("Core Processor", ""),
                              ("Core Processor", ""),
                              ("Lenovo Thinkpad", ""),
                              ("Lenovo", ""),
                              ("PC Partner Limited /", ""),
                              ("Sapphire Technology Radeon", ""),
                              ("Samsung Electronics Co Ltd", ""),
                              ("Toshiba America Info Systems", ""),
                              ("Sony", ""),
                              ("(rev a1)", ""),
                              ("(rev a2)", ""),
                              ("[]", "")]

    def __init__(self):
        # Main Variables and CLI Option Parser      
        self.appTitle = "PC Auditor"
        self.appVersion = "v.5.3"

        self.debug_categories = dict()
        self.isSingleThread = True  # Do we want to run application on single thread only?
        self.isDebugOn = False  # Simple debug mode
        self.logFilterLevel = 0  # Log Filter Level, for debug, from 0 to 4
        self.isAdvancedDebug = False  # Advanced debug, etc. time elapsed between commands
        self.lastFunctionTime = 0  # For AD, how much ms passed since last function
        self.isDataCheckOff = False  # Data Rechecking, skips keyboard test and etc.
        self.isOutputModeOn = False  # If we need to write debug log to file
        self.isIPManuallySet = False  # If user manually set server ip
        self.parsedIP = 0  # User manually entered IP
        self.outputFile = None
        self.parse_cli_arg()

        # Init all dicts
        self.id_Dict = dict()
        self.cpu_Dict = dict()
        self.gpu_Dict = dict()
        self.ram_Dict = dict()
        self.screen_Dict = dict()
        self.drive_Dict = dict()
        self.cdrom_Dict = dict()
        self.battery_Dict = dict()

        self.currentGPUTry = 0
        self.currentDriveTry = 0
        self.currentBatTry = 0

        self.gpu_Output = None
        self.drive_Output = None
        self.bat_Output = None
        self.isCDROMDetected = None
        self.isCameraDetected = None

        # OBS  Variable  Initialization
        self.observations = dict()
        self.observations["All"] = dict()
        self.observations["Recorded"] = dict()

        self.assignedBatch = ""
        self.avail_Batches = ""

        self.avail_Categories = ""
        self.assignedCategory = ""

        self.boxNumber = ""

        self.previousTester = ""
        self.avail_testers = ""

        self.isSold = ""
        self.deviceLicense = ""

        self.pictures = []
        self.obsAddNotes = ""

        self.order_Client = ""
        self.order_Name = ""
        self.order_Status = ""
        self.order_AvailStatus = ""
        self.isOrdered = False

        self.appResourcePath = self.find_resource_folder()

        self.avail_CameraOptions = ["Yes", "No", "Broken", "No video", "Not tested"]
        self.avail_CDROMOptions = ["Present", "Present - Broken", "Missing - Moulage", "Missing", "isn't Supported"]
        self.avail_Licenses = ["None", "Win XP", "Win XP Pro", "Win Vista",
                               "Win 7 HP", "Win 7 Str", "Win 7 Pro", "Win 7 Ult",
                               "Win 8", "Win 8 Pro", "Win 8.1", "Win 8.1 Pro",
                               "Win 10", "Win 10 Pro"]
        self.debug_info("Information", "All Variables initilizated\n")

        self.cpu_temp_key = None
        self.cpu_sensors = None

        self.gpu_temp_key = None
        self.gpu_sensors = None

        self.lshw_Output = self.load_system_information("lshw.log", ['lshw', '-disable', 'SCSI'], "System", "lshw")

        if not self.isSingleThread:
            self._MainSysThread = threading.Thread(target=self.init_system_information)
            self._MainSysThread.start()

            self.server = Server(self, self.parsedIP)

            self._DisplayThread = threading.Thread(target=self.init_display_information)
            self._DisplayThread.start()

            self._MainHWThread = threading.Thread(target=self.init_main_hardware_information)
            self._MainHWThread.start()

            self._BatteryThread = threading.Thread(target=self.init_battery_information)
            self._BatteryThread.start()
            self._DriveThread = threading.Thread(target=self.init_drive_information)
            self._DriveThread.start()
        else:
            self.init_system_information()
            self.server = Server(self, self.parsedIP)
            self.init_display_information()
            self.init_main_hardware_information()
            self.init_battery_information()
            self.init_drive_information()
        print("")

    # < Application Specific Functions
    def parse_cli_arg(self):
        try:
            argument_list = sys.argv[1:]
            unix_options = "d:axo:s:t:"
            gnu_options = ["debug", "advanceddebug", "skipkeyboard", "output", "serverip", "threaded"]

            arguments, values = getopt.getopt(argument_list, unix_options, gnu_options)
            for current_argument, current_value in arguments:
                current_argument = current_argument.lower()
                if current_argument in ("-d", "--debug"):

                    self.debug_categories["Blank"] = 0
                    self.debug_categories["Information"] = 0
                    self.debug_categories["Notice"] = 1
                    self.debug_categories["Warning"] = 2
                    self.debug_categories["Exception"] = 2
                    self.debug_categories["Error"] = 3
                    self.debug_categories["Critical"] = 4
                    self.isDebugOn = True
                    try:
                        if isinstance(int(current_value), int):
                            self.logFilterLevel = int(current_value)
                    except ValueError:
                        print("You can only pass number to log level filter")
                        exit()

                elif current_argument in ("-a", "--advanceddebug"):
                    self.isAdvancedDebug = True

                elif current_argument in ("-x", "--skipkeyboard"):
                    self.isDataCheckOff = True

                elif current_argument in ("-o", "--output"):
                    self.outputFile = current_value
                    self.isOutputModeOn = True

                elif current_argument in ("-s", "--serverip"):
                    current_value = "http://" + str(current_value) + ":8000/"
                    self.parsedIP = current_value.split()
                    self.isIPManuallySet = True

                elif current_argument in ("-t", "--threaded"):
                    self.isSingleThread = current_value

                else:
                    self.debug_info("Information", "Undefined option was given " + str(values))
                    self.debug_info("Information", "Undefined option was given " + str(current_value))

            if self.isDebugOn:
                self.debug_info("Information", "Debug Mode is ON")
            if self.isAdvancedDebug:
                self.debug_info("Information", "Advanced Debug Mode is ON")
            if self.isDataCheckOff:
                self.debug_info("Notice", "Data verification is disabled!")
            if self.isOutputModeOn:
                self.debug_info("Information", "Output file was assigned as " + self.outputFile)
            if self.isIPManuallySet:
                self.debug_info("Information", "Server was manually set to " + str(self.parsedIP))
            if not self.isSingleThread:
                self.debug_info("Warning", "! Single Thread mode !")
        except getopt.error as err:
            self.debug_info("Error", "Something went wrong trying to parse CLI arguments:\n" + str(err))

    def find_resource_folder(self):
        paths = ['Resources/', '/root/GUI/Resources/', '/root/Resources/']
        for directory in paths:
            if os.path.exists(directory):
                self.debug_info("Information", "Resource folder was found in '" + directory + "'")
                return directory
        self.debug_info("Warning", "Resource folder wasn't found, some pictures, audio will not load or work")
        return "Warning! No Resource folder found"

    # < Debug Functions
    def debug_info(self, log_level, text=''):
        if self.isDebugOn and self.logFilterLevel <= self.debug_categories[log_level]:
            current_frame = sys._getframe().f_back
            filename = current_frame.f_code.co_filename.split("/", -1)[-1]
            function = current_frame.f_code.co_name + '()'
            line_no = current_frame.f_lineno

            current_time = str(datetime.datetime.now().time())
            execution_time = float(current_time.replace(':', ''))

            if self.lastFunctionTime:
                timedelta = execution_time - self.lastFunctionTime
            else:
                timedelta = 000.000000
            self.lastFunctionTime = execution_time
            current_time = current_time + " | " + '{:.6f}'.format(timedelta)

            line_no = '{: <4}'.format(line_no)
            log_level = '{: <12}'.format(log_level)
            filename = '{: <17}'.format(filename)
            function = '{: <30}'.format(function)

            # Set Text color based on log level
            default_color = "\033[0m"
            category_color = ""
            if "Information" in log_level:
                category_color = "\033[0m"  # Black  HI
            elif "Notice" in log_level:
                category_color = "\033[1;36m"  # Cyan   Bold
            elif "Warning" in log_level:
                category_color = "\033[1;33m"  # Yellow Bold
            elif "Error" in log_level:
                category_color = "\033[1;91m"  # Red    Bold
            elif "Critical" in log_level:
                category_color = "\033[1;35m"  # Purple Bold

            caller_info = filename + " | " + function + " -> "
            caller_info = category_color + caller_info + default_color
            log_level = category_color + log_level + default_color
            line_no = category_color + line_no + default_color

            # Now concatenate to one string and output
            formatted_text = current_time + ' | ' + line_no + ' - ' + log_level + ' ' + caller_info + str(text)
            print(formatted_text)

            if self.isOutputModeOn:
                formatted_text = formatted_text.replace(category_color, '').replace(default_color, '')
                with open(self.outputFile, 'a') as log_file:
                    log_file.write(formatted_text + "\n")

    # < Init Functions
    def init_system_information(self):
        self.id_Dict["Collected"] = {}
        self.id_Dict["GUI"] = {}
        self.get_system_information()

    def init_main_hardware_information(self):
        self.cpu_Dict["Collected"] = {}
        self.cpu_Dict["GUI"] = {}
        self.cpu_Dict["Stats"] = {}
        self.cpu_Dict["Stats"]["Temps"] = {}
        self.cpu_Dict["Stats"]["Temps"]["Dynamic"] = {}
        self.cpu_Dict["Stats"]["Clock"] = {}
        self.get_cpu()

        self.gpu_Dict["Collected"] = {}
        self.gpu_Dict["GUI"] = {}
        self.gpu_Dict["Stats"] = {}
        self.gpu_Dict["Stats"]["Temps"] = {}
        self.gpu_Dict["Stats"]["Temps"]["Dynamic"] = {}
        self.gpu_Dict["Stats"]["Clock"] = {}
        self.get_gpu()

        self.ram_Dict["Collected"] = {}
        self.ram_Dict['Collected']["Type"] = ""
        self.ram_Dict["Collected"]["No"] = 1
        self.ram_Dict["GUI"] = {}
        self.get_rams()

    def init_display_information(self):
        self.screen_Dict["Collected"] = {}
        self.screen_Dict["GUI"] = {}
        self.get_display()
        self.get_camera()

    def init_drive_information(self):
        self.drive_Output = self.load_information_output("Drive", "Drives.log", 5)
        self.drive_Dict["Collected"] = {}
        self.drive_Dict["Collected"]["No"] = 1
        self.drive_Dict["GUI"] = {}
        self.get_drives()

        self.cdrom_Dict["Collected"] = {}
        self.cdrom_Dict["Collected"]["No"] = 1
        self.cdrom_Dict["GUI"] = {}
        self.isCDROMDetected = False
        self.get_cdrom()

    def init_battery_information(self):
        self.bat_Output = self.load_information_output("Battery", "BatteryBenchmark.log", 5)
        self.battery_Dict["Collected"] = {}
        self.battery_Dict["Collected"]["No"] = 1
        self.battery_Dict["GUI"] = {}
        self.get_batteries()

    # < File Functions | Loading and Reading
    def load_system_information(self, filename, command, category, variable):
        try:
            if os.path.exists(filename):
                state = ' file was found'
                with open(filename, 'r') as tmp:
                    local = tmp.read()
            else:
                state = ' command executed'
                local = subprocess.check_output(command).decode('utf-8')
            self.debug_info("Notice", category + " Information - " + variable + state + " and loaded")
        except Exception as e:
            local = ""
            self.debug_info("Exception", variable + " Output  | " + str(e))
        return local

    def load_information_output(self, category, filename, retry_amount):
        self.debug_info("Information", category + " Information - Loading information to variable")
        if not os.path.exists(filename):
            self.debug_info("Error", category + " Information - File doesn't exist, retrying...")
            self.get_information_output(category, filename, retry_amount)
        self.debug_info("Information", category + " Information - File detected,trying to read it...")
        try:
            with open(filename, 'r') as tmp:
                file_content = tmp.read()
            self.debug_info("Notice", category + " Information - File was loaded")
            return file_content
        except IOError:
            self.debug_info("Error", category + " Information - File couldn't be read")

    def get_information_output(self, category, filename, retry_amount):
        current_try = ''
        command = ['']
        if "Battery" in category:
            command = ['/root/.Scripts/BatteryCheck.sh', '-m', 'info', '-t', '0']
            current_try = self.currentBatTry = self.currentBatTry + 1
        elif "GPU" in category:
            command = ['/root/.Scripts/PXECraft.sh', '--get-gpu']
            current_try = self.currentGPUTry = self.currentGPUTry + 1
        elif "Drive" in category:
            command = ['/root/.Scripts/GetDrivesInfo.sh']
            current_try = self.currentDriveTry = self.currentDriveTry + 1
        self.debug_info("Information", category + " Information - Trying to extract information about " + str(
            category) + " | " + str(current_try) + " / " + str(retry_amount))

        try:
            subprocess.Popen(command).wait()
        except subprocess.CalledProcessError:
            command[0] = command[0].replace("/root/.Scripts/",
                                            "/home/konstantin/Documents/Programming/Scripts/Sopena Group/")
            self.debug_info("Warning", category + " Information - Couldn't get information, trying to change directory")
            subprocess.Popen(command).wait()

        if current_try < retry_amount:
            tmp = self.load_information_output(category, filename, retry_amount)
            return tmp
        else:
            self.debug_info("Error", category + " | Maximum retries exceeded limit")
            return ""

    # < Info Collecting Functions, SYS DONE, CPU DONE
    def get_system_information(self):
        self.debug_info("Information", "System Information - Initialization")

        # Master String
        master_string = self.get_regex_info(r"[\s\S]+?(?=\*-)", self.lshw_Output, 'search', 0)

        # Serial Number
        serial = self.get_regex_info(r"\bserial\:(.*)", master_string, 'search', 1)

        # Manufacturer
        manufacturer = self.get_regex_info(r"\bvendor\:(.*)", master_string, 'search', 1)
        if manufacturer:
            manufacturer = self.replace_strings("Manufacturer", manufacturer)

        # System Model
        if 'lenovo' not in manufacturer.lower():
            _regex = r'\bproduct\:(.*)'
        else:
            _regex = r'\bversion\:(.*)'
        model = self.get_regex_info(_regex, master_string, 'search', 1)
        if model:
            model = self.replace_strings("Device Model", model)

        # System Type
        sys_type = self.get_regex_info(r"\bdescription\:(.*)", master_string, 'search', 1)
        if sys_type:
            sys_type = sys_type.lower()
            if "notebook" in sys_type:
                sys_type = "Laptop"
            elif "portable" in sys_type:
                sys_type = "Laptop"
            elif "laptop" in sys_type:
                sys_type = "Laptop"
            elif "loptop" in sys_type:
                sys_type = "Laptop"
            elif "desktop" in sys_type:
                sys_type = "Desktop"
            elif "tower" in sys_type:
                sys_type = "Desktop"
            elif "space-saving computer" in sys_type:
                sys_type = "Desktop"  # SFF
            elif "computer" in sys_type:
                sys_type = ""  # If it cannot be decide, let user write it

        # MB Serial Number
        master_string = self.get_regex_info(r'\*-core+[\s\S]+?\*-', self.lshw_Output, 'search', 0)

        mb_serial = self.get_regex_info(r'\bserial\:(.*)', master_string, 'search', 1)
        if mb_serial:
            mb_serial = mb_serial.replace(serial, '').replace("/", "").replace(".", "").replace(
                "BASE BOARD SERIAL NUMBER", "")
            if not mb_serial:
                mb_serial = serial
        else:
            mb_serial = serial

        # Pushing To Dict
        self.id_Dict["Collected"]["Serial"] = serial.upper()
        self.id_Dict["Collected"]["Manufacturer"] = manufacturer
        self.id_Dict["Collected"]["Model"] = model
        self.id_Dict["Collected"]["System Type"] = sys_type
        self.id_Dict["Collected"]["MB Serial"] = mb_serial.upper()
        self.id_Dict["Collected"]["BIOS"] = "N/A"
        self.debug_info("Information", "System Information - Values are loaded!")

    def get_cpu(self):
        self.debug_info("Information", "CPU Information - Initialization")

        # Master String
        lscpu_output = self.load_system_information("lscpu.log", ['lscpu', '-J'], "CPU", "lscpu")
        _master = dict()
        for _line in lscpu_output.splitlines():
            if 'field' in _line:
                _line = _line.replace('{"field":', '').replace(':', '').replace(', "data"', ':').replace('},', '')
                _line = re.sub(r'  +', '', _line)
                _line = _line.replace('"', '').split(':')
                _master[_line[0].lower()] = _line[1]

        # Manufacturer
        manufacturer = _master.get('vendor id', '').replace('Genuine', '').replace('Authentic', '')

        # Model
        model = _master.get('model name', '@').replace('Genuine', '')
        stock_clock = _master.get('model name', '0 @ 0')
        if 'Intel' in manufacturer:
            model = model.split('@')[0]
            stock_clock = stock_clock.split('@')[1].replace("GHz", '').replace("MHz", '')
        else:
            model = model.split(' APU')[0]
            stock_clock = _master.get('cpu max mhz', '0.0').split('.')[0]
            stock_clock = str(int(stock_clock) / 1000)
        model = self.replace_strings('CPU Model', model)

        # Minimal / Maximum Clock
        minimal_clock = _master.get('cpu min mhz', '0.0').split('.')[0]
        maximum_clock = _master.get('cpu max mhz', '0.0').split('.')[0]
        if maximum_clock == '0': maximum_clock = float(stock_clock) * 1000

        core_amount = _master.get('core(s) per socket', 1)
        thread_amount = _master.get('cpu(s)', 1)

        self.cpu_Dict["Collected"]["Manufacturer"] = manufacturer
        self.cpu_Dict["Collected"]["Model"] = model
        self.cpu_Dict["Collected"]["Core Amount"] = core_amount
        self.cpu_Dict["Collected"]["Thread Amount"] = thread_amount
        self.cpu_Dict["Collected"]["Stock Clock"] = stock_clock + " GHz"
        self.cpu_Dict["Collected"]["Minimum Clock"] = str(float(minimal_clock) / 1000) + " GHz"
        self.cpu_Dict["Collected"]["Maximum Clock"] = str(float(maximum_clock) / 1000) + " GHz"
        self.cpu_Dict["Collected"]["Minimum Clock INT"] = float(minimal_clock)
        self.cpu_Dict["Collected"]["Maximum Clock INT"] = float(maximum_clock)
        self.debug_info("Information", "CPU Information - Values are loaded!")

    def get_rams(self):
        self.debug_info("Information", "RAM Information - Initialization")
        total_amount = 0
        iter_no = 0

        for iter_no in range(32):
            if iter_no == 0:
                master_pattern = re.compile(r'\*-bank[\s\S]+?(?=\*)')
            else:
                master_pattern = re.compile(r'\*-bank:' + str(iter_no) + r'[\s\S]+?(?=\*)')
            master_string = self.get_regex_info(master_pattern, self.lshw_Output, 'search', 0)
            self.lshw_Output = self.lshw_Output.replace(master_string, '')

            if master_string:
                # Type
                if not self.ram_Dict['Collected']['Type']:
                    ram_type = self.get_regex_info(r'(DDR[0-9])', master_string, 'search', 0)
                    if ram_type:
                        self.ram_Dict['Collected']["Type"] = ram_type

                # Model
                model = self.get_regex_info(r'\bproduct\:(.*)', master_string, 'search', 1)

                # Clock
                clock = self.get_regex_info(r'\bclock\:(.*MHz)', master_string, 'search', 1)

                # Serial
                serial = self.get_regex_info(r'\bserial\:(.*)', master_string, 'search', 1)
                if serial and 'empty' in serial.lower():
                    continue

                # Capacity
                size = self.get_regex_info(r'\bsize\:(.*\d)', master_string, 'search', 1)

                if size:
                    keyword = str(self.ram_Dict["Collected"]["No"]) + " Stick"
                    if keyword not in self.ram_Dict['Collected']:
                        self.ram_Dict['Collected'][keyword] = {}
                    if size.isdigit():
                        total_amount += int(size)
                    self.ram_Dict['Collected'][keyword]["Serial"] = serial
                    self.ram_Dict['Collected'][keyword]["Product"] = model
                    self.ram_Dict['Collected'][keyword]["Size"] = size + " GB"
                    self.ram_Dict['Collected'][keyword]["Clock"] = clock.replace("MHz", " MHz")
                    self.ram_Dict["Collected"]["No"] += 1
                    self.debug_info("Information", "\tRAM Information - Stick " + str(iter_no) + " loaded!")
                    iter_no += 1
                continue
            else:
                continue

        if "Total Amount" not in self.ram_Dict['Collected']:
            self.ram_Dict['Collected']["Total Amount"] = str(total_amount) + " GB"

    def get_gpu(self):
        gpu_output = self.load_information_output("GPU", "GPUList.log", 5)
        if not gpu_output:
            return False
        self.debug_info("Information", "GPU Information - Initialization")
        iter_no = 1

        while 1:
            iter_str = "GPU " + str(iter_no)
            if iter_str in gpu_output:

                model = self.get_regex_info(iter_str + r' - Model: (.+)', gpu_output, 'search', 1).rstrip('\n')
                manufacturer = self.get_regex_info(iter_str + r' - Manufacturer: (.+)', gpu_output, 'search', 1).rstrip(
                    '\n')

                if model:
                    if 'Mobile 4 Series Chipset' in model:
                        model = 'Mobile 4 Series Chipset'
                    else:
                        model = self.decode_intel_gpu(model)
                        model = self.replace_strings('GPU', model)
                if 'advanced' in manufacturer.lower() or 'ati' in manufacturer.lower():
                    manufacturer = "AMD"

                self.gpu_Dict['Collected'][str(iter_no) + " Model"] = model
                self.gpu_Dict['Collected'][str(iter_no) + " Manufacturer"] = manufacturer
                self.debug_info("Information", "\tGPU Information - " + iter_str + " loaded!")
                iter_no += 1
                continue
            else:
                if iter_no == 2:
                    self.gpu_Dict["Collected"][str(iter_no) + " Manufacturer"] = ""
                    self.gpu_Dict["Collected"][str(iter_no) + " Model"] = ""
                break

    def get_drives(self):
        self.debug_info("Information", "Drive Information - Initialization")
        tags = ['Model', 'Capacity', 'Speed', 'Locked', 'Size', 'Health', 'PowerOn', 'Interface',
                'Notes', 'Description', 'Manufacturer', 'Family', 'Width', 'Height', 'Length', 'Weight',
                'Spinup', 'Seek', 'Idle', 'Standby', 'Inspection', 'Type']
        iter_no = 1

        while 1:
            iter_str = "Drive " + str(iter_no)
            if iter_str in self.drive_Output:
                keyword = str(self.drive_Dict['Collected']["No"]) + " Drive"
                master = self.get_regex_info(iter_str + r'[\s\S]+?\=+\n?', self.drive_Output, 'search', 0)
                if master:
                    self.drive_Output = self.drive_Output.replace(master, '')
                    self.drive_Dict['Collected'][keyword] = {}
                if not master:
                    break

                serial = self.get_regex_info(r'SN: (.+)', master, 'search', 1)
                master = master.replace(iter_str + ' - SN: ' + serial, '')
                for _tag in tags:
                    if not _tag == 'Description':
                        info = self.get_regex_info(_tag + r': (.+)', master, 'search', 1).rstrip('\n')
                    else:
                        info = self.get_regex_info(_tag + r': (.[\s\S]+?(?=Drive))', master, 'search', 1).rstrip('\n')
                    master = master.replace(iter_str + ' - ' + _tag + ': ' + info, '')
                    self.drive_Dict['Collected'][keyword][_tag] = info
                self.drive_Dict['Collected'][keyword]["SN"] = serial
                self.drive_Dict['Collected']["No"] += 1
                self.debug_info("Information", "\tDrive Information - " + iter_str + " loaded!")
                iter_no += 1
                continue
            else:
                break

    def get_cdrom(self):
        self.debug_info("Information", "Optical Device Information - Initialization")
        iter_no = 1

        while 1:
            iter_str = "CDROM " + str(iter_no)
            if iter_str in self.drive_Output:
                keyword = str(self.cdrom_Dict['Collected']["No"]) + " Device"
                master = self.get_regex_info(iter_str + r'[\s\S]+?\=+\n?', self.drive_Output, 'search', 0)
                if master:
                    self.drive_Output = self.drive_Output.replace(master, '')
                    self.cdrom_Dict['Collected'][keyword] = {}
                if not master:
                    break

                serial = self.get_regex_info(r'SN: (.+)', master, 'search', 1).rstrip('\n')
                model = self.get_regex_info(r'Model: (.+)', master, 'search', 1).rstrip('\n')
                block = self.get_regex_info(r'BlockLoc: (.+)', master, 'search', 1).rstrip('\n')

                self.cdrom_Dict['Collected'][keyword]["SN"] = serial
                self.cdrom_Dict['Collected'][keyword]["Model"] = model
                self.cdrom_Dict['Collected'][keyword]["BlockLoc"] = block
                self.cdrom_Dict['Collected']["No"] += 1
                self.debug_info("Information", "\tOptical Device Information - " + iter_str + " loaded!")
                self.isCDROMDetected = True
                iter_no += 1
                continue
            else:
                break

    def get_batteries(self):
        self.debug_info("Information", "Battery Information - Initialization")
        tags = ['Serial', 'Model', 'Current Wh', 'Maximum Wh', 'Factory Wh', 'Wear Level', 'Estimated']
        iter_no = 1

        while 1:
            iter_str = "Battery " + str(iter_no)
            if iter_str in self.bat_Output:
                keyword = str(self.battery_Dict['Collected']["No"]) + " Battery"
                master = self.get_regex_info(iter_str + r'[\s\S]+?\=+\n?', self.bat_Output, 'search', 0)
                if master:
                    self.bat_Output = self.bat_Output.replace(master, '')
                    self.battery_Dict['Collected'][keyword] = {}
                if not master:
                    break

                bat_loc = self.get_regex_info(r'Ident: (.+)', master, 'search', 1)
                if bat_loc:
                    master = master.replace(iter_str + ' - Ident: ' + bat_loc, '')
                    for _tag in tags:
                        info = self.get_regex_info(_tag + r': (.+)', master, 'search', 1).rstrip('\n')
                        master = master.replace(iter_str + ' - ' + _tag + ': ' + info, '')
                        self.battery_Dict['Collected'][keyword][_tag] = info
                    self.battery_Dict['Collected']["No"] += 1
                    self.debug_info("Information", "\tBattery Information - " + iter_str + " loaded!")
                    iter_no += 1
                    continue
                else:
                    break
            else:
                break

    def get_display(self):
        self.debug_info("Information", "Display Information - Initialization")
        try:
            if os.path.exists("xrandr.log"):
                self.debug_info("Information", "\tDisplay Information - Master Output file was found")
                with open("xrandr.log", 'r') as tmp:
                    master_connected = tmp.read()
            else:
                master_string = subprocess.check_output(["xrandr"]).decode('utf-8')
                master_connected = self.get_regex_info(r'.* connected.*\n', master_string, 'search', 0)
            self.debug_info("Information", "\tDisplay Information - Master Output file was loaded")
        except Exception as e:
            master_connected = ""
            self.debug_info("Exception", "\tMaster Output  | " + str(e))
        self.debug_info("Information", "\tDisplay Information - Master Output")

        if master_connected:
            # Try to get Display Connection Type
            conn_type = self.get_regex_info(r'^[aA-zZ]+', master_connected, 'match', 0)
            self.debug_info("Information", "\tDisplay Information - Connection Type")

            # Try to get Display Resolution
            resolution = self.get_regex_info(r'[0-9]+x[0-9]+', master_connected, 'search', 0)
            self.debug_info("Information", "\tDisplay Information - Resolution")

            # Try to get Display Diagonal
            dimstr = self.get_regex_info(r'\) ([0-9]{1,}mm x [0-9]{1,}mm)', master_connected, 'search', 1)
            try:
                dim_arr = dimstr.replace("mm", "").replace(" ", "").split("x")
                length_square = int(dim_arr[0]) * int(dim_arr[0])
                height_square = int(dim_arr[1]) * int(dim_arr[1])
                diagonal = pow(length_square + height_square, 1 / 2)
                diagonal = round(diagonal * 0.03937, 1)
                # Moew lets fix broken diagonals
                if 8.0 <= diagonal <= 8.9:
                    diagonal = 8.0
                elif 9.5 <= diagonal <= 10.9:
                    diagonal = 10.1
                elif 11.0 <= diagonal <= 11.9:
                    diagonal = 11.6
                elif 12.0 <= diagonal <= 12.2:
                    diagonal = 12.0
                elif 12.3 <= diagonal <= 12.9:
                    diagonal = 12.5
                elif 13.0 <= diagonal <= 13.7:
                    diagonal = 13.3
                elif 13.8 <= diagonal <= 14.9:
                    diagonal = 14.1
                elif 15.0 <= diagonal <= 15.9:
                    diagonal = 15.6
                elif 17.0 <= diagonal <= 17.3:
                    diagonal = 17.3
                elif 17.4 <= diagonal <= 18.1:
                    diagonal = 17.4
                elif 18.2 <= diagonal <= 18.9:
                    diagonal = 18.3
                # Rawhr if needed add new diagonal above
            except Exception as e:
                diagonal = ""
                self.debug_info("Exception", "\tDiagonal        | " + str(e))
            self.debug_info("Information", "\tDisplay Information - Diagonal")

            # Try to get Display Resolution Category
            try:
                if "1024x768" in resolution:
                    category = "XGA"
                elif "1280x720" in resolution:
                    category = "720p (HD)"
                elif "1280x800" in resolution:
                    category = "720p (WXGA)"
                elif "1360x768" in resolution:
                    category = "720p (WXGA)"
                elif "1366x768" in resolution:
                    category = "720p (WXGA)"
                elif "1400x1050" in resolution:
                    category = "720p (SXGA+)"
                elif "1440x900" in resolution:
                    category = "720p (WXGA+)"
                elif "1600x900" in resolution:
                    category = "900p (HD+)"
                elif "1680x1050" in resolution:
                    category = "1080p (WSXGA+)"
                elif "1600x1200" in resolution:
                    category = "1080p (UXGA)"
                elif "1920x1080" in resolution:
                    category = "1080p (FHD)"
                elif "1920x1200" in resolution:
                    category = "1080p (WUXGA)"
                elif "2560x1080" in resolution:
                    category = "1080p (UFHD)"
                elif "2560x1440" in resolution:
                    category = "1440p (QHD)"
                elif "2560x1920" in resolution:
                    category = "1440p (WQXGA)"
                elif "3840x2160" in resolution:
                    category = "4K (UHD)"
                elif "5120x2880" in resolution:
                    category = "5K"
                elif "8192x4320" in resolution:
                    category = "8K (UHD)"
                else:
                    category = "No suitable category"
            except Exception as e:
                category = ""
                self.debug_info("Exception", "\tCategory        | " + str(e))
            self.debug_info("Information", "\tDisplay Information - Resolution Category")

            self.screen_Dict['Collected']["Diagonal"] = diagonal
            self.screen_Dict['Collected']["Resolution"] = resolution
            self.screen_Dict['Collected']["Category"] = category
            self.screen_Dict['Collected']["Connection Type"] = conn_type
            self.debug_info("Information", "\tDisplay Information - Values -> Dict")

    def get_camera(self, *_args):
        self.debug_info("Information", "Camera Information - Initialization")
        software = ["/root/.Software/luvcview", "/home/konstantin/Programs/luvcview"]
        argument = "-f yuv -s " + str(self.screen_Dict['Collected']["Resolution"])
        try:
            master_string = self.get_regex_info(r'uvcvideo', self.lshw_Output, 'search', 0)
            if master_string:
                self.debug_info("Information", "\tCamera was detected, searching for luvcview!")
                for path in software:
                    self.isCameraDetected = False
                    if os.path.isfile(path):
                        # self.debug_info("Error", "\tCouldn't launch luvcview!")
                        subprocess.Popen([str(path) + " " + argument], shell=True, stdout=subprocess.DEVNULL)
                        self.debug_info("Information", "Camera was found, and software was launched")
                        self.isCameraDetected = True
        except Exception as e:
            self.debug_info("Exception", "\tCouldn't get Camera\n " + str(e))
            self.isCameraDetected = False

    def get_core_clock(self):
        cpu_info = subprocess.Popen(['cat', '/proc/cpuinfo'], stdout=subprocess.PIPE)
        mhz_grep = subprocess.Popen(['grep', '-i', 'mhz'], stdin=cpu_info.stdout, stdout=subprocess.PIPE)
        output = subprocess.check_output(('grep', '-Eo', r'[0-9]{1,}\.[0-9]{1,}*'), stdin=mhz_grep.stdout).decode(
            'utf-8').rstrip('\r\n')
        current_core = 1
        for clock in output.split('\n'):
            clock = clock.split('.')[0]
            keyword = "Core " + str(current_core - 1)
            if keyword not in self.cpu_Dict['Stats']['Clock']:
                self.cpu_Dict['Stats']['Clock'][keyword] = []
            self.cpu_Dict['Stats']['Clock'][keyword].append(int(clock))
            if int(self.cpu_Dict['Collected']['Core Amount']) >= 1:
                if not current_core >= int(self.cpu_Dict['Collected']['Core Amount']):
                    current_core += 1
                else:
                    break

    @staticmethod
    def get_sensors_output():
        output = subprocess.run(["sensors", "-j"], stdout=subprocess.PIPE, encoding='utf-8').stdout
        # with open("Sensors.log", 'r') as tmp:
        #      output = tmp.read()
        return json.loads(output)

    def update_cpu_temp(self, cpu_dict, sensors):
        # Single time - Find CPU Main Sensors Name
        if not self.cpu_temp_key:
            if 'intel' in self.cpu_Dict["Collected"]["Manufacturer"].lower():
                cpu_regex = 'coretemp'
            elif 'amd' in self.cpu_Dict["Collected"]["Manufacturer"].lower():
                cpu_regex = 'k[0-9]+temp'
            else:
                return
            for _key, _value in sensors.items():
                if re.search(cpu_regex, _key):
                    self.cpu_temp_key = _key
                    break

        # Single time - Find Max & Critical temperatures and Find all sensors values
        if not self.cpu_sensors and self.cpu_temp_key:
            self.cpu_sensors = []
            for _key, _value in sensors[self.cpu_temp_key].items():
                if isinstance(_value, dict):
                    for _sub_key, _sub_value in sensors[self.cpu_temp_key][_key].items():
                        if 'Maximum' not in cpu_dict and 'max' in _sub_key:
                            cpu_dict["Maximum"] = _sub_value
                        if 'Critical' not in cpu_dict and 'crit' in _sub_key:
                            cpu_dict["Critical"] = _sub_value
                            if 'Maximum' not in cpu_dict:
                                cpu_dict["Maximum"] = _sub_value - 15

                        if 'input' in _sub_key:
                            _sensor = [_key, _sub_key]
                            if _key not in cpu_dict["Dynamic"]:
                                cpu_dict["Dynamic"][_key] = []
                            self.cpu_sensors.append(_sensor)

        # Update CPU Temperatures
        if self.cpu_temp_key:
            source_dict = sensors[self.cpu_temp_key]
            destination_dict = cpu_dict["Dynamic"]
            for _iter in range(len(self.cpu_sensors)):
                _main_key = self.cpu_sensors[_iter][0]
                _sub_key = self.cpu_sensors[_iter][1]

                destination_dict[_main_key].append(source_dict[_main_key][_sub_key])

    def update_gpu_temp(self, gpu_dict, sensors):
        # Single time - Find GPU Main Sensors Name
        if not self.gpu_temp_key:
            self.gpu_temp_key = []
            possible_gpu_regex = []
            if 'nvidia' in self.gpu_Dict["Collected"]["1 Manufacturer"].lower():
                possible_gpu_regex.append('nouveau')
            elif 'amd' in self.gpu_Dict["Collected"]["1 Manufacturer"].lower():
                possible_gpu_regex.append('radeon')
                possible_gpu_regex.append('amdgpu')

            if 'nvidia' in self.gpu_Dict["Collected"]["2 Manufacturer"].lower():
                possible_gpu_regex.append('nouveau')
            elif 'amd' in self.gpu_Dict["Collected"]["2 Manufacturer"].lower():
                possible_gpu_regex.append('radeon')
                possible_gpu_regex.append('amdgpu')

            for _key, _value in sensors.items():
                for regex in possible_gpu_regex:
                    if re.findall(regex, _key):
                        if _key not in self.gpu_temp_key:
                            self.gpu_temp_key.append(_key)

        # Single time - Find Max & Critical temperatures and Find all sensors values
        if not self.gpu_sensors and self.gpu_temp_key:
            self.gpu_sensors = []
            for _sensor in self.gpu_temp_key:
                for _key, _value in sensors[_sensor].items():
                    if isinstance(_value, dict):
                        for _sub_key, _sub_value in sensors[_sensor][_key].items():
                            if 'Maximum' not in gpu_dict and 'max' in _sub_key:
                                gpu_dict["Maximum"] = _sub_value
                                continue
                            if 'Critical' not in gpu_dict and 'crit' in _sub_key:
                                gpu_dict["Critical"] = _sub_value
                                if 'Maximum' not in gpu_dict:
                                    gpu_dict["Maximum"] = _sub_value - 15
                                continue

                            if _sensor not in gpu_dict["Dynamic"]:
                                gpu_dict["Dynamic"][_sensor] = []

                            if 'temp' in _sub_key and 'input' in _sub_key:
                                _values = [_key, _sub_key]
                                self.gpu_sensors.append(_values)

        # Update CPU Temperatures
        if self.gpu_temp_key:
            for _sensor in self.gpu_temp_key:
                source_dict = sensors[_sensor]
                destination_dict = gpu_dict["Dynamic"]
                for _iter in range(len(self.gpu_sensors)):
                    _main_key = self.gpu_sensors[_iter][0]
                    _sub_key = self.gpu_sensors[_iter][1]
                    destination_dict[_sensor].append(source_dict[_main_key].get(_sub_key, 0))
                    # print(destination_dict)

    # < Other (Unsorted) Functions
    @staticmethod
    def get_regex_info(_regex, _string, _method='findall', _group=None):
        information = ''
        try:
            if _method == 'search':
                information = re.search(_regex, _string)
            elif _method == 'findall':
                information = re.findall(_regex, _string)
            elif _method == 'match':
                information = re.match(_regex, _string)

            if information:
                if isinstance(_group, int):
                    information = information.group(_group)
                else:
                    information = information[0]
                return information.lstrip(' ')
            else:
                return ""
        except re.error:
            return ""

    @staticmethod
    def manage_photos(_device_sn, _device_model, _picture_list):
        if len(_picture_list) > 0:
            tar_path = subprocess.check_output(
                ['/root/.Scripts/PXECraft.sh', '--photo-list', _device_sn, _device_model, str(_picture_list)]).decode(
                'UTF-8').replace('\n', '')
        else:
            tar_path = ''
        return tar_path

    @staticmethod
    def decode_intel_gpu(text):
        if "haswell-ult" in text.lower().lstrip(''):
            text = "HD Graphics (Haswell ULT)"

        elif "4th gen" in text.lower().lstrip(''):
            text = "HD Graphics (Haswell)"

        elif "3rd gen" in text.lower().lstrip(''):
            text = "HD Graphics 4000"

        elif "2nd gen" in text.lower().lstrip(''):
            text = "HD Graphics 3000"

        elif "core processor" in text.lower().lstrip(''):
            text = "HD Graphics (Ironlake)"

        elif "atom/" in text.lower().lstrip('') or \
                "x5-E8000/J3xxx" in text.lower().lstrip(''):
            text = "HD Graphics (Atom/Celeron)"

        elif "atom proccesor" in text.lower().lstrip('') or \
                "Z36xxx" in text.lower().lstrip('') or \
                "Z37xxx" in text.lower().lstrip(''): \
                text = "HD Graphics (z3[6-7]xxx)"
        return text

    def replace_strings(self, title, string):
        unwanted_strings = []
        if title == "Manufacturer":
            unwanted_strings = self.manufacturer_replacements
        elif title == "Device Model":
            list_value = string.split()
            for start_index in range(len(list_value)):
                for end_index in reversed(range(start_index, len(list_value))):
                    front_value = list_value[start_index]
                    end_value = list_value[end_index]
                    if not start_index == end_index:
                        if front_value.replace('(', '').replace(')', '') == end_value.replace('(', '').replace(')', ''):
                            if end_index + 1 < len(list_value):
                                list_value[end_index + 1] = list_value[end_index + 1].replace('(', '').replace(')', '')
                            list_value[end_index - 1] = list_value[end_index - 1].replace('(', '').replace(')', '')
                            list_value.pop(end_index)
            string = ' '.join(str(ch) for ch in list_value)
            unwanted_strings = self.system_models_replacement
        elif title == "CPU Model":
            unwanted_strings = self.cpu_model_replacements
        elif title == "GPU":
            unwanted_strings = self.gpu_model_replacements

        for replacement in unwanted_strings:
            string = string.replace(replacement[0], replacement[1])
            string = re.sub(r'^ +', '', string)
            string = re.sub(r' +', ' ', string)
            string = re.sub(r' +$', '', string.strip())
        return string
