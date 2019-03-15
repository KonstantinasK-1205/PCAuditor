import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class GUITemplate:
    def __init__(self, infocollector):
        self.infocollector = infocollector
        self.main_window = ''
        self.keyboard_box = ''
        self.mouse_box = ''

    def init_variables(self, keyboard_box, mouse_box, window):
        self.main_window = window
        self.keyboard_box = keyboard_box
        self.mouse_box = mouse_box

    # < - Simple GTK Widgets - Label & Entry & Separator
    @staticmethod
    def create_label(_label, _box=''):
        _label = Gtk.Label.new(_label)
        if isinstance(_box, Gtk.Box):
            _box.pack_start(_label, False, False, 0)
        else:
            return _label

    @staticmethod
    def create_entry(_text='', _is_enabled=True, _box=''):
        entry = Gtk.Entry(xalign=0.5, width_chars=20, sensitive=_is_enabled, text=_text)
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
    def create_button(_text, _function='', _box='', _field='', _tooltip='', _stretch=False, _is_enabled=True):
        button = Gtk.Button(label=_text, sensitive=_is_enabled)
        if _tooltip:
            button.set_tooltip_text(_tooltip)
        if not _function == '':
            button.connect('clicked', _function, _field)

        if isinstance(_box, Gtk.Box):
            _box.pack_start(button, _stretch, _stretch, 0)
            return
        else:
            return button

    @staticmethod
    def create_toggleable_button(_text, _function, _field, _toggleable_dict):
        button = Gtk.Button(label=_text)
        button.connect('clicked', _function, _field)
        _toggleable_dict[_field]['Button'] = button
        return button

    @staticmethod
    def create_obs_button(_text, _function, _box, _obs_button_list):
        button = Gtk.Button(label=_text)
        button.connect('clicked', _function)
        _obs_button_list.append(button)
        _box.pack_start(button, False, False, 0)

    @staticmethod
    def create_spin_button(_init_value=1.0, _min_value=1.0, _max_value=1.0, _increment=1.0, _function=''):
        adjustment = Gtk.Adjustment.new(_init_value, _min_value, _max_value, _increment, 10, 0)
        spinbutton = Gtk.SpinButton.new(adjustment, _increment, 0)
        if _function:
            spinbutton.connect('value-changed', _function)
        return spinbutton

    def add_image_to_button(self, _image, _button, _is_always_shown=True, _image_pos=Gtk.PositionType.TOP):
        icon = Gtk.Image.new_from_file(self.infocollector.appResourcePath + "/" + _image)
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
    def create_label_dropbox(label, possible_values, box='', specific_value='', value_boolean=False, is_enabled=True):
        group_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, homogeneous=True)
        label = Gtk.Label.new(label)
        combobox = Gtk.ComboBoxText(sensitive=is_enabled)

        for option in possible_values:
            combobox.append_text(option)

        if specific_value in possible_values:
            combobox.set_active(possible_values.index(specific_value))
        else:
            if value_boolean:
                combobox.set_active(0)

        if isinstance(box, Gtk.Box):
            group_box.pack_start(label, False, False, 0)
            group_box.pack_start(combobox, True, True, 0)
            box.pack_start(group_box, False, False, 0)
            return
        else:
            return group_box, label, combobox

    @staticmethod
    def create_label_button_box(main_box, category_string, category_button):
        temp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, homogeneous=True)
        category = Gtk.Label.new(category_string)
        temp_box.pack_start(category, False, False, 0)
        temp_box.pack_start(category_button, False, False, 0)
        main_box.pack_start(temp_box, False, False, 0)

    @staticmethod
    def create_multiline_entry():
        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        entry = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        scrolled_window.add(entry)
        return scrolled_window

    def create_label_entry_box(self, label, entry, toggle_box, tooltip=''):
        group_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, homogeneous=True)
        label = Gtk.Label.new(label)

        if entry.get_text() == "-":
            entry = Gtk.Label("")
        if tooltip:
            group_box.set_tooltip_text(tooltip)

        group_box.pack_start(label, False, False, 0)
        group_box.pack_start(entry, False, False, 0)
        toggle_box.pack_start(group_box, False, False, 0)
        if not isinstance(entry, Gtk.Label):
            if not label == "Last tester":
                self.create_separator(toggle_box, 'horizontal', 1)

    # <- Set/Get/Change Widgets properties, values
    @staticmethod
    def set_multiline_text(widget, string):
        for child in widget.get_children():
            end_iter = child.get_buffer().get_end_iter()
            child.get_buffer().insert(end_iter, '\n' + string, -1)

            start_iter = child.get_buffer().get_start_iter()
            end_iter = child.get_buffer().get_end_iter()
            buffer_text = child.get_buffer().get_text(start_iter, end_iter, True).lstrip()
            child.get_buffer().set_text(buffer_text)

    @staticmethod
    def get_multiline_text(widget):
        text = ''
        for child in widget.get_children():
            start_iter = child.get_buffer().get_start_iter()
            end_iter = child.get_buffer().get_end_iter()
            text = child.get_buffer().get_text(start_iter, end_iter, True)
        return text

    @staticmethod
    def change_progressbar_value(widget, progress=0):
        widget.set_value(float(progress))

    @staticmethod
    def change_label(widget, text):
        if "Button" in str(type(widget)):
            widget.set_label(text)
        elif "Label" in str(type(widget)):
            widget.set_text(text)
        return False

    # < Dialogs Function
    @staticmethod
    def throw_options_win(_parent_win, _title, _content):
        dialog = Gtk.Dialog(parent=_parent_win)
        dialog.set_title(_title)
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

        image_pix_buf = GdkPixbuf.Pixbuf.new_from_file(_infocollector.pictures[_picture])
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
        dialog.connect('key-release-event', _events.file_chooser_key_event, _picture, dialog, _infocollector)
        dialog.run()
        dialog.destroy()

    def throw_bugreport_win(self, _parent_win, _title):
        dialog = Gtk.Dialog(parent=_parent_win, title=_title)
        dialog.set_size_request(320, 480)
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

        dialog.show_all()
        response = dialog.run()
        if response == 0:
            confirmed = False
            tester = ""
            multiline = ""
        else:
            confirmed = True
            tester = tester.get_text()
            multiline = self.get_multiline_text(multiline)
        dialog.destroy()
        return confirmed, tester, multiline
