import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class NBSummary:
    def __init__(self, gui_base, infocollector):
        self.gui_base = gui_base
        self.infocollector = infocollector

        self.togBooleans = dict()
        self.togBooleans["CPU"] = {}
        self.togBooleans["CPU"]["Bool"] = False
        self.togBooleans["GPU"] = {}
        self.togBooleans["GPU"]["Bool"] = False
        self.togBooleans["RAM"] = {}
        self.togBooleans["RAM"]["Bool"] = False
        self.togBooleans["BAT"] = {}
        self.togBooleans["BAT"]["Bool"] = False
        self.togBooleans["ID"] = {}
        self.togBooleans["ID"]["Bool"] = False
        self.togBooleans["Drive"] = {}
        self.togBooleans["Drive"]["Bool"] = False
        self.togBooleans["Display"] = {}
        self.togBooleans["Display"]["Bool"] = False
        self.togBooleans["Other"] = {}
        self.togBooleans["Other"]["Bool"] = False

        self.page_box = None
        self.destinationRack = None
        self.destinationBox = None

        self.otherCamera = None
        self.otherLicense = None
        self.otherOptical = None

        self.lastTester = None  # Last  Tester (Static - Non Changable after Assigning)
        self.tester = None  # Current Tester (Selective from DropBox)
        self.currentBatch = None  # Initial Computer Category
        self.category = None  # Computer Category, which can be changed later
        self.togIDBox = None  # System Main Box
        self.togIDBttn = None  # System Toggable Button
        self.togCPUBttn = None  # Processor Main Box
        self.togCPUBox = None  # Processor Toggable Button
        self.togRAMBox = None  # RAM Main Box
        self.togRAMBttn = None  # RAM Toggable Button
        self.togGPUBox = None  # GPU Main Box
        self.togGPUBttn = None  # GPU Toggable Button
        self.togBATBox = None  # Battery Main Box
        self.togBATBttn = None  # Battery Toggable Button
        self.togDriveBox = None  # Drive Main Box
        self.togDriveBttn = None  # Drive Toggable Button
        self.togOtherBox = None  # Other Main Box
        self.togOtherBttn = None  # Other Toggable Button
        self.togDisplayBox = None  # Display Main Box
        self.togDisplayBttn = None  # Display Toggable Button
        self.infocollector.debug_info("Information", "Summary NB - Variables Initilizated")

    def create_page(self):
        self.page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, border_width=5)
        # Main Horizontal Box Wrapper
        main_h_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)

        info_columnn_sb1 = self.gui_base.create_scrolling_box()
        info_column_box1 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.create_product_info_1(info_column_box1)
        info_columnn_sb1.add(info_column_box1)

        info_columnn_sb2 = self.gui_base.create_scrolling_box()
        info_column_box2 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.create_product_info_2(info_column_box2)
        info_columnn_sb2.add(info_column_box2)

        main_h_wrapper.pack_start(info_columnn_sb1, True, True, 0)
        main_h_wrapper.pack_start(info_columnn_sb2, True, True, 0)
        self.page_box.pack_start(main_h_wrapper, True, True, 0)

    def create_product_info_1(self, column_box):
        self.infocollector.debug_info("Information", "First  Column Creation")
        column_wrapper = Gtk.Box()
        computer_v_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        self.create_tester_info(computer_v_box)
        self.create_sys_info_short(computer_v_box)
        self.create_cpu_info_short(computer_v_box)
        self.create_ram_info_short(computer_v_box)
        self.create_gpu_info_short(computer_v_box)
        self.create_battery_info_short(computer_v_box)

        column_wrapper.pack_start(computer_v_box, False, False, 0)
        column_box.pack_start(column_wrapper, False, False, 10)
        self.infocollector.debug_info("Information", "First  Column Created")

    def create_product_info_2(self, column_box):
        self.infocollector.debug_info("Information", "Second Column Creation")
        column_wrapper = Gtk.Box()
        computer_v_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)

        self.create_category_info(computer_v_box)
        self.create_display_info_short(computer_v_box)
        self.create_drive_info_short(computer_v_box)
        self.create_other_info_short(computer_v_box)

        column_wrapper.pack_start(computer_v_box, False, False, 0)
        column_box.pack_start(column_wrapper, False, False, 10)
        self.infocollector.debug_info("Information", "Second Column Created")

    # <- Short Information Functions
    def create_tester_info(self, box):
        self.lastTester = self.gui_base.create_entry(self.infocollector.previousTester, False)
        self.gui_base.create_label_entry_box("Last tester", self.lastTester, box)
        tester_box, tester_label, self.tester = self.gui_base.create_label_dropbox("Tester",
                                                                                   self.infocollector.avail_testers,
                                                                                   value_boolean=False)
        tester_box.pack_start(tester_label, True, True, 0)
        tester_box.pack_start(self.tester, True, True, 0)
        box.pack_start(tester_box, True, True, 0)

        self.gui_base.create_separator(box)
        rack_box = Gtk.Box(homogeneous=True)
        rack_label = Gtk.Label("Rack")
        self.destinationRack = self.gui_base.create_spin_button(1, 1, 10000)
        self.destinationRack.set_numeric(True)
        self.destinationRack.set_sensitive(False)
        rack_box.pack_start(rack_label, True, True, 0)
        rack_box.pack_start(self.destinationRack, True, True, 0)
        box.pack_start(rack_box, True, True, 0)

        self.gui_base.create_separator(box)
        self.gui_base.create_label('', box)

    def create_category_info(self, box):
        if self.infocollector.assignedBatch:
            box1, label, self.currentBatch = self.gui_base.create_label_dropbox("Batch",
                                                                                self.infocollector.assignedBatch,
                                                                                value_boolean=True, is_enabled=False)
        else:
            box1, label, self.currentBatch = self.gui_base.create_label_dropbox("Batches",
                                                                                self.infocollector.avail_Batches,
                                                                                value_boolean=False)
        box1.pack_start(label, True, True, 0)
        box1.pack_start(self.currentBatch, True, True, 0)
        box.pack_start(box1, True, True, 0)
        self.gui_base.create_separator(box)

        cat_box, cat_label, self.category = self.gui_base.create_label_dropbox("Category",
                                                                               self.infocollector.avail_Categories,
                                                                               specific_value=self.infocollector.assignedCategory,
                                                                               value_boolean=False)
        cat_box.pack_start(cat_label, True, True, 0)
        cat_box.pack_start(self.category, True, True, 0)
        box.pack_start(cat_box, True, True, 0)
        self.gui_base.create_separator(box)

        box_box = Gtk.Box(homogeneous=True)
        box_label = Gtk.Label("Box No")
        self.destinationBox = self.gui_base.create_spin_button(0, 0, 10000)
        self.destinationBox.set_numeric(True)
        self.destinationBox.set_digits(0)
        if self.infocollector.boxNumber:
            self.destinationBox.set_value(self.infocollector.boxNumber)
        box_box.pack_start(box_label, True, True, 0)
        box_box.pack_start(self.destinationBox, True, True, 0)
        box.pack_start(box_box, True, True, 0)

        self.gui_base.create_separator(box)
        self.gui_base.create_label('', box)

    def create_sys_info_short(self, box):
        self.togIDBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'ID', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Device Identification", self.togIDBttn)

        self.togIDBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_sys_info_extended(self.togIDBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - Identification")

        box.pack_start(self.togIDBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_cpu_info_short(self, box):
        self.togCPUBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'CPU', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Processor (-s) Information", self.togCPUBttn)

        self.togCPUBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_cpu_info_extended(self.togCPUBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - Processor")

        box.pack_start(self.togCPUBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_ram_info_short(self, box):
        self.togRAMBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'RAM', self.togBooleans)
        self.gui_base.create_label_button_box(box, "RAM (-s) Information", self.togRAMBttn)

        self.togRAMBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_ram_info_extended(self.togRAMBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - RAM")

        box.pack_start(self.togRAMBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_gpu_info_short(self, box):
        self.togGPUBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'GPU', self.togBooleans)
        self.gui_base.create_label_button_box(box, "GPU (-s) Information", self.togGPUBttn)

        self.togGPUBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_gpu_info_extended(self.togGPUBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - GPU")

        box.pack_start(self.togGPUBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_drive_info_short(self, box):
        self.togDriveBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'Drive', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Device Drive (-s) Information", self.togDriveBttn)

        self.togDriveBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.create_drive_info_extended(self.togDriveBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 2 - Drive")

        box.pack_start(self.togDriveBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_other_info_short(self, box):
        self.togOtherBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'Other', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Other (-s)", self.togOtherBttn)

        self.togOtherBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.create_other_info_extended(self.togOtherBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 2 - Other")

        box.pack_start(self.togOtherBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_battery_info_short(self, box):
        self.togBATBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'BAT', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Batter (-y /-ies) Information", self.togBATBttn)

        self.togBATBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_battery_info_extended(self.togBATBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - Batteries")

        box.pack_start(self.togBATBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_display_info_short(self, box):
        self.togDisplayBttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'Display',
                                                                     self.togBooleans)
        self.gui_base.create_label_button_box(box, "Screen Information", self.togDisplayBttn)

        self.togDisplayBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.create_display_info_extended(self.togDisplayBox)
        self.infocollector.debug_info("Information", "Summary Page - Info 2 - Display")

        box.pack_start(self.togDisplayBox, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    # <- Extended Information Functions
    def create_sys_info_extended(self, box):
        self.togBooleans['ID']['Box'] = box
        self.infocollector.id_Dict["GUI"]["Serial"] = self.gui_base.create_entry(
            self.infocollector.id_Dict["Collected"]["Serial"])
        self.infocollector.id_Dict["GUI"]["MB Serial"] = self.gui_base.create_entry(
            self.infocollector.id_Dict["Collected"]["MB Serial"])
        self.infocollector.id_Dict["GUI"]["Manufacturer"] = self.gui_base.create_entry(
            self.infocollector.id_Dict["Collected"]["Manufacturer"])
        self.infocollector.id_Dict["GUI"]["Model"] = self.gui_base.create_entry(
            self.infocollector.id_Dict["Collected"]["Model"])
        self.infocollector.id_Dict["GUI"]["System Type"] = self.gui_base.create_entry(
            self.infocollector.id_Dict["Collected"]["System Type"])

        self.gui_base.create_label_entry_box("Serial", self.infocollector.id_Dict["GUI"]["Serial"], box)
        self.gui_base.create_label_entry_box("MB Serial", self.infocollector.id_Dict["GUI"]["MB Serial"], box)
        self.gui_base.create_label_entry_box("Manufacturer", self.infocollector.id_Dict["GUI"]["Manufacturer"], box)
        self.gui_base.create_label_entry_box("Model", self.infocollector.id_Dict["GUI"]["Model"], box)
        self.gui_base.create_label_entry_box("System Type", self.infocollector.id_Dict["GUI"]["System Type"], box)
        box.show_all()

    def create_cpu_info_extended(self, box):
        self.togBooleans['CPU']['Box'] = box
        self.infocollector.cpu_Dict["GUI"]["Manufacturer"] = self.gui_base.create_entry(
            self.infocollector.cpu_Dict["Collected"]["Manufacturer"])
        self.infocollector.cpu_Dict["GUI"]["Model"] = self.gui_base.create_entry(
            self.infocollector.cpu_Dict["Collected"]["Model"])
        self.infocollector.cpu_Dict["GUI"]["Stock Clock"] = self.gui_base.create_entry(
            self.infocollector.cpu_Dict["Collected"]["Stock Clock"])
        self.infocollector.cpu_Dict["GUI"]["Maximum Clock"] = self.gui_base.create_entry(
            self.infocollector.cpu_Dict["Collected"]["Maximum Clock"])
        self.infocollector.cpu_Dict["GUI"]["Core Amount"] = self.gui_base.create_entry(
            self.infocollector.cpu_Dict["Collected"]["Core Amount"])
        self.infocollector.cpu_Dict["GUI"]["Thread Amount"] = self.gui_base.create_entry(
            self.infocollector.cpu_Dict["Collected"]["Thread Amount"])

        self.gui_base.create_label_entry_box("CPU Manufacturer", self.infocollector.cpu_Dict["GUI"]["Manufacturer"],
                                             box)
        self.gui_base.create_label_entry_box("CPU Model", self.infocollector.cpu_Dict["GUI"]["Model"], box)
        self.gui_base.create_label_entry_box("Stock CPU Clock", self.infocollector.cpu_Dict["GUI"]["Stock Clock"], box)
        self.gui_base.create_label_entry_box("MAX CPU Clock", self.infocollector.cpu_Dict["GUI"]["Maximum Clock"], box)
        self.gui_base.create_label_entry_box("CPU Cores", self.infocollector.cpu_Dict["GUI"]["Core Amount"], box)
        self.gui_base.create_label_entry_box("CPU Threads", self.infocollector.cpu_Dict["GUI"]["Thread Amount"], box)
        box.show_all()

    def create_ram_info_extended(self, box):
        self.togBooleans['RAM']['Box'] = box
        self.infocollector.ram_Dict["GUI"]['Total'] = self.gui_base.create_entry(
            self.infocollector.ram_Dict["Collected"]["Total Amount"])
        self.infocollector.ram_Dict["GUI"]['Type'] = self.gui_base.create_entry(
            self.infocollector.ram_Dict["Collected"]["Type"])

        self.gui_base.create_label_entry_box("Total", self.infocollector.ram_Dict["GUI"]['Total'], box)
        self.gui_base.create_label_entry_box("Type", self.infocollector.ram_Dict["GUI"]['Type'], box)
        self.gui_base.create_label('', box)

        for iter_ in range(1, self.infocollector.ram_Dict["Collected"]["No"]):
            if iter_ > 1:
                self.gui_base.create_label('', box)

            keyword = str(iter_) + " Stick"
            if keyword not in self.infocollector.ram_Dict["GUI"]:
                self.infocollector.ram_Dict["GUI"][keyword] = {}

            self.infocollector.ram_Dict["GUI"][keyword]["Serial"] = self.gui_base.create_entry(
                self.infocollector.ram_Dict["Collected"][keyword]["Serial"])
            self.infocollector.ram_Dict["GUI"][keyword]["Product"] = self.gui_base.create_entry(
                self.infocollector.ram_Dict["Collected"][keyword]["Product"])
            self.infocollector.ram_Dict["GUI"][keyword]["Size"] = self.gui_base.create_entry(
                self.infocollector.ram_Dict["Collected"][keyword]["Size"])
            self.infocollector.ram_Dict["GUI"][keyword]["Clock"] = self.gui_base.create_entry(
                self.infocollector.ram_Dict["Collected"][keyword]["Clock"])
            self.gui_base.create_label_entry_box("Serial", self.infocollector.ram_Dict["GUI"][keyword]["Serial"], box)
            self.gui_base.create_label_entry_box("Model", self.infocollector.ram_Dict["GUI"][keyword]["Product"], box)
            self.gui_base.create_label_entry_box("Size", self.infocollector.ram_Dict["GUI"][keyword]["Size"], box)
            self.gui_base.create_label_entry_box("Clock", self.infocollector.ram_Dict["GUI"][keyword]["Clock"], box)
        box.show_all()

    def create_gpu_info_extended(self, box):
        self.togBooleans['GPU']['Box'] = box
        self.infocollector.gpu_Dict["GUI"]["1 Manufacturer"] = self.gui_base.create_entry(
            self.infocollector.gpu_Dict["Collected"]["1 Manufacturer"])
        self.infocollector.gpu_Dict["GUI"]["1 Model"] = self.gui_base.create_entry(
            self.infocollector.gpu_Dict["Collected"]["1 Model"])
        self.infocollector.gpu_Dict["GUI"]["2 Manufacturer"] = self.gui_base.create_entry(
            self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"])
        self.infocollector.gpu_Dict["GUI"]["2 Model"] = self.gui_base.create_entry(
            self.infocollector.gpu_Dict["Collected"]["2 Model"])

        self.gui_base.create_label_entry_box("iGPU Manufacturer", self.infocollector.gpu_Dict["GUI"]["1 Manufacturer"],
                                             box)
        self.gui_base.create_label_entry_box("iGPU Model", self.infocollector.gpu_Dict["GUI"]["1 Model"], box)
        self.gui_base.create_label('', box)
        self.gui_base.create_label_entry_box("dGPU Manufacturer", self.infocollector.gpu_Dict["GUI"]["2 Manufacturer"],
                                             box)
        self.gui_base.create_label_entry_box("dGPU Model", self.infocollector.gpu_Dict["GUI"]["2 Model"], box)
        box.show_all()

    def create_drive_info_extended(self, box):
        self.togBooleans['Drive']['Box'] = box
        for iter_ in range(1, self.infocollector.drive_Dict["Collected"]["No"]):
            if iter_ > 1:
                self.gui_base.create_label('', box)

            keyword = str(iter_) + " Drive"
            if keyword not in self.infocollector.drive_Dict["GUI"]:
                self.infocollector.drive_Dict["GUI"][keyword] = {}

            self.infocollector.drive_Dict["GUI"][keyword]["SN"] = self.gui_base.create_entry(
                self.infocollector.drive_Dict["Collected"][keyword]["SN"])
            self.infocollector.drive_Dict["GUI"][keyword]["Manufacturer"] = self.gui_base.create_entry(
                self.infocollector.drive_Dict["Collected"][keyword]["Manufacturer"])
            self.infocollector.drive_Dict["GUI"][keyword]["Model"] = self.gui_base.create_entry(
                self.infocollector.drive_Dict["Collected"][keyword]["Model"])
            self.infocollector.drive_Dict["GUI"][keyword]["Interface"] = self.gui_base.create_entry(
                self.infocollector.drive_Dict["Collected"][keyword]["Interface"])
            self.infocollector.drive_Dict["GUI"][keyword]["Capacity"] = self.gui_base.create_entry(
                self.infocollector.drive_Dict["Collected"][keyword]["Capacity"])
            self.infocollector.drive_Dict["GUI"][keyword]["Health"] = self.gui_base.create_entry(
                self.infocollector.drive_Dict["Collected"][keyword]["Health"])
            self.infocollector.drive_Dict["GUI"][keyword]["Description"] = \
                self.infocollector.drive_Dict["Collected"][keyword]["Description"]

            self.gui_base.create_label_entry_box("Serial", self.infocollector.drive_Dict["GUI"][keyword]["SN"], box)
            self.gui_base.create_label_entry_box("Vendor",
                                                 self.infocollector.drive_Dict["GUI"][keyword]["Manufacturer"], box)
            self.gui_base.create_label_entry_box("Model", self.infocollector.drive_Dict["GUI"][keyword]["Model"], box)
            self.gui_base.create_label_entry_box("Interface",
                                                 self.infocollector.drive_Dict["GUI"][keyword]["Interface"], box)
            self.gui_base.create_label_entry_box("Capacity", self.infocollector.drive_Dict["GUI"][keyword]["Capacity"],
                                                 box)
            self.gui_base.create_label_entry_box("Health", self.infocollector.drive_Dict["GUI"][keyword]["Health"],
                                                 box, self.infocollector.drive_Dict["GUI"][keyword]["Description"])
        box.show_all()

    def create_other_info_extended(self, box):
        self.togBooleans['Other']['Box'] = box

        box1, camera_label, self.otherCamera = self.gui_base.create_label_dropbox("Camera",
                                                                                  self.infocollector.avail_CameraOptions,
                                                                                  value_boolean=self.infocollector.isCameraDetected)
        box2, license_label, self.otherLicense = self.gui_base.create_label_dropbox("License",
                                                                                    self.infocollector.avail_Licenses,
                                                                                    specific_value=self.infocollector.deviceLicense)
        box3, optical_label, self.otherOptical = self.gui_base.create_label_dropbox("Optical Device",
                                                                                    self.infocollector.avail_CDROMOptions,
                                                                                    value_boolean=self.infocollector.isCDROMDetected)
        if self.infocollector.id_Dict["GUI"]["System Type"].get_text() == "Desktop":
            self.otherCamera.set_active(1)

        box1.pack_start(camera_label, True, True, 0)
        box1.pack_start(self.otherCamera, True, True, 0)
        box2.pack_start(license_label, True, True, 0)
        box2.pack_start(self.otherLicense, True, True, 0)
        box3.pack_start(optical_label, True, True, 0)
        box3.pack_start(self.otherOptical, True, True, 0)

        box.pack_start(box1, True, True, 0)
        box.pack_start(box2, True, True, 0)
        box.pack_start(box3, True, True, 0)

        for iter_ in range(1, self.infocollector.cdrom_Dict["Collected"]["No"]):
            if iter_ > 1:
                self.gui_base.create_label('', box)

            keyword = str(iter_) + " Device"
            if keyword not in self.infocollector.cdrom_Dict["GUI"]:
                self.infocollector.cdrom_Dict["GUI"][keyword] = {}

            self.infocollector.cdrom_Dict["GUI"][keyword]["SN"] = self.gui_base.create_entry(
                self.infocollector.cdrom_Dict["Collected"][keyword]["SN"])
            self.infocollector.cdrom_Dict["GUI"][keyword]["Model"] = self.gui_base.create_entry(
                self.infocollector.cdrom_Dict["Collected"][keyword]["Model"])

            self.gui_base.create_label_entry_box("Serial", self.infocollector.cdrom_Dict["GUI"][keyword]["SN"], box)
            self.gui_base.create_label_entry_box("Model", self.infocollector.cdrom_Dict["GUI"][keyword]["Model"], box)
            self.gui_base.create_separator(box, 'horizontal')
        box.show_all()

    def create_battery_info_extended(self, box):
        self.togBooleans['BAT']['Box'] = box
        for iter_ in range(0, len(self.infocollector.battery_Dict["Collected"]["Names"])):
            if iter_ > 0:
                self.gui_base.create_label('', box)

            gui_keyword = str(iter_) + " Battery"
            ic_keyword = self.infocollector.battery_Dict["Collected"]["Names"][iter_]
            if gui_keyword not in self.infocollector.battery_Dict["GUI"]:
                self.infocollector.battery_Dict["GUI"][gui_keyword] = {}

            self.infocollector.battery_Dict["GUI"][gui_keyword]["SN"] = self.gui_base.create_entry(
                self.infocollector.battery_Dict["Collected"][ic_keyword]["Serial"])
            self.infocollector.battery_Dict["GUI"][gui_keyword]["Model"] = self.gui_base.create_entry(
                self.infocollector.battery_Dict["Collected"][ic_keyword]["Model"])
            self.infocollector.battery_Dict["GUI"][gui_keyword]["Estimated"] = self.gui_base.create_entry(
                self.infocollector.battery_Dict["Collected"][ic_keyword]["Estimated"])

            max_energy = self.infocollector.battery_Dict["Collected"][ic_keyword]["Maximum Wh"]
            max_factory = self.infocollector.battery_Dict["Collected"][ic_keyword]["Factory Wh"]
            wearlevel = self.infocollector.battery_Dict["Collected"][ic_keyword]["Wear Level"]
            tooltip = "Current / Factory\n" + str(max_energy) + " / " + str(max_factory) + "\n\nWear level: " + str(
                wearlevel)

            self.gui_base.create_label_entry_box("Serial", self.infocollector.battery_Dict["GUI"][gui_keyword]["SN"],
                                                 box)
            self.gui_base.create_label_entry_box("Model", self.infocollector.battery_Dict["GUI"][gui_keyword]["Model"],
                                                 box)
            self.gui_base.create_label_entry_box("Estimated Time",
                                                 self.infocollector.battery_Dict["GUI"][gui_keyword]["Estimated"], box,
                                                 tooltip)
        box.show_all()

    def create_display_info_extended(self, box):
        self.togBooleans['Display']['Box'] = box

        self.infocollector.screen_Dict["GUI"]["Diagonal"] = self.gui_base.create_entry(
            self.infocollector.screen_Dict["Collected"]["Diagonal"])
        self.infocollector.screen_Dict["GUI"]["Resolution"] = self.gui_base.create_entry(
            self.infocollector.screen_Dict["Collected"]["Resolution"])
        self.infocollector.screen_Dict["GUI"]["Category"] = self.gui_base.create_entry(
            self.infocollector.screen_Dict["Collected"]["Category"])
        self.infocollector.screen_Dict["GUI"]["Connection Type"] = self.gui_base.create_entry(
            self.infocollector.screen_Dict["Collected"]["Connection Type"])

        self.gui_base.create_label_entry_box("Diagonal", self.infocollector.screen_Dict["GUI"]["Diagonal"], box)
        self.gui_base.create_label_entry_box("Resolution", self.infocollector.screen_Dict["GUI"]["Resolution"], box)
        self.gui_base.create_label_entry_box("Category", self.infocollector.screen_Dict["GUI"]["Category"], box)
        self.gui_base.create_label_entry_box("Connection Type",
                                             self.infocollector.screen_Dict["GUI"]["Connection Type"], box)

        if self.infocollector.id_Dict["GUI"]["System Type"].get_text() == "Desktop":
            self.infocollector.screen_Dict["GUI"]["Diagonal"].set_text("N/A")
            self.infocollector.screen_Dict["GUI"]["Resolution"].set_text("N/A")
            self.infocollector.screen_Dict["GUI"]["Category"].set_text("N/A")
            self.infocollector.screen_Dict["GUI"]["Connection Type"].set_text("N/A")
        box.show_all()

        # <- Other Functions

    def toggle_field(self, _button, field):
        if self.togBooleans[field]['Bool']:
            self.togBooleans[field]['Box'].hide()
            self.togBooleans[field]['Button'].set_label("Show")
            self.togBooleans[field]['Bool'] = False
        else:
            self.togBooleans[field]['Box'].show()
            self.togBooleans[field]['Button'].set_label("Hide")
            self.togBooleans[field]['Bool'] = True
