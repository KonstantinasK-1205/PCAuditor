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
        self.dest_rack = None
        self.dest_box = None

        self.sys_form_factor = None
        self.camera_dropbox = None
        self.license_dropbox = None
        self.optical_dropbox = None

        self.last_tester = None  # Last  Tester (Static - Non Changable after Assigning)
        self.tester = None  # Current Tester (Selective from DropBox)
        self.current_batch = None  # Initial Computer Category
        self.category = None  # Computer Category, which can be changed later
        self.tog_id_box = None  # System Main Box
        self.tog_id_bttn = None  # System Toggable Button
        self.tog_cpu_box = None  # Processor Toggable Button
        self.tog_cpu_bttn = None  # Processor Main Box
        self.tog_ram_box = None  # RAM Main Box
        self.tog_ram_bttn = None  # RAM Toggable Button
        self.tog_gpu_box = None  # GPU Main Box
        self.tog_gpu_bttn = None  # GPU Toggable Button
        self.tog_bat_box = None  # Battery Main Box
        self.tog_bat_bttn = None  # Battery Toggable Button
        self.tog_drive_box = None  # Drive Main Box
        self.tog_drive_bttn = None  # Drive Toggable Button
        self.tog_other_box = None  # Other Main Box
        self.tog_other_bttn = None  # Other Toggable Button
        self.tog_display_box = None  # Display Main Box
        self.tog_display_bttn = None  # Display Toggable Button
        self.infocollector.debug_info("Information", "Summary NB - Variables Initilizated")

    def create_page(self):
        self.page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, border_width=5)
        # Main Horizontal Box Wrapper
        main_h_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        info_columnn_sb1 = self.gui_base.create_scrolling_box()
        info_column_box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_product_info_1(info_column_box1)
        info_columnn_sb1.add(info_column_box1)

        info_columnn_sb2 = self.gui_base.create_scrolling_box()
        info_column_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_product_info_2(info_column_box2)
        info_columnn_sb2.add(info_column_box2)

        main_h_wrapper.pack_start(info_columnn_sb1, True, True, 0)
        main_h_wrapper.pack_start(info_columnn_sb2, True, True, 0)
        self.page_box.pack_start(main_h_wrapper, True, True, 0)

    def create_product_info_1(self, column_box):
        self.infocollector.debug_info("Information", "First  Column Creation")
        column_wrapper = Gtk.Box()
        computer_v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

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
        computer_v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.create_category_info(computer_v_box)
        self.create_display_info_short(computer_v_box)
        self.create_drive_info_short(computer_v_box)
        self.create_other_info_short(computer_v_box)

        column_wrapper.pack_start(computer_v_box, False, False, 0)
        column_box.pack_start(column_wrapper, False, False, 10)
        self.infocollector.debug_info("Information", "Second Column Created")

    # <- Short Information Functions
    def create_tester_info(self, box):
        self.last_tester = self.gui_base.create_entry(self.infocollector.previousTester, False)
        self.gui_base.create_label_entry_box("Last tester", self.last_tester, box)
        tester_box, tester_label, self.tester = self.gui_base.create_label_dropbox("Tester",
                                                                                   self.infocollector.avail_testers,
                                                                                   _value_boolean=False)
        tester_box.pack_start(tester_label, True, True, 0)
        tester_box.pack_start(self.tester, True, True, 0)
        box.pack_start(tester_box, True, True, 0)

        self.gui_base.create_separator(box)
        rack_box = Gtk.Box(homogeneous=True)
        rack_label = Gtk.Label("Rack")
        self.dest_rack = self.gui_base.create_spin_button(1, 1, 10000)
        self.dest_rack.set_numeric(True)
        self.dest_rack.set_sensitive(False)
        rack_box.pack_start(rack_label, True, True, 0)
        rack_box.pack_start(self.dest_rack, True, True, 0)
        box.pack_start(rack_box, True, True, 0)

        self.gui_base.create_separator(box)
        self.gui_base.create_label('', box)

    def create_category_info(self, box):
        if self.infocollector.assigned_batch:
            self.current_batch = self.gui_base.create_label_dropbox("Batch", self.infocollector.assigned_batch, box,
                                                                    _value_boolean=True, _is_enabled=False,
                                                                    _pack_start=True)
        else:
            self.current_batch = self.gui_base.create_label_dropbox("Batches", self.infocollector.available_batches,
                                                                    box,
                                                                    _value_boolean=False, _pack_start=True)
        self.gui_base.create_separator(box)

        self.category = self.gui_base.create_label_dropbox("Category", self.infocollector.available_categories, box,
                                                           _specific_value=self.infocollector.assigned_category,
                                                           _value_boolean=False, _pack_start=True)
        self.gui_base.create_separator(box)

        box_box = Gtk.Box(homogeneous=True)
        box_label = Gtk.Label("Box No")
        self.dest_box = self.gui_base.create_spin_button(0, 0, 10000)
        self.dest_box.set_numeric(True)
        self.dest_box.set_digits(0)
        if self.infocollector.boxNumber:
            self.dest_box.set_value(self.infocollector.boxNumber)
        box_box.pack_start(box_label, True, True, 0)
        box_box.pack_start(self.dest_box, True, True, 0)
        box.pack_start(box_box, True, True, 0)

        self.gui_base.create_separator(box)
        self.gui_base.create_label('', box)

    def create_sys_info_short(self, box):
        self.tog_id_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'ID', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Device Identification", self.tog_id_bttn)

        self.tog_id_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_sys_info_extended(self.tog_id_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - Identification")

        box.pack_start(self.tog_id_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_cpu_info_short(self, box):
        self.tog_cpu_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'CPU', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Processor (-s) Information", self.tog_cpu_bttn)

        self.tog_cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_cpu_info_extended(self.tog_cpu_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - Processor")

        box.pack_start(self.tog_cpu_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_ram_info_short(self, box):
        self.tog_ram_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'RAM', self.togBooleans)
        self.gui_base.create_label_button_box(box, "RAM (-s) Information", self.tog_ram_bttn)

        self.tog_ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_ram_info_extended(self.tog_ram_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - RAM")

        box.pack_start(self.tog_ram_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_gpu_info_short(self, box):
        self.tog_gpu_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'GPU', self.togBooleans)
        self.gui_base.create_label_button_box(box, "GPU (-s) Information", self.tog_gpu_bttn)

        self.tog_gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_gpu_info_extended(self.tog_gpu_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - GPU")

        box.pack_start(self.tog_gpu_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_drive_info_short(self, box):
        self.tog_drive_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'Drive',
                                                                     self.togBooleans)
        self.gui_base.create_label_button_box(box, "Device Drive (-s) Information", self.tog_drive_bttn)

        self.tog_drive_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_drive_info_extended(self.tog_drive_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 2 - Drive")

        box.pack_start(self.tog_drive_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_other_info_short(self, box):
        self.tog_other_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'Other',
                                                                     self.togBooleans)
        self.gui_base.create_label_button_box(box, "Other (-s)", self.tog_other_bttn)

        self.tog_other_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_other_info_extended(self.tog_other_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 2 - Other")

        box.pack_start(self.tog_other_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_battery_info_short(self, box):
        self.tog_bat_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'BAT', self.togBooleans)
        self.gui_base.create_label_button_box(box, "Batter (-y /-ies) Information", self.tog_bat_bttn)

        self.tog_bat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_battery_info_extended(self.tog_bat_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 1 - Batteries")

        box.pack_start(self.tog_bat_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    def create_display_info_short(self, box):
        self.tog_display_bttn = self.gui_base.create_toggleable_button("Show", self.toggle_field, 'Display',
                                                                       self.togBooleans)
        self.gui_base.create_label_button_box(box, "Screen Information", self.tog_display_bttn)

        self.tog_display_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.create_display_info_extended(self.tog_display_box)
        self.infocollector.debug_info("Information", "Summary Page - Info 2 - Display")

        box.pack_start(self.tog_display_box, False, False, 0)
        self.gui_base.create_separator(box, 'horizontal', 3)

    # <- Extended Information Functions
    def create_sys_info_extended(self, box):
        self.togBooleans['ID']['Box'] = box

        id_gui = self.infocollector.id_Dict["GUI"]
        id_col = self.infocollector.id_Dict["Collected"]
        tpl = self.gui_base

        id_gui["Serial"] = tpl.create_entry(id_col["Serial"])
        id_gui["MB Serial"] = tpl.create_entry(id_col["MB Serial"])
        id_gui["Manufacturer"] = tpl.create_entry(id_col["Manufacturer"])
        id_gui["Model"] = tpl.create_entry(id_col["Model"])
        id_gui["System Type"] = tpl.create_entry_with_signal(id_col["System Type"], _signal='changed',
                                                             _function=self.computer_type_changed)
        if id_gui["System Type"].get_text() == "Laptop":
            sensitive = False
        else:
            sensitive = True
        self.sys_form_factor = tpl.create_label_dropbox("Form Factor",
                                                        self.infocollector.available_ffactor,
                                                        box,
                                                        self.infocollector.assigned_ffactor,
                                                        _is_enabled=sensitive)

        tpl.create_label_entry_box("Serial", id_gui["Serial"], box)
        tpl.create_label_entry_box("MB Serial", id_gui["MB Serial"], box)
        tpl.create_label_entry_box("Manufacturer", id_gui["Manufacturer"], box)
        tpl.create_label_entry_box("Model", id_gui["Model"], box)
        tpl.create_label_entry_box("System Type", id_gui["System Type"], box)
        box.show_all()

    def create_cpu_info_extended(self, box):
        self.togBooleans['CPU']['Box'] = box

        cpu_gui = self.infocollector.cpu_Dict["GUI"]
        cpu_col = self.infocollector.cpu_Dict["Collected"]
        tpl = self.gui_base

        cpu_gui["Manufacturer"] = tpl.create_entry(cpu_col["Manufacturer"])
        cpu_gui["Model"] = tpl.create_entry(cpu_col["Model"])
        cpu_gui["Stock Clock"] = tpl.create_entry(cpu_col["Stock Clock"])
        cpu_gui["Maximum Clock"] = tpl.create_entry(cpu_col["Maximum Clock"])
        cpu_gui["Core Amount"] = tpl.create_entry(cpu_col["Core Amount"])
        cpu_gui["Thread Amount"] = tpl.create_entry(cpu_col["Thread Amount"])

        tpl.create_label_entry_box("CPU Manufacturer", cpu_gui["Manufacturer"], box)
        tpl.create_label_entry_box("CPU Model", cpu_gui["Model"], box)
        tpl.create_label_entry_box("Stock CPU Clock", cpu_gui["Stock Clock"], box)
        tpl.create_label_entry_box("MAX CPU Clock", cpu_gui["Maximum Clock"], box)
        tpl.create_label_entry_box("CPU Cores", cpu_gui["Core Amount"], box)
        tpl.create_label_entry_box("CPU Threads", cpu_gui["Thread Amount"], box)
        box.show_all()

    def create_ram_info_extended(self, box):
        self.togBooleans['RAM']['Box'] = box

        ram_gui = self.infocollector.ram_Dict["GUI"]
        ram_col = self.infocollector.ram_Dict["Collected"]
        tpl = self.gui_base

        ram_gui['Total'] = tpl.create_entry(ram_col["Total Amount"])
        ram_gui['Type'] = tpl.create_entry(ram_col["Type"])

        tpl.create_label_entry_box("Total", ram_gui['Total'], box)
        tpl.create_label_entry_box("Type", ram_gui['Type'], box)
        tpl.create_label('', box)

        for iter_ in range(1, ram_col["No"]):
            if iter_ > 1:
                tpl.create_label('', box)

            keyword = str(iter_) + " Stick"
            if keyword not in ram_gui:
                ram_gui[keyword] = {}

            ram_gui[keyword]["Serial"] = tpl.create_entry(ram_col[keyword]["Serial"])
            ram_gui[keyword]["Product"] = tpl.create_entry(ram_col[keyword]["Product"])
            ram_gui[keyword]["Size"] = tpl.create_entry(ram_col[keyword]["Size"])
            ram_gui[keyword]["Clock"] = tpl.create_entry(ram_col[keyword]["Clock"])

            tpl.create_label_entry_box("Serial", ram_gui[keyword]["Serial"], box)
            tpl.create_label_entry_box("Model", ram_gui[keyword]["Product"], box)
            tpl.create_label_entry_box("Size", ram_gui[keyword]["Size"], box)
            tpl.create_label_entry_box("Clock", ram_gui[keyword]["Clock"], box)
        box.show_all()

    def create_gpu_info_extended(self, box):
        self.togBooleans['GPU']['Box'] = box

        gpu_gui = self.infocollector.gpu_Dict["GUI"]
        gpu_col = self.infocollector.gpu_Dict["Collected"]
        tpl = self.gui_base

        gpu_gui["1 Manufacturer"] = tpl.create_entry(gpu_col["1 Manufacturer"])
        gpu_gui["1 Model"] = tpl.create_entry(gpu_col["1 Model"])
        gpu_gui["2 Manufacturer"] = tpl.create_entry(gpu_col["2 Manufacturer"])
        gpu_gui["2 Model"] = tpl.create_entry(gpu_col["2 Model"])

        tpl.create_label_entry_box("iGPU Manufacturer", gpu_gui["1 Manufacturer"], box)
        tpl.create_label_entry_box("iGPU Model", gpu_gui["1 Model"], box)
        tpl.create_label('', box)

        tpl.create_label_entry_box("dGPU Manufacturer", gpu_gui["2 Manufacturer"], box)
        tpl.create_label_entry_box("dGPU Model", gpu_gui["2 Model"], box)

        box.show_all()

    def create_drive_info_extended(self, box):
        self.togBooleans['Drive']['Box'] = box

        drive_gui = self.infocollector.drive_Dict["GUI"]
        drive_col = self.infocollector.drive_Dict["Collected"]
        tpl = self.gui_base

        for iter_ in range(1, drive_col["No"]):
            if iter_ > 1:
                tpl.create_label('', box)

            keyword = str(iter_) + " Drive"
            if keyword not in drive_gui:
                drive_gui[keyword] = {}

            drive_gui[keyword]["SN"] = tpl.create_entry(drive_col[keyword]["SN"])
            drive_gui[keyword]["Manufacturer"] = tpl.create_entry(drive_col[keyword]["Manufacturer"])
            drive_gui[keyword]["Model"] = tpl.create_entry(drive_col[keyword]["Model"])
            drive_gui[keyword]["Interface"] = tpl.create_entry(drive_col[keyword]["Interface"])
            drive_gui[keyword]["Capacity"] = tpl.create_entry(drive_col[keyword]["Capacity"])
            drive_gui[keyword]["Health"] = tpl.create_entry(drive_col[keyword]["Health"])
            drive_gui[keyword]["Description"] = drive_col[keyword]["Description"]

            tpl.create_label_entry_box("Serial", drive_gui[keyword]["SN"], box)
            tpl.create_label_entry_box("Vendor", drive_gui[keyword]["Manufacturer"], box)
            tpl.create_label_entry_box("Model", drive_gui[keyword]["Model"], box)
            tpl.create_label_entry_box("Interface", drive_gui[keyword]["Interface"], box)
            tpl.create_label_entry_box("Capacity", drive_gui[keyword]["Capacity"], box)
            tpl.create_label_entry_box("Health", drive_gui[keyword]["Health"], box, drive_gui[keyword]["Description"])

        box.show_all()

    def create_other_info_extended(self, box):
        self.togBooleans['Other']['Box'] = box

        cd_gui = self.infocollector.cdrom_Dict["GUI"]
        cd_col = self.infocollector.cdrom_Dict["Collected"]
        tpl = self.gui_base

        self.camera_dropbox = tpl.create_label_dropbox("Camera",
                                                       self.infocollector.avail_CameraOptions, box,
                                                       _value_boolean=self.infocollector.isCameraDetected)
        self.license_dropbox = tpl.create_label_dropbox("License",
                                                        self.infocollector.avail_Licenses, box,
                                                        _specific_value=self.infocollector.deviceLicense)
        self.optical_dropbox = tpl.create_label_dropbox("Optical Device",
                                                        self.infocollector.avail_CDROMOptions, box,
                                                        _value_boolean=self.infocollector.isCDROMDetected)

        if self.infocollector.id_Dict["Collected"]["System Type"] == "Desktop":
            self.camera_dropbox.set_active(1)

        for iter_ in range(1, cd_col["No"]):
            if iter_ > 1:
                tpl.create_label('', box)

            keyword = str(iter_) + " Device"
            if keyword not in cd_gui:
                cd_gui[keyword] = {}

            cd_gui[keyword]["SN"] = tpl.create_entry(cd_col[keyword]["SN"])
            cd_gui[keyword]["Model"] = tpl.create_entry(cd_col[keyword]["Model"])

            tpl.create_label_entry_box("Serial", cd_gui[keyword]["SN"], box)
            tpl.create_label_entry_box("Model", cd_gui[keyword]["Model"], box)
            tpl.create_separator(box, 'horizontal')

        box.show_all()

    def create_battery_info_extended(self, box):
        self.togBooleans['BAT']['Box'] = box

        bat_gui = self.infocollector.battery_Dict["GUI"]
        bat_col = self.infocollector.battery_Dict["Collected"]
        tpl = self.gui_base

        for iter_ in range(0, len(bat_col["Names"])):
            if iter_ > 0:
                tpl.create_label('', box)

            gui_keyword = str(iter_) + " Battery"
            ic_keyword = bat_col["Names"][iter_]
            if gui_keyword not in bat_gui:
                bat_gui[gui_keyword] = {}

            bat_gui[gui_keyword]["SN"] = tpl.create_entry(bat_col[ic_keyword]["Serial"])
            bat_gui[gui_keyword]["Model"] = tpl.create_entry(bat_col[ic_keyword]["Model"])
            bat_gui[gui_keyword]["Estimated"] = tpl.create_entry(bat_col[ic_keyword]["Estimated"])

            max_energy = bat_col[ic_keyword]["Maximum Wh"]
            max_factory = bat_col[ic_keyword]["Factory Wh"]
            wearlevel = bat_col[ic_keyword]["Wear Level"]
            tooltip = "Current / Factory\n" + str(max_energy) + " / " + \
                      str(max_factory) + "\n\nWear level: " + str(wearlevel)

            tpl.create_label_entry_box("Serial", bat_gui[gui_keyword]["SN"], box)
            tpl.create_label_entry_box("Model", bat_gui[gui_keyword]["Model"], box)
            tpl.create_label_entry_box("Estimated Time", bat_gui[gui_keyword]["Estimated"], box, tooltip)

        box.show_all()

    def create_display_info_extended(self, box):
        self.togBooleans['Display']['Box'] = box

        screen_gui = self.infocollector.screen_Dict["GUI"]
        screen_col = self.infocollector.screen_Dict["Collected"]
        tpl = self.gui_base

        screen_gui["Diagonal"] = tpl.create_entry(screen_col["Diagonal"])
        screen_gui["Resolution"] = tpl.create_entry(screen_col["Resolution"])
        screen_gui["Category"] = tpl.create_entry(screen_col["Category"])
        screen_gui["Connection Type"] = tpl.create_entry(screen_col["Connection Type"])

        tpl.create_label_entry_box("Diagonal", screen_gui["Diagonal"], box)
        tpl.create_label_entry_box("Resolution", screen_gui["Resolution"], box)
        tpl.create_label_entry_box("Category", screen_gui["Category"], box)
        tpl.create_label_entry_box("Connection Type", screen_gui["Connection Type"], box)

        if self.infocollector.id_Dict["Collected"]["System Type"] == "Desktop":
            screen_gui["Diagonal"].set_text("N/A")
            screen_gui["Resolution"].set_text("N/A")
            screen_gui["Category"].set_text("N/A")
            screen_gui["Connection Type"].set_text("N/A")

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

    def computer_type_changed(self, _button):
        if not _button.get_text().lower() == "laptop":
            sensitive = True
        else:
            sensitive = False
        self.sys_form_factor.set_sensitive(sensitive)
