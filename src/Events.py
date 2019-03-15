import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Events:
    def __init__(self):
        self.main_window = None
        self.nbTestPage = None
        self.infocollector = None

        self.MainNBCurrentPage = ''  # Keeps Main Notebook Page Index
        self.SubNBCurrentPage = ''  # Keeps Sub Notebook Page Index

        self.KeyPressedSignalID = None  # Keeps Key   Press   Event Signal ID
        self.KeyReleaseSignalID = None  # Keeps Key   Release Event Signal ID
        self.isKeyboardEventActive = False  # Keeps Keyboard      Event Boolean

        self.MousePressedSignalID = None  # Keeps Mouse Press   Event Signal ID
        self.MouseReleaseSignalID = None  # Keeps Mouse Release Event Signal ID
        self.isMouseEventActive = False  # Keeps Mouse         Event Boolean

        self.firstKeyEvent = True  # Turns false when any first button is pressed
        self.isCapslockOn = False  # Checks CapsLock State
        self.isNumlockOn = False  # Checks NumLock  State

    def init_variables(self, infocollector, win, test_page):
        self.infocollector = infocollector
        self.main_window = win
        self.nbTestPage = test_page
        self.infocollector.debug_info("Information", "Variables Initilizated")

    def toggle_mouse_signal(self, state):
        if not state:
            if self.isMouseEventActive:
                if self.MousePressedSignalID:
                    self.main_window.disconnect(self.MousePressedSignalID)
                if self.MouseReleaseSignalID:
                    self.main_window.disconnect(self.MouseReleaseSignalID)
                self.isMouseEventActive = False
        else:
            if not self.isMouseEventActive:
                self.MousePressedSignalID = self.main_window.connect("button-press-event", self.on_button_press,
                                                                     self.nbTestPage.mouseSubBox)
                self.MouseReleaseSignalID = self.main_window.connect("button-release-event", self.on_button_press,
                                                                     self.nbTestPage.mouseSubBox)
            self.isMouseEventActive = True

    def toggle_keyboard_signal(self, state):
        if not state:
            if self.isKeyboardEventActive:
                if self.KeyPressedSignalID:
                    self.main_window.disconnect(self.KeyPressedSignalID)
                if self.KeyReleaseSignalID:
                    self.main_window.disconnect(self.KeyReleaseSignalID)
                self.isKeyboardEventActive = False
        else:
            if not self.isKeyboardEventActive:
                self.KeyPressedSignalID = self.main_window.connect("key-press-event", self.on_key_press,
                                                                   self.nbTestPage.keyboardSubBox)
                self.KeyReleaseSignalID = self.main_window.connect("key-release-event", self.on_key_press,
                                                                   self.nbTestPage.keyboardSubBox)
            self.isKeyboardEventActive = True

    def get_notebook_page(self, _widget, _ev, data=None, field=''):
        nb_object = data.get_nth_page(data.get_current_page())
        if 'main' in field.lower():
            self.MainNBCurrentPage = data.get_tab_label_text(nb_object)
        elif 'sub' in field.lower():
            self.SubNBCurrentPage = data.get_tab_label_text(nb_object)
        self.main_event_parser()

    def main_event_parser(self, _widget='', _ev='', _data=None):
        if "tests" in self.MainNBCurrentPage.lower():
            if "mouse" in self.SubNBCurrentPage.lower():
                self.toggle_keyboard_signal(False)
                self.toggle_mouse_signal(True)
            elif "keyboard" in self.SubNBCurrentPage.lower():
                self.toggle_mouse_signal(False)
                self.toggle_keyboard_signal(True)
            else:
                self.toggle_mouse_signal(False)
                self.toggle_keyboard_signal(False)
        else:
            self.toggle_mouse_signal(False)
            self.toggle_keyboard_signal(False)

    def file_chooser_key_event(self, _widget, ev, data, dialog, infocollector):
        key_received = Gdk.keyval_name(ev.keyval)
        if key_received == 'Delete':
            infocollector.pictures.pop(data)
            self.main_window.reload_picture_gallery()
            dialog.destroy()
        if key_received == 'Escape':
            dialog.destroy()
        return False

    @staticmethod
    def on_button_press(_widget, ev, data=None):
        key_received = str(ev.button)
        event_type = str(ev.type)
        if key_received == "1":
            key_received = 'Left Button'
        elif key_received == "2":
            key_received = 'Middle Button'
        elif key_received == "3":
            key_received = 'Right Button'

        for button in data.get_children():
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

    def on_key_press(self, _widget, ev, data=None):
        key_received = Gdk.keyval_name(ev.keyval)
        event_type = str(ev.type)
        if key_received == "Escape":
            key_received = 'Esc'
        elif key_received == "grave":
            key_received = '`'
        elif key_received == "minus":
            key_received = '-'
        elif key_received == "equal":
            key_received = '='
        elif key_received == "bracketleft":
            key_received = '['
        elif key_received == "bracketright":
            key_received = ']'
        elif key_received == "ISO_Left_Tab":
            key_received = 'sTab'
        elif key_received == "Caps_Lock":
            key_received = 'CLK'
        elif key_received == "BackSpace":
            key_received = '⌫'
        elif key_received == "Return":
            key_received = '⏎'
        elif key_received == "semicolon":
            key_received = ';'
        elif key_received == "apostrophe":
            key_received = '\''
        elif key_received == "backslash":
            key_received = '\\'
        elif key_received == "comma":
            key_received = '.'
        elif key_received == "period":
            key_received = ','
        elif key_received == "slash":
            key_received = '/'
        elif key_received == "space":
            key_received = 'Space'
        elif key_received == "less":
            key_received = '<'
        elif key_received == "greater":
            key_received = '>'
        elif key_received == "question":
            key_received = '?'
        elif key_received == "colon":
            key_received = ':'
        elif key_received == "quotedbl":
            key_received = '\"'
        elif key_received == "bar":
            key_received = '|'
        elif key_received == "braceleft":
            key_received = '{'
        elif key_received == "braceright":
            key_received = '}'
        elif key_received == "asciitilde":
            key_received = '~'
        elif key_received == "exclam":
            key_received = '!'
        elif key_received == "at":
            key_received = '@'
        elif key_received == "numbersign":
            key_received = '#'
        elif key_received == "dollar":
            key_received = '$'
        elif key_received == "percent":
            key_received = '%'
        elif key_received == "asciicircum":
            key_received = '^'
        elif key_received == "ampersand":
            key_received = '&'
        elif key_received == "asterisk":
            key_received = '*'
        elif key_received == "parenleft":
            key_received = '('
        elif key_received == "parenright":
            key_received = ')'
        elif key_received == "underscore":
            key_received = '_'
        elif key_received == "plus":
            key_received = '+'
        elif key_received == "Up":
            key_received = '↑'
        elif key_received == "Down":
            key_received = '↓'
        elif key_received == "Left":
            key_received = '←'
        elif key_received == "Right":
            key_received = '→'
        elif key_received == "Page_Up":
            key_received = 'Page\nUp'
        elif key_received == "Page_Down":
            key_received = 'Page\nDown'
        elif key_received == "Delete":
            key_received = 'Del'
        elif key_received == "Print":
            key_received = 'Prnt\nScrn'
        elif key_received == "Scroll_Lock":
            key_received = 'Scr\nLck'
        elif key_received == "Num_Lock":
            key_received = 'Num\nLock'
        elif key_received == "KP_0":
            key_received = 'KP_0'
        elif key_received == "KP_1":
            key_received = 'KP_1'
        elif key_received == "KP_2":
            key_received = 'KP_2'
        elif key_received == "KP_3":
            key_received = 'KP_3'
        elif key_received == "KP_4":
            key_received = 'KP_4'
        elif key_received == "KP_5":
            key_received = 'KP_5'
        elif key_received == "KP_6":
            key_received = 'KP_6'
        elif key_received == "KP_7":
            key_received = 'KP_7'
        elif key_received == "KP_8":
            key_received = 'KP_8'
        elif key_received == "KP_9":
            key_received = 'KP_9'
        elif key_received == "KP_Decimal":
            key_received = 'KP_.'
        elif key_received == "KP_Subtract":
            key_received = 'KP_-'
        elif key_received == "KP_Add":
            key_received = 'KP_+'
        elif key_received == "KP_Divide":
            key_received = 'KP_/'
        elif key_received == "KP_Multiply":
            key_received = 'KP_*'
        elif key_received == "KP_Enter":
            key_received = 'KP\n⮠'

        if self.firstKeyEvent:
            if "LOCK_MASK" in str(ev.state):
                self.isCapslockOn = True
            if "MOD2_MASK" in str(ev.state):
                self.isNumlockOn = True
            self.firstKeyEvent = False

        for FirstLevelContainer in data.get_children():
            for Button in FirstLevelContainer:
                if key_received == Button.get_label():
                    color = ''
                    # Handle Events
                    if key_received not in self.nbTestPage.PressedKeys:
                        self.nbTestPage.PressedKeys[key_received] = 0
                    if "PRESS" in event_type:
                        color = Gdk.color_parse('#ffae5d')
                    elif "RELEASE" in event_type:
                        # Increase pressed value of received key by one
                        value = self.nbTestPage.PressedKeys.get(key_received) + 1
                        self.nbTestPage.PressedKeys[key_received] = value

                        # Increase progress bar
                        self.nbTestPage.PressedPercentage = len(self.nbTestPage.PressedKeys) / 87 * 100
                        self.nbTestPage.percentage_complete.set_value(self.nbTestPage.PressedPercentage)

                        # Set color and tooltip for button (key)
                        color = Gdk.color_parse('#aeff5d')
                        Button.set_tooltip_text(
                            "Pressed: True ( " + str(self.nbTestPage.PressedKeys[key_received]) + " )")
                        if 'CLK' == key_received:
                            self.isCapslockOn = not self.isCapslockOn
                            if self.isCapslockOn:
                                color = Gdk.color_parse('#498eeb')
                        if 'Num\nLock' == key_received:
                            self.isNumlockOn = not self.isNumlockOn
                            if self.isNumlockOn:
                                color = Gdk.color_parse('#498eeb')

                    Button.modify_bg(Gtk.StateType.NORMAL, color)
                    break
        return True
