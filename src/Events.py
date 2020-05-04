import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import subprocess


class Events:
    def __init__(self):
        self.main_window = None
        self.nb_test_page = None
        self.infocollector = None

        self.main_nb_current_page = ''  # Keeps Main Notebook Page Index
        self.sub_nb_current_page = ''  # Keeps Sub Notebook Page Index

        self.key_pressed_signal_id = None  # Keeps Key Press Event Signal ID
        self.key_released_signal_id = None  # Keeps Key Release Event Signal ID
        self.is_keyboard_event_active = False  # Keeps Keyboard Event Boolean

        self.mouse_pressed_signal_id = None  # Keeps Mouse Press Event Signal ID
        self.mouse_released_signal_id = None  # Keeps Mouse Release Event Signal ID
        self.is_mouse_event_active = False  # Keeps Mouse Event Boolean

        self.first_key_event = True  # Turns false when any first button is pressed
        self.is_capslock_on = False  # Checks CapsLock State
        self.is_numlock_on = False  # Checks NumLock  State

    def init_variables(self, _infocollector, _window, _test_page):
        self.infocollector = _infocollector
        self.main_window = _window
        self.nb_test_page = _test_page
        self.infocollector.debug_info("Information", "Variables Initialized")

    def toggle_mouse_signal(self, _state):
        if not _state:
            if self.is_mouse_event_active:
                if self.mouse_pressed_signal_id:
                    self.main_window.disconnect(self.mouse_pressed_signal_id)
                if self.mouse_released_signal_id:
                    self.main_window.disconnect(self.mouse_released_signal_id)
                self.is_mouse_event_active = False
        else:
            if not self.is_mouse_event_active:
                self.mouse_pressed_signal_id = self.main_window.connect("button-press-event", self.on_button_press,
                                                                        self.nb_test_page.mouseSubBox)
                self.mouse_released_signal_id = self.main_window.connect("button-release-event", self.on_button_press,
                                                                         self.nb_test_page.mouseSubBox)
            self.is_mouse_event_active = True

    def toggle_keyboard_signal(self, _state):
        if not _state:
            if self.is_keyboard_event_active:
                if self.key_pressed_signal_id:
                    self.main_window.disconnect(self.key_pressed_signal_id)
                if self.key_released_signal_id:
                    self.main_window.disconnect(self.key_released_signal_id)
                self.is_keyboard_event_active = False
        else:
            if not self.is_keyboard_event_active:
                self.key_pressed_signal_id = self.main_window.connect("key-press-event", self.on_key_press,
                                                                      self.nb_test_page.keyboardSubBox)
                self.key_released_signal_id = self.main_window.connect("key-release-event", self.on_key_press,
                                                                       self.nb_test_page.keyboardSubBox)
            self.is_keyboard_event_active = True

    def get_notebook_page(self, _widget, _event, data=None, _field=''):
        nb_object = data.get_nth_page(data.get_current_page())
        if 'main' in _field.lower():
            self.main_nb_current_page = data.get_tab_label_text(nb_object)
        elif 'sub' in _field.lower():
            self.sub_nb_current_page = data.get_tab_label_text(nb_object)
        self.main_event_parser()

    def main_event_parser(self, _widget='', _event='', _data=None):
        if "tests" in self.main_nb_current_page.lower():
            if "mouse" in self.sub_nb_current_page.lower():
                self.toggle_keyboard_signal(False)
                self.toggle_mouse_signal(True)
            elif "keyboard" in self.sub_nb_current_page.lower():
                self.toggle_mouse_signal(False)
                self.toggle_keyboard_signal(True)
            else:
                self.toggle_mouse_signal(False)
                self.toggle_keyboard_signal(False)
        else:
            self.toggle_mouse_signal(False)
            self.toggle_keyboard_signal(False)

    def file_chooser_key_event(self, _widget, _event, _data, _dialog):
        key_received = Gdk.keyval_name(_event.keyval)
        if key_received == 'Delete':
            self.infocollector.pictures.pop(_data)
            self.main_window.reload_picture_gallery()
            _dialog.destroy()
        if key_received == 'Escape':
            _dialog.destroy()
        return False

    @staticmethod
    def on_button_press(_widget, _event, _data=None):
        key_received = str(_event.button)
        event_type = str(_event.type)
        if key_received == "1":
            key_received = 'Left Button'
        elif key_received == "2":
            key_received = 'Middle Button'
        elif key_received == "3":
            key_received = 'Right Button'

        for button in _data.get_children():
            if key_received == button.get_label():
                valid_event = False
                color = ''
                if "PRESS" in event_type:
                    color = Gdk.color_parse('#ffae5d')
                    valid_event = True
                elif "RELEASE" in event_type:
                    color = Gdk.color_parse('#aeff5d')
                    valid_event = True
                if valid_event:
                    button.modify_bg(Gtk.StateType.NORMAL, color)
                    button.set_tooltip_text("Pressed: True")

    def on_key_press(self, _widget, _event, _data=None):
        key_received = Gdk.keyval_name(_event.keyval).lower()
        first_letter = key_received[:1]
        event_type = str(_event.type)

        if 'a' in first_letter:
            if key_received == "asciicircum":
                key_received = '^'
            elif key_received == "ampersand":
                key_received = '&'
            elif key_received == "asterisk":
                key_received = '*'
            elif key_received == "apostrophe":
                key_received = '\''
            elif key_received == "asciitilde":
                key_received = '~'
            elif key_received == "at":
                key_received = '@'
            elif key_received == "alt_l":
                key_received = 'Alt_L'
            elif key_received == "alt_r":
                key_received = 'Alt_R'
        elif 'b' in first_letter:
            if key_received == "backslash":
                key_received = '\\'
            elif key_received == "bracketleft":
                key_received = '['
            elif key_received == "bracketright":
                key_received = ']'
            elif key_received == "braceleft":
                key_received = '{'
            elif key_received == "braceright":
                key_received = '}'
            elif key_received == "bar":
                key_received = '|'
            elif key_received == "backspace":
                key_received = '⌫'
        elif 'c' in first_letter:
            if key_received == "caps_lock":
                key_received = 'CLK'
            elif key_received == "comma":
                key_received = '.'
            elif key_received == "colon":
                key_received = ':'
            elif key_received == "control_l":
                key_received = 'Control_L'
            elif key_received == "control_r":
                key_received = 'Control_R'
        elif 'd' in first_letter:
            if key_received == "down":
                key_received = '↓'
            elif key_received == "dollar":
                key_received = '$'
            elif key_received == "delete":
                key_received = 'Del'
        elif 'e' in first_letter:
            if key_received == "escape":
                key_received = 'Esc'
            elif key_received == "equal":
                key_received = '='
            elif key_received == "exclam":
                key_received = '!'
            elif key_received == "end":
                key_received = 'End'
        elif 'f' in first_letter:
            if key_received == "f1":
                key_received = 'F1'
            elif key_received == "f2":
                key_received = 'F2'
            elif key_received == "f3":
                key_received = 'F3'
            elif key_received == "f4":
                key_received = 'F4'
            elif key_received == "f5":
                key_received = 'F5'
            elif key_received == "f6":
                key_received = 'F6'
            elif key_received == "f7":
                key_received = 'F7'
            elif key_received == "f8":
                key_received = 'F8'
            elif key_received == "f9":
                key_received = 'F9'
            elif key_received == "f10":
                key_received = 'F10'
            elif key_received == "f11":
                key_received = 'F11'
            elif key_received == "f12":
                key_received = 'F12'
        elif 'g' in first_letter:
            if key_received == "grave":
                key_received = '`'
            elif key_received == "greater":
                key_received = '>'
        elif 'h' in first_letter:
            if key_received == "home":
                key_received = 'Home'
        elif 'i' in first_letter:
            if key_received == "iso_left_tab":
                key_received = 'sTab'
            if key_received == "insert":
                key_received = 'Insert'
        elif 'k' in first_letter:
            if key_received == "kp_0":
                key_received = 'KP_0'
            elif key_received == "kp_1":
                key_received = 'KP_1'
            elif key_received == "kp_2":
                key_received = 'KP_2'
            elif key_received == "kp_3":
                key_received = 'KP_3'
            elif key_received == "kp_4":
                key_received = 'KP_4'
            elif key_received == "kp_5":
                key_received = 'KP_5'
            elif key_received == "kp_6":
                key_received = 'KP_6'
            elif key_received == "kp_7":
                key_received = 'KP_7'
            elif key_received == "kp_8":
                key_received = 'KP_8'
            elif key_received == "kp_9":
                key_received = 'KP_9'
            elif key_received == "kp_decimal":
                key_received = 'KP_.'
            elif key_received == "kp_subtract":
                key_received = 'KP_-'
            elif key_received == "kp_add":
                key_received = 'KP_+'
            elif key_received == "kp_divide":
                key_received = 'KP_/'
            elif key_received == "kp_multiply":
                key_received = 'KP_*'
            elif key_received == "kp_enter":
                key_received = 'KP\n⮠'
        elif 'l' in first_letter:
            if key_received == "less":
                key_received = '<'
            elif key_received == "left":
                key_received = '←'
        elif 'm' in first_letter:
            if key_received == "minus":
                key_received = '-'
        elif 'n' in first_letter:
            if key_received == "numbersign":
                key_received = '#'
            elif key_received == "num_lock":
                key_received = 'Num\nLock'
        elif 'p' in first_letter:
            if key_received == "page_up":
                key_received = 'Page\nUp'
            elif key_received == "page_down":
                key_received = 'Page\nDown'
            elif key_received == "print":
                key_received = 'Prnt\nScrn'
            elif key_received == "plus":
                key_received = '+'
            elif key_received == "percent":
                key_received = '%'
            elif key_received == "parenleft":
                key_received = '('
            elif key_received == "parenright":
                key_received = ')'
            elif key_received == "period":
                key_received = ','
            elif key_received == "pause":
                key_received = 'Pause'
        elif 'q' in first_letter:
            if key_received == "question":
                key_received = '?'
            elif key_received == "quotedbl":
                key_received = '\"'
        elif 'r' in first_letter:
            if key_received == "return":
                key_received = '⏎'
            elif key_received == "right":
                key_received = '→'
        elif 's' in first_letter:
            if key_received == "semicolon":
                key_received = ';'
            elif key_received == "slash":
                key_received = '/'
            elif key_received == "space":
                key_received = 'Space'
            elif key_received == "scroll_lock":
                key_received = 'Scr\nLck'
            elif key_received == "shift_l":
                key_received = 'Shift_L'
            elif key_received == "shift_r":
                key_received = 'Shift_R'
            elif key_received == "super_l":
                key_received = 'Super_L'
            elif key_received == "super_r":
                key_received = 'Super_R'
        elif 't' in first_letter:
            if key_received == "tab":
                key_received = 'Tab'
        elif 'u' in first_letter:
            if key_received == "underscore":
                key_received = '_'
            elif key_received == "up":
                key_received = '↑'

        if self.first_key_event:
            if "LOCK_MASK" in str(_event.state):
                self.is_capslock_on = True
            if "MOD2_MASK" in str(_event.state):
                self.is_numlock_on = True
            self.first_key_event = False

        for FirstLevelContainer in _data.get_children():
            for Button in FirstLevelContainer:
                if key_received == Button.get_label():
                    color = ''
                    # Handle Events
                    if key_received not in self.nb_test_page.PressedKeys:
                        self.nb_test_page.PressedKeys[key_received] = 0
                    if "PRESS" in event_type:
                        color = Gdk.color_parse('#ffae5d')
                    elif "RELEASE" in event_type:
                        # Increase pressed value of received key by one
                        value = self.nb_test_page.PressedKeys.get(key_received) + 1
                        self.nb_test_page.PressedKeys[key_received] = value

                        # Increase progress bar
                        self.nb_test_page.PressedPercentage = len(self.nb_test_page.PressedKeys) / 87 * 100
                        self.nb_test_page.percentage_complete.set_value(self.nb_test_page.PressedPercentage)

                        # Set color and tooltip for button (key)
                        color = Gdk.color_parse('#aeff5d')
                        Button.set_tooltip_text(
                            "Pressed: True ( " + str(self.nb_test_page.PressedKeys[key_received]) + " )")
                        if 'CLK' == key_received:
                            self.is_capslock_on = not self.is_capslock_on
                            if self.is_capslock_on:
                                color = Gdk.color_parse('#498eeb')
                        if 'Num\nLock' == key_received:
                            self.is_numlock_on = not self.is_numlock_on
                            if self.is_numlock_on:
                                color = Gdk.color_parse('#498eeb')

                    Button.modify_bg(Gtk.StateType.NORMAL, color)
                    break
        return True

    @staticmethod
    def volume_changed(_event, _widget, _data, _bar):
        if _data <= 0:
            _bar.set_value(0)
        elif _data >= 100:
            _bar.set_value(100)

        try:
            subprocess.check_output(['amixer', 'sset', 'Master', str(_data) + '%'], stderr=subprocess.DEVNULL).decode(
                'utf-8', errors='ignore')
        except subprocess.CalledProcessError:
            subprocess.Popen(['amixer', '-c', '1', 'sset', 'Master', str(_data)], stderr=subprocess.DEVNULL)

    def audio_state_changed(self, _event, _widget, _data):
        if _widget.props.has_tooltip:
            icon = self.infocollector.appResourcePath + "Icons/MediumVolumeR_x32.png"
            _data = "on"
        else:
            icon = self.infocollector.appResourcePath + "Icons/Mute_x32.png"
            _data = "off"

        try:
            subprocess.check_output(['amixer', 'sset', 'Master', str(_data)], stderr=subprocess.DEVNULL).decode('utf-8',
                                                                                                                errors='ignore')
        except subprocess.CalledProcessError:
            subprocess.Popen(['amixer', '-c', '1', 'sset', 'Master', str(_data)], stderr=subprocess.DEVNULL)

        _widget.set_image(Gtk.Image.new_from_file(filename=icon))
        _widget.props.has_tooltip = not _widget.props.has_tooltip
