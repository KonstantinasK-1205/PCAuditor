import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class NBObservations:
    def __init__(self, gui_base, infocollector):
        self.gui_base = gui_base
        self.infocollector = infocollector
        self.selectedObs = dict()

        self.page_box = None
        self.obs_CategoryNB = None
        self.obs_CodeArea = None
        self.obs_CodeAreaInner = None

        self.obs_ListStore = Gtk.ListStore(str)

        self.obsCodes = []  # Stores string version of observations
        self.obsButtonList = []  # Stores list of GTK:Button(-s)
        self.obsNotes = None

        self.infocollector.debug_info("Information", "Observations - Variables Initilizated")

    def create_page(self):
        self.infocollector.debug_info("Information", "Creating Observations Page")
        self.page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.obs_CategoryNB = Gtk.Notebook(tab_pos=Gtk.PositionType.LEFT)

        self.obs_CodeArea = Gtk.Box()
        self.obs_CodeAreaInner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        if self.infocollector.observations["All"]:
            self.create_obs_notes(self.page_box)
            self.create_selected_code_area(self.obs_CodeAreaInner)
            # < Observations      | Adding obs to Obs List
            for MainKey, MainValue in self.infocollector.observations["All"].items():
                subcategory_nb = Gtk.Notebook()
                for SubKey, SubValue in MainValue.items():
                    if SubValue:
                        button_box_sb = self.gui_base.create_scrolling_box('vertical', 'always')
                        buttons_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                        for codeName, code in SubValue.items():
                            # For every Code create his own button
                            self.gui_base.create_obs_button(codeName, self.add_selected_to_list, buttons_box,
                                                            self.obsButtonList)
                        button_box_sb.add(buttons_box)
                        subcategory_nb.append_page(button_box_sb, Gtk.Label.new_with_mnemonic(SubKey))
                self.obs_CategoryNB.append_page(subcategory_nb, Gtk.Label.new_with_mnemonic(MainKey))

            self.load_saved_obs(self.infocollector.observations["Recorded"], self.infocollector.observations["All"])
            self.gui_base.create_button("Remove All", self.remove_all_selected_codes,
                                        self.obs_CodeAreaInner, 'Remove All')

            # < Observations      | Pushing to main Boxes
            self.obs_CodeArea.pack_start(self.obs_CategoryNB, True, True, 0)
            self.obs_CodeArea.pack_start(self.obs_CodeAreaInner, False, False, 0)
            self.page_box.pack_start(self.obs_CodeArea, True, True, 0)

        self.infocollector.debug_info("Information", "Finished creating - Observations Page")

    def create_obs_notes(self, box):
        note_box = Gtk.Box()
        label = Gtk.Label("Other")
        self.obsNotes = self.gui_base.create_multiline_entry()
        if self.infocollector.obsAddNotes:
            self.gui_base.set_multiline_text(self.obsNotes, self.infocollector.obsAddNotes)
        note_box.pack_end(self.obsNotes, True, True, 0)
        note_box.pack_end(label, False, False, 10)
        box.pack_end(note_box, True, True, 0)

    def create_selected_code_area(self, box):
        scroll_window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER,
                                           vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        treeview = Gtk.TreeView(model=self.obs_ListStore)
        treeview.connect("row_activated", self.get_activated_row)

        obs_code_render = Gtk.CellRendererText()
        treeview_column = Gtk.TreeViewColumn("Selected:", obs_code_render, text=0)
        treeview.append_column(treeview_column)
        scroll_window.add(treeview)
        box.pack_start(scroll_window, True, True, 0)

    # Observation Functions - [ add, load, sort, clear ]
    def add_selected_to_list(self, button='', _field=''):
        if not isinstance(button, Gtk.Button):
            for _button in self.obsButtonList:
                if button == _button.get_label():
                    button = _button
        obs_code = self.value_to_key(self.infocollector.observations["All"], button.get_label())
        if obs_code not in self.obsCodes:
            self.obsCodes.append(obs_code)
            self.obs_ListStore.append([obs_code])
            color = Gdk.color_parse('#ffae5d')
            button.modify_bg(Gtk.StateType.NORMAL, color)

    def load_saved_obs(self, obs_variable, observations):
        if obs_variable:
            for key, value in obs_variable.items():
                for _subKey, _subValue in obs_variable[key].items():
                    for code in _subValue:
                        self.add_selected_to_list(self.key_to_value(observations, code))

    def sort_obs_codes(self):
        self.clear_selected_codes()
        for code in sorted(self.obsCodes):
            _MainCategory = ''
            _SubCategory = ''
            for _mainKey, _mainValue in self.infocollector.observations["All"].items():
                for _subKey, _subValue in self.infocollector.observations["All"][_mainKey].items():
                    for _2subKey, _2subValue in self.infocollector.observations["All"][_mainKey][_subKey].items():
                        if code in _2subValue:
                            _MainCategory = _mainKey
                            _SubCategory = _subKey

            if _MainCategory not in self.selectedObs:
                self.selectedObs[_MainCategory] = {}
            if _SubCategory not in self.selectedObs[_MainCategory]:
                self.selectedObs[_MainCategory][_SubCategory] = []
            if code not in self.selectedObs[_MainCategory][_SubCategory]:
                self.selectedObs[_MainCategory][_SubCategory].append(code)

    def clear_selected_codes(self):
        note = self.gui_base.get_multiline_text(self.obsNotes)
        if "Add. comment" in self.selectedObs:
            note = self.selectedObs["Add. comment"]
        self.selectedObs.clear()
        self.selectedObs["Add. comment"] = note

    # Event - On Click ( Selected OBS )
    def get_activated_row(self, _treeview, path, _column):
        tree_iter = self.obs_ListStore.get_iter(path)
        key_code = self.key_to_value(self.infocollector.observations["All"], self.obs_ListStore[tree_iter][0])
        for _button in self.obsButtonList:
            if key_code == _button.get_label():
                _button.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#ffffff'))
                break
        self.obsCodes.remove(self.obs_ListStore[tree_iter][0])
        self.obs_ListStore.remove(tree_iter)

    # Button Functions
    def remove_all_selected_codes(self, _button, _field):
        if self.obsCodes:
            self.obsCodes.clear()
            self.obs_ListStore.clear()
            self.clear_selected_codes()
            for button in self.obsButtonList:
                color = Gdk.color_parse('#ffffff')
                button.modify_bg(Gtk.StateType.NORMAL, color)

    # Dict Related Functions
    def value_to_key(self, target_obj, key):
        if key in target_obj:
            return target_obj[key]
        for _key, _value in target_obj.items():
            if isinstance(_value, dict):
                _value = self.value_to_key(_value, key)
                if _value:
                    return _value

    def key_to_value(self, target_obj, searched_value):
        for _key, _value in target_obj.items():
            if isinstance(_value, dict):
                _value = self.key_to_value(_value, searched_value)
                if _value:
                    return _value
            if isinstance(_value, str):
                if _value == searched_value:
                    return _key
