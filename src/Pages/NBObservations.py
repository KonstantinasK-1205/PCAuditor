import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class NBObservations:
    def __init__(self, _gui_template, _infocollector):
        self.gui_base = _gui_template
        self.infocollector = _infocollector

        self.page = None
        self.category_nb = None
        self.page_wrapper = None
        self.selected_codes_area = None

        self.list_store_code = Gtk.ListStore(str)

        self.code_button_list = dict()
        self.selected_obs = []
        self.add_note = None

        self.infocollector.debug_info("Information", "Observations - Variables Initialized")

    def create_page(self):
        self.infocollector.debug_info("Information", "Creating Observations Page")

        self.page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.category_nb = Gtk.Notebook(tab_pos=Gtk.PositionType.LEFT)
        server_observations = self.infocollector.observations["Server"]

        self.page_wrapper = Gtk.Box()
        self.selected_codes_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        if server_observations:
            self.create_add_note(self.page)
            self.create_selected_code_area(self.selected_codes_area)

            # Observations | Adding observation codes as buttons
            # First items are main categories, etc: Top lid, Bottom lid, Palmrest
            for _category_key, _category_val in server_observations.items():
                type_nb = Gtk.Notebook()
                # Type items are sub categories, etc: Appearance, Function, Missing
                for _type_key, _type_val in _category_val.items():
                    if _type_val:
                        sc_box = self.gui_base.create_scrolling_box('vertical', 'always')
                        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                        for _code_name, _code_val in _type_val.items():
                            # For every Code create his own button
                            button = self.gui_base.create_obs_button(_code_name, self.add_selected_to_list,
                                                                     _category_key, _type_key, _code_val)
                            self.code_button_list.update({_code_val: button})
                            box.pack_start(button, False, False, 0)

                        sc_box.add(box)
                        type_nb.append_page(sc_box, Gtk.Label.new_with_mnemonic(_type_key))
                self.category_nb.append_page(type_nb, Gtk.Label.new_with_mnemonic(_category_key))

            self.gui_base.create_button("Remove All", self.remove_all_selected_codes,
                                        self.selected_codes_area, 'Remove All')

            if self.infocollector.observations["Recorded"]:
                self.load_saved_obs(self.infocollector.observations["Recorded"], server_observations)

            # < Observations      | Pushing to main Boxes
            self.page_wrapper.pack_start(self.category_nb, True, True, 0)
            self.page_wrapper.pack_start(self.selected_codes_area, False, False, 0)
            self.page.pack_start(self.page_wrapper, True, True, 0)

        self.infocollector.debug_info("Information", "Finished creating - Observations Page")

    def create_add_note(self, box):
        note_box = Gtk.Box()
        label = Gtk.Label("Other")
        self.add_note = self.gui_base.create_multiline_entry()
        if self.infocollector.obsAddNotes:
            self.gui_base.set_multiline_text(self.add_note, self.infocollector.obsAddNotes)
        note_box.pack_end(self.add_note, True, True, 0)
        note_box.pack_end(label, False, False, 10)
        box.pack_end(note_box, True, True, 0)

    def create_selected_code_area(self, box):
        scroll_window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER,
                                           vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        treeview = Gtk.TreeView(model=self.list_store_code)
        treeview.connect("row_activated", self.get_activated_row)

        obs_code_render = Gtk.CellRendererText()
        treeview_column = Gtk.TreeViewColumn("Selected:", obs_code_render, text=0)
        treeview.append_column(treeview_column)
        scroll_window.add(treeview)
        box.pack_start(scroll_window, True, True, 0)

    # Observation Functions - [ add, load, sort, clear ]
    def add_selected_to_list(self, _button, _category, _type, _code_val):
        # This block gets executed when there is any saved observations
        if isinstance(_button, str):
            _button = self.code_button_list.get(_code_val)

        if _code_val not in self.selected_obs:
            self.selected_obs.append(_code_val)
            self.list_store_code.append([_code_val])
            color = Gdk.color_parse('#ffae5d')
            _button.modify_bg(Gtk.StateType.NORMAL, color)

    def load_saved_obs(self, _recorded_obs, _observations):
        for _category_key, _category_val in _recorded_obs.items():
            for _type_key, _type_val in _category_val.items():
                for _code_key, _code_val in _type_val.items():
                    self.add_selected_to_list(_code_key, _category_key, _type_key, _code_val)

    def prepare_obs(self):
        note = self.gui_base.get_multiline_text(self.add_note)
        self.infocollector.observations["Selected"].clear()
        self.infocollector.observations["Selected"]["Add. comment"] = note

        for code in sorted(self.selected_obs):
            server_obs = self.infocollector.observations["Server"]
            selected_obs = self.infocollector.observations["Selected"]
            main_category = ''
            sub_category = ''
            # Now based on SNDA1, BTMM2 found it category and type
            for _main_key, _main_value in server_obs.items():
                for _sub_key, _sub_value in server_obs[_main_key].items():
                    for _sub_sub_key, _sub_sub_Value in server_obs[_main_key][_sub_key].items():
                        if code in _sub_sub_Value:
                            main_category = _main_key
                            sub_category = _sub_key

            if main_category and main_category not in selected_obs:
                selected_obs[main_category] = {}

            if sub_category and sub_category not in selected_obs[main_category]:
                selected_obs[main_category][sub_category] = []

            if code and code not in selected_obs[main_category][sub_category]:
                selected_obs[main_category][sub_category].append(code)

    # Event - On Click ( Selected OBS )
    def get_activated_row(self, _treeview, _path, _column):
        tree_iter = self.list_store_code.get_iter(_path)
        code_val = self.list_store_code[tree_iter][0]

        _button = self.code_button_list.get(code_val)
        _button.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#ffffff'))

        self.selected_obs.remove(code_val)
        self.list_store_code.remove(tree_iter)

    # Button Functions
    def remove_all_selected_codes(self, _button, _field):
        if self.selected_obs:
            self.list_store_code.clear()
            self.selected_obs.clear()
            for button in self.code_button_list.values():
                color = Gdk.color_parse('#ffffff')
                button.modify_bg(Gtk.StateType.NORMAL, color)
