import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class GUITemplate:
    def __init__(self, _infocollector):
        self.infocollector = _infocollector
        self.main_window = ''
        self.keyboard_box = ''
        self.mouse_box = ''

    def init_variables(self, _keyboard_box, _mouse_box, _window):
        self.main_window = _window
        self.keyboard_box = _keyboard_box
        self.mouse_box = _mouse_box

    # < - Simple GTK Widgets - Label & Entry & Separator
    @staticmethod
    def create_label(_label, _box=None):
        _label = Gtk.Label.new(_label)
        if isinstance(_box, Gtk.Box):
            _box.pack_start(_label, False, False, 0)
        else:
            return _label

    @staticmethod
    def create_entry(_text, _is_enabled=True, _box=None):
        entry = Gtk.Entry(xalign=0.5, width_chars=20, sensitive=_is_enabled, text=_text)
        if isinstance(_box, Gtk.Box):
            _box.pack_start(entry, False, False, 0)
        else:
            return entry

    @staticmethod
    def create_entry_with_signal(_text, _box=None, _signal=None, _function=None):
        entry = Gtk.Entry(xalign=0.5, width_chars=20, text=_text)
        entry.connect(_signal, _function)
        if isinstance(_box, Gtk.Box):
            _box.pack_start(entry, False, False, 0)
        else:
            return entry

    @staticmethod
    def create_separator(_box, _orientation='horizontal', _width=1):
        if 'horizontal' in _orientation.lower():
            _orientation = Gtk.Orientation.HORIZONTAL
        else:
            _orientation = Gtk.Orientation.VERTICAL
        separator = Gtk.Separator(orientation=_orientation, height_request=_width)
        _box.pack_start(separator, False, False, 0)

    # < - Simple GTK Widgets - Buttons
    @staticmethod
    def create_button(_text, _function=None, _box=None, _field=None, _tooltip=None, _stretch=False, _is_enabled=True):
        button = Gtk.Button(label=_text, sensitive=_is_enabled)
        if _function:
            if not _field:
                button.connect('clicked', _function)
            else:
                button.connect('clicked', _function, _field)
        if _tooltip:
            button.set_tooltip_text(_tooltip)

        if isinstance(_box, Gtk.Box):
            _box.pack_start(button, _stretch, _stretch, 0)
        else:
            return button

    @staticmethod
    def create_toggleable_button(_text, _function, _field, _toggleable_dict):
        button = Gtk.Button(label=_text)
        button.connect('clicked', _function, _field)
        _toggleable_dict[_field]['Button'] = button
        return button

    @staticmethod
    def create_obs_button(_text, _function, _first_level, _second_level, _code_val):
        button = Gtk.Button(label=_text)
        button.connect('clicked', _function, _first_level, _second_level, _code_val)
        return button

    @staticmethod
    def create_spin_button(_init_value=1.0, _min_value=1.0, _max_value=1.0, _increment=1.0, _function=''):
        adjustment = Gtk.Adjustment.new(value=_init_value, lower=_min_value, upper=_max_value,
                                        step_increment=_increment, page_increment=10, page_size=0)
        spin_button = Gtk.SpinButton.new(adjustment, climb_rate=_increment, digits=0)
        if _function:
            spin_button.connect('value-changed', _function)
        return spin_button

    def add_image_to_button(self, _image, _button, _is_always_shown=True, _image_pos=Gtk.PositionType.TOP):
        icon = Gtk.Image.new_from_file(filename=self.infocollector.appResourcePath + "/" + _image)
        _button.set_image(icon)
        _button.set_always_show_image(_is_always_shown)
        _button.set_image_position(_image_pos)
        return _button

    # < - Simple GTK Widgets - Containers
    @staticmethod
    def create_scrolling_box(_orientation='vertical', _visible='auto'):
        visibility = never = Gtk.PolicyType.NEVER
        if 'always' in _visible.lower():
            visibility = Gtk.PolicyType.ALWAYS
        elif 'auto' in _visible.lower():
            visibility = Gtk.PolicyType.AUTOMATIC

        scrolling_box = Gtk.ScrolledWindow()
        if 'vertical' in _orientation.lower():
            scrolling_box.set_policy(never, visibility)
        elif 'horizontal' in _orientation.lower():
            scrolling_box.set_policy(visibility, never)
        elif 'both' in _orientation.lower():
            scrolling_box.set_policy(visibility, visibility)
        return scrolling_box

    # < - Complex GTK Widgets
    @staticmethod
    def create_label_dropbox(_label, _possible_values, _box=None,
                             _specific_value=None, _value_boolean=False, _is_enabled=True, _pack_start=False):
        group_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, homogeneous=True)
        _label = Gtk.Label.new(_label)
        combobox = Gtk.ComboBoxText(sensitive=_is_enabled)

        for option in _possible_values:
            combobox.append_text(option)

        if _specific_value and _specific_value in _possible_values:
            combobox.set_active(_possible_values.index(_specific_value))
        else:
            if _value_boolean:
                combobox.set_active(0)

        if isinstance(_box, Gtk.Box):
            group_box.pack_start(_label, False, False, 0)
            group_box.pack_start(combobox, True, True, 0)
            if _pack_start:
                _box.pack_start(group_box, False, False, 0)
            else:
                _box.pack_end(group_box, False, False, 0)
            return combobox
        else:
            return group_box, _label, combobox

    @staticmethod
    def create_label_button_box(_main_box, _category_string, _category_button, _tooltip=None):
        temp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, homogeneous=True)
        category = Gtk.Label.new(_category_string)
        temp_box.pack_start(category, False, False, 0)
        temp_box.pack_start(_category_button, False, False, 0)

        if _tooltip:
            _category_button.set_tooltip_text(_tooltip)

        _main_box.pack_start(temp_box, False, False, 0)

    @staticmethod
    def create_multiline_entry():
        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        entry = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        scrolled_window.add(entry)
        return scrolled_window

    def create_label_entry_box(self, _label, _entry, _toggle_box, _tooltip=None):
        group_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, homogeneous=True)
        _label = Gtk.Label.new(_label)

        if _entry.get_text() == "-":
            _entry = Gtk.Label("")
        if _tooltip:
            group_box.set_tooltip_text(_tooltip)

        group_box.pack_start(_label, False, False, 0)
        group_box.pack_start(_entry, False, False, 0)
        _toggle_box.pack_start(group_box, False, False, 0)
        if not isinstance(_entry, Gtk.Label):
            if not _label == "Last tester":
                self.create_separator(_toggle_box, 'horizontal', 1)

    # <- Set/Get/Change Widgets properties, values
    @staticmethod
    def set_multiline_text(_widget, _string):
        for child in _widget.get_children():
            end_iter = child.get_buffer().get_end_iter()
            child.get_buffer().insert(end_iter, '\n' + _string, -1)

            start_iter = child.get_buffer().get_start_iter()
            end_iter = child.get_buffer().get_end_iter()
            buffer_text = child.get_buffer().get_text(start_iter, end_iter, True).lstrip()
            child.get_buffer().set_text(buffer_text)

    @staticmethod
    def get_multiline_text(_widget):
        text = ''
        for child in _widget.get_children():
            start_iter = child.get_buffer().get_start_iter()
            end_iter = child.get_buffer().get_end_iter()
            text = child.get_buffer().get_text(start_iter, end_iter, True)
        return text

    @staticmethod
    def change_progressbar_value(_widget, _progress=0):
        _widget.set_value(float(_progress))

    @staticmethod
    def change_label(_widget, _text):
        if isinstance(_widget, Gtk.Button):
            _widget.set_label(_text)
        elif isinstance(_widget, Gtk.Label):
            _widget.set_text(_text)
        return False

    # < Dialogs Function
    @staticmethod
    def throw_options_win(_parent_win, _title, _content):
        dialog = Gtk.Dialog(parent=_parent_win, title=_title)
        dialog.add_button("Godex DT4x ( Office)", 0)
        dialog.add_button("Godex G500 ( eBay )", 1)
        dialog.add_button("Cancel", 2)

        response = dialog.run()
        if response == 0:
            _str = "Godex_DT4x"
        elif response == 1:
            _str = "Godex_G500"
        else:
            _str = "Cancel"
        dialog.destroy()
        return _str

    @staticmethod
    def throw_question_win(parent_win, title, content):
        dialog = Gtk.MessageDialog(parent=parent_win, flags=0, message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO, text=title, secondary_text=content)
        response = dialog.run()
        response_state = ''
        if response == Gtk.ResponseType.YES:
            response_state = True
        elif response == Gtk.ResponseType.NO:
            response_state = False
        dialog.destroy()
        return response_state

    @staticmethod
    def throw_error_win(parent_win, title, content):
        dialog = Gtk.MessageDialog(parent=parent_win, flags=0, message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.CANCEL, text=title, secondary_text=content)
        dialog.run()
        dialog.destroy()

    @staticmethod
    def throw_image_window(_picture, _infocollector, _events):
        dialog = Gtk.Dialog(title=_infocollector.pictures[_picture])

        image_pix_buf = GdkPixbuf.Pixbuf.new_from_file(filename=_infocollector.pictures[_picture])
        image = Gtk.Image.new_from_pixbuf(image_pix_buf)
        image_box = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                                       vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        image_box.add(image)

        box = dialog.get_content_area()
        box.pack_start(image_box, True, True, 0)

        width = image_pix_buf.get_width() + 128
        height = image_pix_buf.get_height() + 128
        dialog.set_default_size(width, height)

        dialog.show_all()
        dialog.connect('key-release-event', _events.file_chooser_key_event, _picture, dialog)
        dialog.run()
        dialog.destroy()

    def throw_bugreport_win(self, _parent_win, _title):
        dialog = Gtk.Dialog(parent=_parent_win, title=_title, default_width=480, default_height=320)
        box = dialog.get_content_area()

        tester = Gtk.Entry()
        self.create_label_entry_box("Enter your name:", tester, box)
        self.create_label("\nPlease describe your problem:", box)
        multiline = self.create_multiline_entry()
        multiline.set_margin_bottom(5)
        multiline.set_margin_left(25)
        multiline.set_margin_right(25)
        box.add(multiline)
        dialog.add_button("Cancel", 0)
        dialog.add_button("Submit", 1)

        is_info_valid = False
        confirmed = False

        dialog.show_all()
        while not is_info_valid:
            response = dialog.run()
            if response == 0:
                is_info_valid = True
                confirmed = False
                tester = ""
                multiline = ""
            else:
                if not isinstance(tester, Gtk.Entry) or not tester.get_text():
                    self.throw_error_win(_parent_win, "Error", "Tester cannot be empty!")

                if not isinstance(multiline, Gtk.ScrolledWindow) or not self.get_multiline_text(multiline):
                    self.throw_error_win(_parent_win, "Error", "Problem description cannot be empty!")

                if isinstance(tester, Gtk.Entry) and isinstance(multiline, Gtk.ScrolledWindow):
                    if self.get_multiline_text(multiline) and tester.get_text():
                        multiline = self.get_multiline_text(multiline)
                        tester = tester.get_text()
                        is_info_valid = True
                        confirmed = True
        dialog.destroy()
        return confirmed, tester, multiline
