import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# Importing Modules related To Audio
import pyaudio
import audioop
import dbus


class NBTests:
    def __init__(self, gui_base, infocollector, events):
        self.gui_base = gui_base
        self.infocollector = infocollector
        self.events = events

        self.page_box = None
        self.display_box = None
        self.audio_box = None

        self.mouseBox = None
        self.mouseSubBox = None
        self.MicrophoneButton = None
        self.MicLevelBar = None

        self.keyboardBox = None
        self.keyboardSubBox = None
        self.percentage_complete = None

        self.colourIndex = None
        self.MicrophoneTestTime = None

        self.threadElapsedTime = None
        self.threadSecondsTime = None

        self.PressedKeys = dict()  # Stores pressed keys as list
        self.PressedPercentage = 0  # Keeps pressed keys amount in %
        self.LowerKeys = [  # Keyboard map
            '|NL|',
            'Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', '⌫', '|NL|',
            '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '', '|NL|',
            'Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '⏎', '|NL|',
            'CLK', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '\\', '|NL|',
            'Shift_L', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', ',', '/', 'Shift_R', '|NL|',
            'Control_L', 'Super_L', 'Alt_L', 'Space', 'Alt_R', 'Super_R', 'Control_R',
            '|NL|',
            '|Hx|', '|Hx|', '|Hx|', 'Prnt\nScrn', 'Scr\nLck', 'Pause', '|Hx|', 'Num\nLock', 'KP_/', 'KP_*', 'KP_-',
            '|NL|',
            '|Hx|', '|Hx|', '|Hx|', 'Insert', 'Home', 'Page\nUp', '|Hx|', 'KP_7', 'KP_8', 'KP_9', 'KP_+', '|NL|',
            '|Hx|', '|Hx|', '|Hx|', 'Del', 'End', 'Page\nDown', '|Hx|', 'KP_4', 'KP_5', 'KP_6', '|Hx|', '|NL|',
            '|Hx|', '|Hx|', '|Hx|', '|Hx|', '↑', '|Hx|', '|Hx|', 'KP_1', 'KP_2', 'KP_3', 'KP\n⮠', '|NL|',
            '|Hx|', '|Hx|', '|Hx|', '←', '↓', '→', '|Hx|', 'KP_0', 'KP_.']

        self.isMicrophoneTestActive = False
        self.isSpeakerTestActive = False

        self.kbd_bus = self.get_kbd_bus()
        try:
            self.kbd_max = self.kbd_bus.GetMaxBrightness()
        except dbus.exceptions.DBusException:
            self.kbd_bus = None
        if self.kbd_bus:
            self.kbd_thread = None
            self.kbd_brightness = None
            self.kbd_range_ended = False

        self.infocollector.debug_info("Information", "Tests NB - Variables Initilizated")

    def create_page(self):
        self.page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        test_sub_nb = Gtk.Notebook(tab_pos=Gtk.PositionType.LEFT)
        self.infocollector.debug_info("Information", "Creating - Test Page")

        self.create_display_page()
        self.create_multimedia_page()
        self.create_mouse_page()
        self.create_keyboard_page()

        test_sub_nb.connect('key-release-event', self.events.get_notebook_page, test_sub_nb, 'sub')
        test_sub_nb.connect('button-release-event', self.events.get_notebook_page, test_sub_nb, 'sub')

        test_sub_nb.append_page(self.display_box, Gtk.Label("Display"))
        test_sub_nb.append_page(self.audio_box, Gtk.Label("Audio"))
        test_sub_nb.append_page(self.mouseBox, Gtk.Label("Mouse"))
        test_sub_nb.append_page(self.keyboardBox, Gtk.Label("Keyboard"))

        self.page_box.pack_start(test_sub_nb, True, True, 0)

    def create_mouse_page(self):
        self.mouseBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mouseSubBox = Gtk.Box()
        event_boxy = Gtk.EventBox()
        mouse_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=250)
        self.gui_base.create_button(_text="Left Button", _box=self.mouseSubBox, _tooltip="Pressed: False", _function='',
                                    _stretch=True)
        self.gui_base.create_button(_text="Middle Button", _box=self.mouseSubBox, _tooltip="Pressed: False",
                                    _function='', _stretch=True)
        self.gui_base.create_button(_text="Right Button", _box=self.mouseSubBox, _tooltip="Pressed: False",
                                    _function='',
                                    _stretch=True)

        touchpad_area = Gtk.Box()
        touchpad = Gtk.Label(" ")
        touchpad_area.pack_start(touchpad, True, True, 0)

        mouse_layout.pack_start(touchpad_area, True, True, 0)
        mouse_layout.pack_start(self.mouseSubBox, True, True, 0)
        event_boxy.add(mouse_layout)
        self.mouseBox.pack_start(event_boxy, True, True, 0)
        self.infocollector.debug_info("Information", "Test Page - Mouse")

    # Display Functions
    def create_display_page(self):
        self.display_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.gui_base.create_button("Automatic", self.display_test, self.display_box, "Automatic")
        self.gui_base.create_label('', self.display_box)
        self.gui_base.create_label('', self.display_box)
        self.gui_base.create_button("White", self.display_test, self.display_box, "White")
        self.gui_base.create_button("Red  ", self.display_test, self.display_box, "Red")
        self.gui_base.create_button("Green", self.display_test, self.display_box, "Green")
        self.gui_base.create_button("Blue ", self.display_test, self.display_box, "Blue")
        self.gui_base.create_button("Black", self.display_test, self.display_box, "Black")
        self.infocollector.debug_info("Information", "Test Page - Display")

    def display_test(self, _button, color=''):
        self.colourIndex = 0
        if "automatic" in color.lower():
            colour_array = ['White', 'Red', 'Green', 'Blue', 'Black', 'Exit']
        else:
            colour_array = [color, 'Exit']
        colour_parsed = Gdk.color_parse(colour_array[self.colourIndex])

        test_window = Gtk.Window()
        test_window.fullscreen()
        test_window.connect('button-release-event', self.display_test_action, test_window, colour_array)
        test_window.connect('key-release-event', self.display_test_action, test_window, colour_array)
        test_window.connect("destroy", Gtk.main_quit)

        test_window.modify_bg(Gtk.StateType.NORMAL, colour_parsed)
        test_window.show_all()
        Gtk.main()

    def display_test_action(self, _widget, _event, test_win, color_array):
        self.colourIndex += 1
        if 'Exit' in color_array[self.colourIndex]:
            test_win.destroy()

        colour_parsed = Gdk.color_parse(color_array[self.colourIndex])
        test_win.modify_bg(Gtk.StateType.NORMAL, colour_parsed)
        return False

    # Multimedia Functions
    def create_multimedia_page(self):
        self.audio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        audio_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        full_speaker_button = self.gui_base.create_button(_text="Full Test", _function=self.audio_test)
        full_speaker_button = self.gui_base.add_image_to_button("Icons/BSpeaker.ico", full_speaker_button, True,
                                                                Gtk.PositionType.TOP)

        sub_box = Gtk.Box()
        left_speaker_button = self.gui_base.create_button(_text="Left", _function=self.audio_test)
        left_speaker_button = self.gui_base.add_image_to_button("Icons/LSpeaker.ico", left_speaker_button, True,
                                                                Gtk.PositionType.TOP)

        right_speaker_button = self.gui_base.create_button(_text="Right", _function=self.audio_test)
        right_speaker_button = self.gui_base.add_image_to_button("Icons/RSpeaker.ico", right_speaker_button, True,
                                                                 Gtk.PositionType.TOP)

        self.MicrophoneButton = self.gui_base.create_button(_text="Mic", _function=self.audio_test)
        self.MicrophoneButton = self.gui_base.add_image_to_button("Icons/Microphone.ico", self.MicrophoneButton,
                                                                  True, Gtk.PositionType.TOP)

        sub_box.pack_start(left_speaker_button, True, True, 0)
        sub_box.pack_start(self.MicrophoneButton, True, True, 0)
        sub_box.pack_start(right_speaker_button, True, True, 0)

        self.MicLevelBar = Gtk.LevelBar(min_value=0.0, max_value=10.0, mode=Gtk.LevelBarMode.DISCRETE)

        audio_layout.pack_start(full_speaker_button, False, False, 0)
        audio_layout.pack_start(sub_box, False, False, 0)
        audio_layout.pack_start(self.MicLevelBar, True, True, 0)
        self.audio_box.pack_start(audio_layout, True, True, 0)
        self.infocollector.debug_info("Information", "Test Page - Audio")

    def audio_test(self, widget, _data=0):
        source_button = widget.get_label()
        if "Mic" in source_button:
            if not self.isMicrophoneTestActive:
                stream = self.init_microphone()
                self.MicrophoneTestTime = 3  # 10
                self.MicrophoneButton.set_sensitive(False)
                GLib.timeout_add(5, self.microphone_thread, stream, 5, self.gui_base, self.MicrophoneButton,
                                 self.MicLevelBar)
        elif "Full" in source_button:
            if not self.isMicrophoneTestActive:
                stream = self.init_microphone()
                self.MicrophoneTestTime = 5
                self.MicrophoneButton.set_sensitive(False)
                GLib.timeout_add(5, self.microphone_thread, stream, 5, self.gui_base, self.MicrophoneButton,
                                 self.MicLevelBar)
            if not self.isSpeakerTestActive:
                GLib.timeout_add(0, self.speaker_test, source_button, widget)
        else:
            if not self.isSpeakerTestActive:
                GLib.timeout_add(0, self.speaker_test, source_button, widget)

    def speaker_test(self, target_speaker, _data=None, _ev=''):
        self.isSpeakerTestActive = True
        command = ["/root/.Scripts/PXECraft.sh", "--audio-test", "--" + target_speaker]
        try:
            subprocess.Popen(command)
        except FileNotFoundError:
            try:
                command[0] = command[0].replace("/root/.Scripts/",
                                                "/home/konstantin/Documents/Programming/Sopena Scripts/")
                subprocess.Popen(command)
            except Exception as e:
                self.infocollector.debug_info("Error", "Speaker Test - Problems With " + target_speaker + " Speaker")
                self.infocollector.debug_info("Error", e)
        self.infocollector.debug_info("Information", "Speaker Test was launched on " + str(target_speaker))
        self.isSpeakerTestActive = False
        return False

    def init_microphone(self):
        try:
            p = pyaudio.PyAudio()
            devices = {}
            print("Input : " + str(pyaudio.PyAudio().get_default_input_device_info()))
            print("Output: " + str(pyaudio.PyAudio().get_default_output_device_info()))
            print("Count : " + str(pyaudio.PyAudio().get_device_count()))
            for x in range(pyaudio.PyAudio().get_device_count()):
                d = pyaudio.PyAudio().get_device_info_by_index(x)
                devices[x] = {'name': d['name'], 'type': 'output' if d['maxInputChannels'] == 0 else 'input'}
                print(str(x) + " " + str(devices[x]))
            stream = p.open(format=pyaudio.paInt16,
                            frames_per_buffer=1024,
                            rate=44100,
                            input=True,
                            channels=2)
            self.threadElapsedTime = 0
            self.threadSecondsTime = -1
            self.isMicrophoneTestActive = True
            return stream
        except Exception as e:
            self.infocollector.debug_info("Exception", "Microphone Initialization, has catched exception")
            self.infocollector.debug_info("Exception", e)

    def microphone_thread(self, stream, update_time, gui_base, mic_button, mic_bar):
        try:
            self.threadElapsedTime += update_time / 1000
            if self.threadElapsedTime >= self.MicrophoneTestTime:
                gui_base.change_progressbar_value(mic_bar, 0)
                gui_base.change_label(mic_button, "Mic")
                mic_button.set_sensitive(True)
                self.isMicrophoneTestActive = False
                return False

            if int(self.threadElapsedTime + 0.005) > self.threadSecondsTime:
                self.threadSecondsTime = int(self.threadElapsedTime + 0.005)
                timeleft = self.MicrophoneTestTime - self.threadElapsedTime + 0.005
                gui_base.change_label(mic_button, "Timeleft: " + str(int(timeleft)) + " s")
                self.infocollector.debug_info("Information", "Microphone Thread, Timeleft: " + str(int(timeleft)))

            data = stream.read(1024, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            rms = rms / 3200

            gui_base.change_progressbar_value(mic_bar, rms)
            return True
        except Exception as e:
            self.infocollector.debug_info("Exception", "Microphone thread, has catched exception")
            self.infocollector.debug_info("Exception", e)
            return False

    # Keyboard Functions
    def create_keyboard_page(self):
        self.infocollector.debug_info("Information", "Test Page - Keyboard")

        self.keyboardBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.keyboardSubBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        keyboard_layout = Gtk.Grid(row_homogeneous=True, column_homogeneous=True)
        column = row = 0
        # Draw Keypad
        for keycap in self.LowerKeys:
            if '|NL|' in keycap:
                column = 0
                row += 1
                continue

            if '|Hx|' in keycap:
                button = Gtk.Label(label='')
            elif '|Vx|' in keycap:
                button = Gtk.Label(label='', angle=90)
            else:
                button = self.gui_base.create_button(keycap, _function='', _tooltip="Pressed: False")

            if "⏎" in keycap:
                keyboard_layout.attach(button, column, row, 1, 2)
                column += 2
                continue
            elif "⌫" in keycap:
                keyboard_layout.attach(button, column, row, 1, 2)
                column += 2
                continue
            elif "Space" in keycap:
                keyboard_layout.attach(button, column, row, 2, 1)
                column += 2
                continue
            elif "Shift" in keycap:
                keyboard_layout.attach(button, column, row, 2, 1)
                column += 2
                continue
            elif "Control" in keycap:
                keyboard_layout.attach(button, column, row, 2, 1)
                column += 2
                continue
            elif "Super" in keycap:
                keyboard_layout.attach(button, column, row, 2, 1)
                column += 2
                continue
            elif "Alt" in keycap:
                keyboard_layout.attach(button, column, row, 2, 1)
                column += 2
                continue
            elif "KP_0" in keycap:
                keyboard_layout.attach(button, column, row, 2, 1)
                column += 2
                continue
            elif "KP_+" in keycap:
                keyboard_layout.attach(button, column, row, 1, 2)
                column += 2
                continue
            elif "KP_-" in keycap:
                keyboard_layout.attach(button, column, row, 1, 1)
                column += 2
                continue
            elif "KP\n⮠" in keycap:
                keyboard_layout.attach(button, column, row, 1, 2)
                column += 2
                continue
            else:
                keyboard_layout.attach(button, column, row, 1, 1)
                column += 1

        self.keyboardSubBox.pack_start(keyboard_layout, True, True, 0)
        self.percentage_complete = Gtk.LevelBar.new_for_interval(min_value=0.0, max_value=100.0)

        self.keyboardBox.pack_start(self.keyboardSubBox, True, True, 0)
        self.keyboardBox.pack_start(self.percentage_complete, True, True, 0)

        box = Gtk.Box()
        kb_auto_button = self.gui_base.create_button("Start Backlight Test")
        kb_auto_button.connect('clicked', self.start_kb_thread)
        kb_cancel_button = self.gui_base.create_button("Cancel Backlight Test")
        kb_cancel_button.connect('clicked', self.stop_kb_thread, kb_auto_button)
        if not self.kbd_bus:
            kb_auto_button.set_sensitive(False)
            kb_cancel_button.set_sensitive(False)

        kb_reset_test = self.gui_base.create_button("Restart Keyboard Test")
        kb_reset_test.connect('clicked', self.restart_keyboard_test)

        box.pack_start(kb_auto_button, True, True, 0)
        box.pack_start(kb_cancel_button, True, True, 0)
        box.pack_start(kb_reset_test, True, True, 0)
        self.keyboardBox.pack_start(box, False, False, 0)

    def restart_keyboard_test(self, _widget='', _data=''):
        self.percentage_complete.set_value(0)
        self.PressedPercentage = 0
        self.PressedKeys.clear()
        for grid in self.keyboardSubBox:
            for button in grid:
                color = Gdk.color_parse('#ffffff')
                button.set_tooltip_text("Pressed: False")
                button.modify_bg(Gtk.StateType.NORMAL, color)

    def check_keyboard_test(self):
        _str = ''
        allow_to_pass = False
        if int(self.percentage_complete.get_value()) <= 5:
            _str = "Please start Keyboard interactive test!"
        elif int(self.percentage_complete.get_value()) <= 10:
            _str = "We would like to ask you again, to complete keyboard test!"
        elif int(self.percentage_complete.get_value()) <= 15:
            _str = "For fuck sake, press at least few more buttons to continue"
        elif int(self.percentage_complete.get_value()) <= 20:
            _str = "Keyboard test was done very poorly, are you sure want to continue?\n" \
                   "Gintaras & Marius will be notified about this."
            allow_to_pass = True
        elif int(self.percentage_complete.get_value()) <= 40:
            _str = "Not all keyboard keys was tested, are you sure you want to continue?"
            allow_to_pass = True
        elif int(self.percentage_complete.get_value()) <= 60:
            _str = "Test has been done only half way, please if possible finish test!\n" \
                   "If it isn't possible press \'Yes\', to continue"
            allow_to_pass = True
        elif int(self.percentage_complete.get_value()) <= 85 or int(self.percentage_complete.get_value()) > 85:
            allow_to_pass = True
        return [allow_to_pass, _str]

    @staticmethod
    def get_kbd_bus():
        try:
            bus = dbus.SystemBus()
            proxy = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower/KbdBacklight')
            kbd_backlight = dbus.Interface(proxy, 'org.freedesktop.UPower.KbdBacklight')
            return kbd_backlight
        except dbus.UnknownMethodException:
            return False

    def start_kb_thread(self, _button=None):
        if not self.kbd_thread:
            _button.set_sensitive(False)
            self.kbd_bus.SetBrightness(0)
            self.kbd_brightness = 0
            self.kbd_range_ended = False
            self.kbd_thread = GLib.timeout_add(100, self.set_kb_auto_test, self.kbd_bus, self.kbd_max)

    def stop_kb_thread(self, _button, _start_button=None):
        if self.kbd_thread:
            _start_button.set_sensitive(True)
            GLib.source_remove(self.kbd_thread)
            self.kbd_thread = None

    def set_kb_auto_test(self, _kbd_bus, _kbd_max):
        brightness = self.kbd_brightness
        if brightness < _kbd_max + 1 and not self.kbd_range_ended:
            brightness += 1
        else:
            brightness -= 1

        if brightness == _kbd_max:
            self.kbd_range_ended = True
        elif brightness == 0:
            self.kbd_range_ended = False

        _kbd_bus.SetBrightness(brightness)
        self.kbd_brightness = brightness
        return True

    # USB Functions
    @staticmethod
    def interface_changed(_signal, _iface, *_args):
        print("Received something... " + str(_args))
