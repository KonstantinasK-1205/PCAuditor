# Importing Class
import json

import requests

from Events import *
from GUITemplate import *
from InfoCollector import *
from Pages.NBObservations import *
from Pages.NBOrder import *
from Pages.NBStress import *
from Pages.NBSummary import *
from Pages.NBTests import *


class MyWindow(Gtk.Window):
    def __init__(self):
        global summary_thread, observations_thread, tests_thread, stress_thread, order_thread
        Gtk.Window.__init__(self, default_width=1024, default_height=800,
                            border_width=3, window_position=1)
        self.MainBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.connect("key-press-event", events.main_event_parser)
        self.connect("button-press-event", events.main_event_parser)
        self.add(self.MainBox)
        infocollector.debug_info("Information", "GUI - Main Window initilizated")
        # < Variable Initialization
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.post_dict = dict()
        self.post_dict["Observations"] = {}

        infocollector.debug_info("Information", "GUI - Barebones Init...")
        self.TopContent = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        self.TopLine = Gtk.Box()
        self.TopContent.pack_start(self.TopLine, True, True, 0)

        self.AppWrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        self.MainNoteBook = Gtk.Notebook(tab_pos=Gtk.PositionType.LEFT)

        self.BottomContent = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        self.create_bottom_content(self.BottomContent)

        photo_bar_sb = guiTemplate.create_scrolling_box('Horizontal')
        self.PhotoBar = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.create_photo_bar(self.PhotoBar)
        photo_bar_sb.add(self.PhotoBar)
        infocollector.debug_info("Information", "GUI - Barebones initilizated")

        if not infocollector.isSingleThread:
            infocollector.debug_info("Information", "Starting to stop all gathering threads")
            infocollector._MainHWThread.join()
            infocollector._DisplayThread.join()
            infocollector._BatteryThread.join()
            infocollector._DriveThread.join()
            infocollector.debug_info("Information", "All gathering threads were stopped")

            for thread in infocollector.server.serverThreads:
                infocollector.debug_info("Information", "Waiting | Thread " + str(thread))
                thread.join()
                infocollector.debug_info("Information", "Done    | Thread " + str(thread))
            infocollector.debug_info("Information", "Stopping Server Threads")
        self.set_title(
            infocollector.appTitle + ' ' + infocollector.appVersion + ' | Server: ' + infocollector.server.serverIP)

        if not infocollector.isSingleThread:
            infocollector.debug_info("Information", "GUI - Summary Page")
            summary_thread = threading.Thread(target=nbSummary.create_page)
            summary_thread.start()
            if infocollector.observations["All"]:
                infocollector.debug_info("Information", "GUI - Observ. Page")
                observations_thread = threading.Thread(target=nbObservations.create_page)
                observations_thread.start()

            infocollector.debug_info("Information", "GUI - Test   Page")
            tests_thread = threading.Thread(target=nbTests.create_page)
            tests_thread.start()

            infocollector.debug_info("Information", "GUI - Stress Page")
            stress_thread = threading.Thread(target=nbStress.create_page)
            stress_thread.start()

            if infocollector.order_Name:
                infocollector.debug_info("Information", "GUI - Order Page")
                order_thread = threading.Thread(target=nbOrder.create_page)
                order_thread.start()
        else:
            nbSummary.create_page()
            if infocollector.observations["All"]:
                nbObservations.create_page()
            nbTests.create_page()
            nbStress.create_page()
            if infocollector.order_Name:
                nbOrder.create_page()

        # < Notebook | Finalising
        self.MainNoteBook.append_page(nbSummary.page_box, Gtk.Label("Summary"))
        self.MainNoteBook.append_page(nbTests.page_box, Gtk.Label("Tests"))
        if infocollector.observations["All"]:
            self.MainNoteBook.append_page(nbObservations.page_box, Gtk.Label("Observations"))
        self.MainNoteBook.append_page(nbStress.page_box, Gtk.Label("Stress"))
        if infocollector.order_Name:
            self.MainNoteBook.append_page(nbOrder.page_box, Gtk.Label("Order"))
        self.MainNoteBook.set_current_page(0)

        self.MainNoteBook.connect('key-release-event', events.get_notebook_page, self.MainNoteBook, 'main')
        self.MainNoteBook.connect('button-release-event', events.get_notebook_page, self.MainNoteBook, 'main')
        self.AppWrapper.pack_start(self.MainNoteBook, True, True, 0)
        self.AppWrapper.pack_start(photo_bar_sb, False, True, 0)

        # < Pushin all Layout to MainBox
        self.MainBox.pack_start(self.TopContent, False, False, 0)
        self.MainBox.pack_start(self.AppWrapper, True, True, 0)
        self.MainBox.pack_start(self.BottomContent, False, False, 0)

        if not infocollector.isSingleThread:
            summary_thread.join()
            observations_thread.join()
            tests_thread.join()
            stress_thread.join()
            if infocollector.order_Name:
                order_thread.join()

        events.init_variables(infocollector, self, nbTests)
        GLib.timeout_add(1000, nbStress.stress_thread, 1000, self.MainNoteBook, self)

    def create_bottom_content(self, box):
        button_array = [["Close", self.single_action_click, ""],
                        ["Restart", self.single_action_click, "Restart"],
                        ["Shutdown", self.single_action_click, "Shutdown"],
                        ["", ],
                        ["", ],
                        ["", ],
                        ["Open Cam", infocollector.get_camera, ""],
                        ["Bug Report", self.bug_report_action, "Report"],
                        ["ReInit Battery", self.re_init_battery, "ReInit Battery"],
                        ["ReInit Drives", self.re_init_drive, "ReInit Drives"],
                        ["Submit", self.submit_action, "Submit"]]
        for bttn in button_array:
            if bttn[0] == "":
                guiTemplate.create_label("\t\t", box)
            else:
                button = guiTemplate.create_button(bttn[0], bttn[1], _field=bttn[2])
                box.pack_start(button, True, True, 0)

    def create_photo_bar(self, production_box_col1):
        for no in range(0, len(infocollector.pictures)):
            picture_address = infocollector.pictures[no]
            image = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(picture_address, 128, 128))

            image_event_box = Gtk.EventBox()
            image_event_box.connect('button-press-event', self.on_mouse_click_show_pic, no)
            image_event_box.add(image)

            guiTemplate.create_separator(production_box_col1)
            production_box_col1.pack_start(image_event_box, True, True, 5)
            guiTemplate.create_separator(production_box_col1)

        if len(infocollector.pictures) == 0:
            image_add_pix_buf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                infocollector.appResourcePath + "Icons/ImageAdd.png", 64, 64)
        else:
            image_add_pix_buf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                infocollector.appResourcePath + "Icons/ImageAdd.png", 128, 128)
        image_add = Gtk.Image.new_from_pixbuf(image_add_pix_buf)
        image_add_event_box = Gtk.EventBox()
        image_add_event_box.connect('button-press-event', self.on_mouse_click_add_pic)
        image_add_event_box.add(image_add)
        production_box_col1.pack_start(image_add_event_box, False, False, 5)

    def reload_picture_gallery(self):
        for child in self.PhotoBar.get_children():
            child.destroy()
        self.create_photo_bar(self.PhotoBar)
        self.PhotoBar.show_all()

    @staticmethod
    def bug_report_action(_button, _action=''):
        is_confirmed, tester, problem = guiTemplate.throw_bugreport_win(win, "Bug Report")
        if is_confirmed:
            _button.set_sensitive(False)
            _identification = infocollector.id_Dict["Collected"]
            _id_serial = _identification["Serial"]
            _id_manufacturer = _identification["Manufacturer"]
            _id_model = _identification["Model"]

            _processor = infocollector.cpu_Dict["Collected"]
            _cpu_manufacturer = _processor["Manufacturer"]
            _cpu_model = _processor["Model"]

            _ram = infocollector.ram_Dict["Collected"]
            _ram_amount = _ram["Total Amount"]
            _ram_type = _ram["Type"]

            _gpu = infocollector.gpu_Dict["Collected"]
            _gpu_maf_1 = _gpu["1 Manufacturer"]
            _gpu_maf_2 = ''
            _gpu_model_1 = _gpu["1 Model"]
            _gpu_model_2 = ''
            if "2 Manufacturer" in _gpu:
                _gpu_maf_2 = _gpu["2 Manufacturer"]
                _gpu_model_2 = _gpu["2 Model"]

            _id = ' '.join(['Serial:', _id_serial, '| Manufacturer:', _id_manufacturer, '| Model:', _id_model])
            _cpu = ' '.join(['Processor:', _cpu_manufacturer, _cpu_model])
            _ram = ' '.join(['RAM:', _ram_amount, _ram_type])
            _gpu = ' '.join(['GPU:', _gpu_maf_1, _gpu_model_1, '|', _gpu_maf_2, _gpu_model_2])
            _lshw_output = infocollector.lshw_Output
            _lscpu = subprocess.check_output(['lscpu'], encoding='utf-8')
            _sensors_output = subprocess.check_output(['sensors', '-j'], encoding='utf-8')

            bug_report = dict()
            bug_report["alias"] = "Report from " + str(tester)
            bug_report["text"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "\n" + \
                                 "Bug report of " + _id_model + " | SN: " + _id_serial + "\n\n" + \
                                 "Problem description\n" + str(problem) + "\n------------------------------"
            bug_report["attachments"] = []
            commands = ["sensors -j", "lscpu -J", "lshw"]
            for output in commands:
                _output = subprocess.check_output(output.split(' '), encoding='utf-8')
                _report = dict()
                _report["title"] = output.split(' ')[0].capitalize() + " Report"
                _report["text"] = "```" + _output + "```"
                _report["collapsed"] = True
                bug_report["attachments"].append(_report)

            json_data = json.dumps(bug_report)
            url = 'http://192.168.0.1:3000/hooks/zbm63BT5nmg2qFaLc/WHqeHPMXnRYB4gdE9z3rKcXKaAr44H7oamf3qsxBgZcTzASn'
            re = requests.post(url, data=json_data)
            print(re.url)
            print(re.reason)
            print(re.elapsed)
        else:
            return ""

    def single_action_click(self, _button, action):
        if 'shutdown' in action.lower():
            os.system("shutdown -h now")
        elif 'restart' in action.lower():
            os.system("shutdown -hr now")
        elif 'close' in action.lower():
            if not guiTemplate.throw_question_win(self, "Confirm?", "Are you sure you want to exist?"):
                self.destroy()

    @staticmethod
    def re_init_battery(_button, _field):
        infocollector.init_battery_information()
        for child in nbSummary.togBATBox.get_children():
            child.destroy()
        guiTemplate.create_BatteryInformation(nbSummary.togBATBox)

    @staticmethod
    def re_init_drive(_button, _field):
        infocollector.firstLaunch = False
        infocollector.init_drive_information()
        for child in nbSummary.togDriveBox.get_children():
            child.destroy()

        for child in nbSummary.togOtherBox.get_children():
            child.destroy()
        guiTemplate.create_DriveInformation(nbSummary.togDriveBox)
        guiTemplate.create_OtherInformation(nbSummary.togOtherBox)

    def check_variable_value(self, _dict, error_mssg):
        if isinstance(_dict, Gtk.SpinButton):
            if _dict.get_value() == 0:
                infocollector.debug_info("Error", error_mssg)
                guiTemplate.throw_error_win(self, "Error!", error_mssg)
                return False
        elif isinstance(_dict, Gtk.Entry):
            if _dict.get_text() == '' or _dict.get_text() == ' ' or _dict.get_text() is None or _dict.get_text() == '0.0' or _dict.get_text() == 0.0:
                infocollector.debug_info("Error", error_mssg)
                guiTemplate.throw_error_win(self, "Error!", error_mssg)
                return False
        elif isinstance(_dict, Gtk.ComboBoxText):
            if _dict.get_active_text() == '' or _dict.get_active_text() is None:
                infocollector.debug_info("Error", error_mssg)
                guiTemplate.throw_error_win(self, "Error!", error_mssg)
                return False
        return True

    def submit_action(self, _button, _field):
        # Lets check if all required variables are set!)
        is_order_info_faulty = True
        if infocollector.order_Name:
            if nbOrder.status_entry.get_active_text() is None:
                guiTemplate.throw_error_win(self, "Error!", "You must select computer status (Order tab)")
            else:
                is_order_info_faulty = False
        else:
            is_order_info_faulty = False

        if infocollector.assignedBatch == '' and not infocollector.avail_Batches == '':
            if nbSummary.currentBatch.get_active_text() is None:
                guiTemplate.throw_error_win(self, "Error!", "Batch dropbox cannot be empty!")
                is_batch_faulty = True
            else:
                is_batch_faulty = False
        else:
            is_batch_faulty = False

        if not self.check_variable_value(infocollector.id_Dict["GUI"]["Serial"], "System Serial cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.id_Dict["GUI"]["MB Serial"],
                                         "System MB Serial cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.id_Dict["GUI"]["Manufacturer"],
                                         "System Manufacturer cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.id_Dict["GUI"]["Model"], "System Model cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.id_Dict["GUI"]["System Type"], "System Type cannot be empty!"):
            return False

        if not self.check_variable_value(infocollector.cpu_Dict["GUI"]["Manufacturer"],
                                         "CPU Manufacturer cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.cpu_Dict["GUI"]["Model"], "CPU Model cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.cpu_Dict["GUI"]["Stock Clock"],
                                         "CPU Stock Clock cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.cpu_Dict["GUI"]["Maximum Clock"],
                                         "CPU Max Clock cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.cpu_Dict["GUI"]["Core Amount"], "CPU Cores cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.cpu_Dict["GUI"]["Thread Amount"],
                                         "CPU Threads cannot be empty!"):
            return False

        if not self.check_variable_value(infocollector.ram_Dict["GUI"]['Type'], "RAM Type cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.ram_Dict["GUI"]['Total'], "RAM Capacity cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.ram_Dict["GUI"]['Total'], "RAM Capacity cannot be None!"):
            return False

        if not self.check_variable_value(infocollector.gpu_Dict["GUI"]["1 Manufacturer"],
                                         "iGPU Manufacturer cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.gpu_Dict["GUI"]["1 Model"], "iGPU Model cannot be empty!"):
            return False

        if not self.check_variable_value(infocollector.screen_Dict["GUI"]["Diagonal"],
                                         "Display Diagonal cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.screen_Dict["GUI"]["Resolution"],
                                         "Display Resolution cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.screen_Dict["GUI"]["Category"],
                                         "Display Category cannot be empty!"):
            return False
        if not self.check_variable_value(infocollector.screen_Dict["GUI"]["Connection Type"],
                                         "Display Type cannot be empty!"):
            return False

        if not self.check_variable_value(nbSummary.otherOptical, "Optical Device dropbox cannot be empty"):
            return False
        if not self.check_variable_value(nbSummary.otherLicense, "License dropbox cannot be empty"):
            return False
        if not self.check_variable_value(nbSummary.otherCamera, "Camera dropbox cannot be empty"):
            return False
        if not self.check_variable_value(nbSummary.tester, "Tester dropbox cannot be empty"):
            return False
        if not self.check_variable_value(nbSummary.category, "Category dropbox cannot be empty"):
            return False
        if not self.check_variable_value(nbSummary.destinationBox, "Box number cannot be empty"):
            return False

        if infocollector.id_Dict["GUI"]["System Type"].get_text() == "Laptop":
            kb_test_output = nbTests.check_keyboard_test()
            if kb_test_output[0]:
                if kb_test_output[1]:
                    if not guiTemplate.throw_question_win(win, "Keyboard Error!", kb_test_output[1]):
                        return False
            else:
                guiTemplate.throw_error_win(win, "Keyboard Error!", kb_test_output[1])
                infocollector.debug_info("Information", "Keyboard test wasn't completed")
                return False

        if is_order_info_faulty:
            infocollector.debug_info("Error", "There is a problem with order!")
            guiTemplate.throw_error_win(self, "Error!", "There is a problem with order!")
        elif is_batch_faulty:
            infocollector.debug_info("Error", "There is a problem with batch!")
            guiTemplate.throw_error_win(self, "Error!", "There is a problem with batch!")
        else:
            if nbStress.isGPUOverheating:
                guiTemplate.set_multiline_text(nbObservations.obsNotes, nbStress.gpuOverheatingText)
            if nbStress.isCPUOverheating:
                guiTemplate.set_multiline_text(nbObservations.obsNotes, nbStress.cpuOverheatingText)
            self.acquire_dict_info()
            if infocollector.server.record_exists():
                proceed = guiTemplate.throw_question_win(self, "Computer was already logged!",
                                                         "Computer with this SN [ " +
                                                         infocollector.id_Dict["GUI"]["Serial"].get_text() +
                                                         " ], was already logged!\nDo you want to update this computer?")
                if not proceed:
                    return False
            if infocollector.server.send_json(self.post_dict):
                has_passed = guiTemplate.throw_question_win(self, "Computer was logged!",
                                                            "Computer was logged successfully!\nDo you want to print QR for this machine?")
                if has_passed:
                    printer = guiTemplate.throw_options_win(self, "Choose Printer",
                                                            "Please choose from which printer you want to print")
                    if not printer == "Cancel":
                        infocollector.server.request_print_qr(printer)
                    else:
                        return False

    def on_mouse_click_add_pic(self, _widget, _event, _data=''):
        self.throw_file_chooser_window()

    @staticmethod
    def on_mouse_click_show_pic(_widget, _event, data):
        guiTemplate.throw_image_window(data, infocollector, events)

    def acquire_dict_info(self):
        # < Log Information
        self.post_dict["Log Information"] = {}
        self.post_dict["Log Information"]["Tester"] = nbSummary.tester.get_active_text()
        self.post_dict["Log Information"]["Category"] = nbSummary.category.get_active_text()
        self.post_dict["Log Information"]["Received batch"] = nbSummary.currentBatch.get_active_text()
        # < System Information
        self.post_dict["System Info"] = {}
        self.post_dict["System Info"]["Serial Number"] = infocollector.id_Dict["GUI"]["Serial"].get_text()
        self.post_dict["System Info"]["MB Serial"] = infocollector.id_Dict["GUI"]["MB Serial"].get_text()
        self.post_dict["System Info"]["Type"] = infocollector.id_Dict["GUI"]["System Type"].get_text().capitalize()
        self.post_dict["System Info"]["Manufacturer"] = infocollector.id_Dict["GUI"]["Manufacturer"].get_text()
        self.post_dict["System Info"]["Model"] = infocollector.id_Dict["GUI"]["Model"].get_text()
        self.post_dict["System Info"]["BIOS"] = infocollector.id_Dict["Collected"]["BIOS"]
        # < Processor Information
        self.post_dict["CPU"] = {}
        self.post_dict["CPU"]["1 Processor"] = {}
        self.post_dict["CPU"]["1 Processor"]["Manufacturer"] = infocollector.cpu_Dict["GUI"]["Manufacturer"].get_text()
        self.post_dict["CPU"]["1 Processor"]["Model"] = infocollector.cpu_Dict["GUI"]["Model"].get_text()
        self.post_dict["CPU"]["1 Processor"]["Stock Clock"] = infocollector.cpu_Dict["GUI"]["Stock Clock"].get_text()
        self.post_dict["CPU"]["1 Processor"]["Maximum Clock"] = infocollector.cpu_Dict["GUI"][
            "Maximum Clock"].get_text()
        self.post_dict["CPU"]["1 Processor"]["Cores Amount"] = infocollector.cpu_Dict["GUI"]["Core Amount"].get_text()
        self.post_dict["CPU"]["1 Processor"]["Threads Amount"] = infocollector.cpu_Dict["GUI"][
            "Thread Amount"].get_text()
        # < RAM Information
        self.post_dict["RAM"] = {}
        self.post_dict["RAM"]["Type"] = infocollector.ram_Dict["GUI"]['Type'].get_text()
        self.post_dict["RAM"]["Total"] = infocollector.ram_Dict["GUI"]['Total'].get_text()
        for iter_ in range(1, infocollector.ram_Dict["Collected"]["No"]):
            keyword = str(iter_) + " Stick"
            serial = infocollector.ram_Dict["GUI"][keyword]["Serial"].get_text()
            product = infocollector.ram_Dict["GUI"][keyword]["Product"].get_text()
            size = infocollector.ram_Dict["GUI"][keyword]["Size"].get_text()
            clock = infocollector.ram_Dict["GUI"][keyword]["Clock"].get_text()

            if keyword not in self.post_dict["RAM"]:
                self.post_dict["RAM"][keyword] = {}

            self.post_dict["RAM"][keyword]["Serial"] = serial
            self.post_dict["RAM"][keyword]["Model"] = product
            self.post_dict["RAM"][keyword]["Capacity"] = size
            self.post_dict["RAM"][keyword]["Clock"] = clock
        # < GPU Information
        self.post_dict["GPU"] = {}
        self.post_dict["GPU"]["1 Device"] = {}
        self.post_dict["GPU"]["1 Device"]["Manufacturer"] = infocollector.gpu_Dict["GUI"]["1 Manufacturer"].get_text()
        self.post_dict["GPU"]["1 Device"]["Model"] = infocollector.gpu_Dict["GUI"]["1 Model"].get_text()
        if not infocollector.gpu_Dict["GUI"]["2 Manufacturer"].get_text() == '':
            self.post_dict["GPU"]["2 Device"] = {}
            self.post_dict["GPU"]["2 Device"]["Manufacturer"] = infocollector.gpu_Dict["GUI"][
                "2 Manufacturer"].get_text()
            self.post_dict["GPU"]["2 Device"]["Model"] = infocollector.gpu_Dict["GUI"]["2 Model"].get_text()
        # < Hardware Information
        self.post_dict["Hardware"] = {}
        self.post_dict["Hardware"]["Additional"] = {}
        self.post_dict["Hardware"]["Additional"]["Camera"] = nbSummary.otherCamera.get_active_text()
        # < Display Information
        self.post_dict["Display"] = {}
        self.post_dict["Display"]["Diagonal"] = infocollector.screen_Dict["GUI"]["Diagonal"].get_text()
        self.post_dict["Display"]["Resolution"] = infocollector.screen_Dict["GUI"]["Resolution"].get_text()
        self.post_dict["Display"]["Category"] = infocollector.screen_Dict["GUI"]["Category"].get_text()
        self.post_dict["Display"]["Cable Type"] = infocollector.screen_Dict["GUI"]["Connection Type"].get_text()
        # < Drives Information
        for iter_ in range(1, infocollector.drive_Dict["Collected"]["No"]):
            if iter_ == 1:
                self.post_dict["Drives"] = {}
            keyword = str(iter_) + " Drive"
            serial = infocollector.drive_Dict["GUI"][keyword]["SN"].get_text()
            vendor = infocollector.drive_Dict["GUI"][keyword]["Manufacturer"].get_text()
            model = infocollector.drive_Dict["GUI"][keyword]["Model"].get_text()
            interface = infocollector.drive_Dict["GUI"][keyword]["Interface"].get_text()
            capacity = infocollector.drive_Dict["GUI"][keyword]["Capacity"].get_text()
            health = infocollector.drive_Dict["GUI"][keyword]["Health"].get_text()
            report = infocollector.drive_Dict["GUI"][keyword]["Description"]
            speed = infocollector.drive_Dict["Collected"][keyword]["Speed"]
            locked = infocollector.drive_Dict["Collected"][keyword]["Locked"]
            size = infocollector.drive_Dict["Collected"][keyword]["Size"]
            poweron = infocollector.drive_Dict["Collected"][keyword]["PowerOn"]
            notes = infocollector.drive_Dict["Collected"][keyword]["Notes"]
            family = infocollector.drive_Dict["Collected"][keyword]["Family"]
            width = infocollector.drive_Dict["Collected"][keyword]["Width"]
            height = infocollector.drive_Dict["Collected"][keyword]["Height"]
            length = infocollector.drive_Dict["Collected"][keyword]["Length"]
            weight = infocollector.drive_Dict["Collected"][keyword]["Weight"]
            powerspin = infocollector.drive_Dict["Collected"][keyword]["Spinup"]
            powerseek = infocollector.drive_Dict["Collected"][keyword]["Seek"]
            poweridle = infocollector.drive_Dict["Collected"][keyword]["Idle"]
            powerstan = infocollector.drive_Dict["Collected"][keyword]["Standby"]
            inspection = infocollector.drive_Dict["Collected"][keyword]["Inspection"]
            drivetype = infocollector.drive_Dict["Collected"][keyword]["Type"]

            if keyword not in self.post_dict["Drives"]:
                self.post_dict["Drives"][keyword] = {}

            self.post_dict["Drives"][keyword]["Serial"] = serial
            self.post_dict["Drives"][keyword]["Manufacturer"] = vendor
            self.post_dict["Drives"][keyword]["Model"] = model
            self.post_dict["Drives"][keyword]["Interface"] = interface
            self.post_dict["Drives"][keyword]["Capacity"] = capacity
            self.post_dict["Drives"][keyword]["Health"] = health
            self.post_dict["Drives"][keyword]["Description"] = report
            self.post_dict["Drives"][keyword]["Speed"] = speed
            self.post_dict["Drives"][keyword]["Locked"] = locked
            self.post_dict["Drives"][keyword]["Size"] = size
            self.post_dict["Drives"][keyword]["Power On"] = poweron
            self.post_dict["Drives"][keyword]["Notes"] = notes
            self.post_dict["Drives"][keyword]["Family"] = family
            self.post_dict["Drives"][keyword]["Width"] = width
            self.post_dict["Drives"][keyword]["Height"] = height
            self.post_dict["Drives"][keyword]["Length"] = length
            self.post_dict["Drives"][keyword]["Weight"] = weight
            self.post_dict["Drives"][keyword]["Power Spin"] = powerspin
            self.post_dict["Drives"][keyword]["Power Seek"] = powerseek
            self.post_dict["Drives"][keyword]["Power Idle"] = poweridle
            self.post_dict["Drives"][keyword]["Power Standby"] = powerstan
            self.post_dict["Drives"][keyword]["Inspection Date"] = inspection
            self.post_dict["Drives"][keyword]["Type"] = drivetype
        # < Optical Device Information
        self.post_dict["Optical Device"] = {}
        self.post_dict["Optical Device"]["State"] = nbSummary.otherOptical.get_active_text()
        for iter_ in range(1, infocollector.cdrom_Dict["Collected"]["No"]):
            keyword = str(iter_) + " Device"
            serial = infocollector.cdrom_Dict["GUI"][keyword]["SN"].get_text()
            model = infocollector.cdrom_Dict["GUI"][keyword]["Model"].get_text()

            if keyword not in self.post_dict["Optical Device"]:
                self.post_dict["Optical Device"][keyword] = {}

            self.post_dict["Optical Device"][keyword]["Serial"] = serial
            self.post_dict["Optical Device"][keyword]["Model"] = model
        # < Batteries Information
        for iter_ in range(1, infocollector.battery_Dict["Collected"]["No"]):
            if iter_ == 1:
                self.post_dict["Batteries"] = {}
            keyword = str(iter_) + " Battery"
            serial = infocollector.battery_Dict["GUI"][keyword]["SN"].get_text()
            model = infocollector.battery_Dict["GUI"][keyword]["Model"].get_text()
            estimated = infocollector.battery_Dict["GUI"][keyword]["Estimated"].get_text()
            current_wh = infocollector.battery_Dict["Collected"][keyword]["Current Wh"]
            maximum_wh = infocollector.battery_Dict["Collected"][keyword]["Maximum Wh"]
            factory_wh = infocollector.battery_Dict["Collected"][keyword]["Factory Wh"]
            wear_level = infocollector.battery_Dict["Collected"][keyword]["Wear Level"]

            if keyword not in self.post_dict["Batteries"]:
                self.post_dict["Batteries"][keyword] = {}

            self.post_dict["Batteries"][keyword]["Serial"] = serial
            self.post_dict["Batteries"][keyword]["Model"] = model
            self.post_dict["Batteries"][keyword]["Estimated"] = estimated
            self.post_dict["Batteries"][keyword]["Current Wh"] = current_wh
            self.post_dict["Batteries"][keyword]["Maximum Wh"] = maximum_wh
            self.post_dict["Batteries"][keyword]["Factory Wh"] = factory_wh
            self.post_dict["Batteries"][keyword]["Wear Level"] = wear_level
        # < Observation Information
        self.post_dict["Observations"]["Add. comment"] = guiTemplate.get_multiline_text(nbObservations.obsNotes)
        nbObservations.sort_obs_codes()
        self.post_dict["Observations"] = nbObservations.selectedObs
        # < Other Information
        self.post_dict["Others"] = {}
        self.post_dict["Others"]["License"] = nbSummary.otherLicense.get_active_text()
        self.post_dict["Others"]["Box number"] = int(nbSummary.destinationBox.get_value())
        # < Order Information
        if infocollector.order_Name:
            self.post_dict["Order"] = {}
            self.post_dict["Order"]["Status"] = nbOrder.status_entry.get_active_text()
            self.post_dict["Order"]["Add. notes"] = guiTemplate.get_multiline_text(nbOrder.add_order_notes)

    def throw_file_chooser_window(self):
        dialog = Gtk.FileChooserDialog(parent=self, title="Please choose a file", action=Gtk.FileChooserAction.OPEN,
                                       buttons=(
                                           Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                                           Gtk.ResponseType.OK))
        preview = Gtk.Image()
        dialog.set_select_multiple(True)
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', self.update_preview_cb, preview, dialog)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Images")
        file_filter.add_mime_type("image/png")
        file_filter.add_mime_type("image/jpeg")
        file_filter.add_mime_type("image/gif")
        file_filter.add_pattern("*.[pP][nN][gG]")
        file_filter.add_pattern("*.[jJ][pP][eE]?[gG]")
        file_filter.add_pattern("*.[gG][iI][fF]")
        file_filter.add_pattern("*.[tT][iI][fF]{1,2}")
        file_filter.add_pattern("*.[xX][pP][mM]")
        dialog.add_filter(file_filter)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for filename in dialog.get_filenames():
                if filename in infocollector.pictures:
                    guiTemplate.throw_error_win(self, "Error", "File you choosed is already included!")
                else:
                    infocollector.pictures.append(filename)
                    self.reload_picture_gallery()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return False
        dialog.destroy()
        return False

    @staticmethod
    def update_preview_cb(_file_chooser, preview, dialog):
        path = dialog.get_preview_filename()
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path))
            # scale the image
            max_width, max_height = 300.0, 700.0
            width = pixbuf.get_width()
            height = pixbuf.get_height()
            scale = min(max_width / width, max_height / height)
            if scale < 2:
                width, height = int(width * scale), int(height * scale)
                pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

                preview.set_from_pixbuf(pixbuf)
            dialog.set_preview_widget_active(True)
        except GLib.GError:
            dialog.set_preview_widget_active(False)


infocollector = InfoCollector()
guiTemplate = GUITemplate(infocollector)
events = Events()
nbSummary = NBSummary(guiTemplate, infocollector)
nbTests = NBTests(guiTemplate, infocollector, events)
nbObservations = NBObservations(guiTemplate, infocollector)
nbStress = NBStress(guiTemplate, infocollector)
nbOrder = NBOrder(guiTemplate, infocollector)

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
# win.close()

# Hide all toggleable boxes
if isinstance(nbSummary.togIDBox, Gtk.Box):
    nbSummary.togIDBox.hide()
if isinstance(nbSummary.togCPUBox, Gtk.Box):
    nbSummary.togCPUBox.hide()
if isinstance(nbSummary.togRAMBox, Gtk.Box):
    nbSummary.togRAMBox.hide()
if isinstance(nbSummary.togGPUBox, Gtk.Box):
    nbSummary.togGPUBox.hide()
if isinstance(nbSummary.togBATBox, Gtk.Box):
    nbSummary.togBATBox.hide()
if isinstance(nbSummary.togDriveBox, Gtk.Box):
    nbSummary.togDriveBox.hide()
if isinstance(nbSummary.togOtherBox, Gtk.Box):
    nbSummary.togOtherBox.hide()
if isinstance(nbSummary.togDisplayBox, Gtk.Box):
    nbSummary.togDisplayBox.hide()

infocollector.debug_info("Information", "Application was launched!")
Gtk.main()
