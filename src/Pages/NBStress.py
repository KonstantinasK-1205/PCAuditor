import os
import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np


class NBStress:
    def __init__(self, gui_base, infocollector):
        # Main Class variables
        self.gui_base = gui_base
        self.infocollector = infocollector
        self.stress_threads = ['', '', '', '']

        # GUI variables
        self.page_box = None
        self.timer_spinbox = None
        self.cpu_stress_bttn = None
        self.gpu_1_stress_bttn = None
        self.gpu_2_stress_bttn = None
        self.all_stress_bttn = None
        self.cancel_bttn = None
        self.save_figure = None
        self.cpu_timer = 0
        self.gpu_timer = 0

        # Plot(-s) Variables
        self.ExecutionTime = 0
        self.ExecutionTimeArray = []

        self.clock_figure = None
        self.clock_plot = None
        self.clock_data = None
        self.clock_stats = [9999, 0, 0]

        self.temp_figure = None
        self.temp_plot = None
        self.temp_data = None

        # Stress Variables
        self.full_stress_alive = 0
        self.cpu_stress_alive = 0
        self.gpu_stress_alive = [0, 0]
        self.cooldown_time = 15

        self.is_cpu_stressed = False
        self.is_gpu_stressed = False
        self.is_cpu_overheats = False
        self.is_gpu_overheats = False

        self.cpu_at_overheat = 0
        self.gpu_at_overheat = 0
        self.cpu_warning_text = ''
        self.gpu_warning_text = ''

        self.gpu_offload = os.environ.copy()

        self.infocollector.debug_info("Information", "Stress - Variables Initialized")

    def create_page(self):
        # Create page wrapper, content body and its elements
        self.page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button_box = Gtk.Box()
        self.timer_spinbox = self.gui_base.create_spin_button(10, 1, 60, 1)
        self.cpu_stress_bttn = self.gui_base.create_button(_text="Stress CPU", _function=self.stress_system,
                                                           _field='CPU')
        self.gpu_1_stress_bttn = self.gui_base.create_button(_text="Stress 1 GPU", _function=self.stress_system,
                                                             _field='1 GPU')
        self.gpu_2_stress_bttn = self.gui_base.create_button(_text="Stress 2 GPU", _function=self.stress_system,
                                                             _field='2 GPU')
        self.all_stress_bttn = self.gui_base.create_button(_text="Stress ALL", _function=self.stress_system,
                                                           _field='All')
        self.cancel_bttn = self.gui_base.create_button(_text="CANCEL Stress", _function=self.stress_system,
                                                       _field='Cancel')
        self.save_figure = self.gui_base.create_button(_text="Save Stress", _function=self.save_stress,
                                                       _field='Save')
        if not self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
            self.gpu_2_stress_bttn.set_sensitive(False)

        # Push all elements inside container
        button_box.pack_start(self.timer_spinbox, True, True, 0)
        button_box.pack_start(self.cpu_stress_bttn, True, True, 0)
        button_box.pack_start(self.gpu_1_stress_bttn, True, True, 0)
        button_box.pack_start(self.gpu_2_stress_bttn, True, True, 0)
        button_box.pack_start(self.all_stress_bttn, True, True, 0)
        button_box.pack_start(self.cancel_bttn, True, True, 0)
        button_box.pack_start(self.save_figure, True, True, 0)
        self.page_box.pack_start(button_box, False, False, 0)
        self.ExecutionTimeArray.append(0)

        self.temp_figure = self.create_figure_plot(1, 1, 75)
        self.temp_plot = self.temp_figure.add_subplot(111, facecolor='#262626')
        self.temp_plot.grid(b=True, which='major', axis='y', color='#4c4c4c', linestyle='-', linewidth=1.5)
        self.temp_plot.grid(b=True, which='major', axis='x', color='#4c4c4c', linestyle='-.', linewidth=1)
        self.temp_plot.set_ylim(0, 120)
        self.temp_plot.set_ylabel('Min temp: \nAvg temp: \nMax temp: ')

        self.temp_data = []
        for _key in self.infocollector.cpu_Dict["Stats"]['Temps']["Dynamic"].keys():
            line, = self.temp_plot.plot(0, 0, label=_key)
            self.temp_data.append(line)

        for _key in self.infocollector.gpu_Dict["Stats"]['Temps']["Dynamic"].keys():
            line, = self.temp_plot.plot(0, 0, label=_key)
            self.temp_data.append(line)
        self.temp_plot.legend(loc=2)

        self.clock_figure = self.create_figure_plot(1, 1, 75)
        self.clock_plot = self.clock_figure.add_subplot(111, facecolor='#262626')
        self.clock_plot.grid(b=True, which='major', axis='y', color='#4c4c4c', linestyle='-', linewidth=1.5)
        self.clock_plot.grid(b=True, which='major', axis='x', color='#4c4c4c', linestyle='-.', linewidth=1)
        self.clock_plot.set_ylim(0, self.infocollector.cpu_Dict["Collected"]["Maximum Clock INT"] + 500)
        self.clock_plot.set_ylabel('Core Clock')

        self.clock_data = []
        for _key in self.infocollector.cpu_Dict["Stats"]['Clock'].keys():
            line, = self.clock_plot.plot(0, 0, label=_key)
            self.clock_data.append(line)
        self.clock_plot.legend(loc=2)
        self.page_box.show_all()

        self.page_box.pack_start(FigureCanvas(self.temp_figure), True, True, 0)
        self.page_box.pack_start(FigureCanvas(self.clock_figure), True, True, 0)
        # < -----------------------------------------------------------------------------
        # < -----------------------------------------------------------------------------

    def update_plot(self, _frame, *_data):
        # _data = ( Plot, 2DLines, TimeArray, String )
        # Set appropriate variables
        if _data[3] == 'clock':
            cpu_dict = self.infocollector.cpu_Dict["Stats"]['Clock']
            gpu_dict = self.infocollector.gpu_Dict["Stats"]['Clock']
        elif _data[3] == 'temp':
            cpu_dict = self.infocollector.cpu_Dict["Stats"]['Temps']['Dynamic']
            gpu_dict = self.infocollector.gpu_Dict["Stats"]['Temps']['Dynamic']
        else:
            return None
        for line in _data[1]:
            label = line.get_label()
            if label in cpu_dict:
                line.set_data(_data[2], cpu_dict[label])
            elif label in gpu_dict:
                line.set_data(_data[2], gpu_dict[label])
            yield line

    def stress_thread(self, _update_time, _notebook, _parent_win):
        # Initialize variables
        tab_label = "Stress"
        max_cpu_temp = max_gpu_temp = None

        cpu_clock = self.infocollector.cpu_Dict['Stats']['Clock']
        cpu_temps = self.infocollector.cpu_Dict['Stats']['Temps']
        gpu_temps = self.infocollector.gpu_Dict['Stats']['Temps']

        self.ExecutionTime += _update_time / 1000
        self.ExecutionTimeArray.append(int(self.ExecutionTime))
        current_sec = self.ExecutionTime

        # Update sensors, temperature and clocks
        sensors = self.infocollector.get_sensors_output()
        self.infocollector.update_cpu_temp(cpu_temps, sensors)
        self.infocollector.update_gpu_temp(gpu_temps, sensors)
        self.infocollector.get_core_clock(cpu_clock)

        # Update Clock Plot
        if cpu_clock:
            # Update x axis limit for plots
            if current_sec > 300:
                self.clock_plot.set_xlim(current_sec - 300, current_sec, False)
            else:
                self.clock_plot.set_xlim(0, current_sec, False)
            animation.FuncAnimation(self.clock_figure, self.update_plot, frames=1, repeat=False, blit=True,
                                    fargs=(self.clock_plot, self.clock_data, self.ExecutionTimeArray, 'clock'))
            self.temp_plot.set_ylabel('Min temp: ' + str(self.clock_stats[0]) + '\n'
                                                                                'Avg temp: ' + str(
                self.clock_stats[1]) + '\n'
                                       'Max temp: ' + str(self.clock_stats[2]))

        # Update Temp Plot
        if cpu_temps['Dynamic'] or gpu_temps['Dynamic']:
            # Update x axis limit
            if current_sec > 300:
                self.temp_plot.set_xlim(current_sec - 300, current_sec, False)
            else:
                self.temp_plot.set_xlim(0, current_sec, False)
            animation.FuncAnimation(self.temp_figure, self.update_plot, frames=1, repeat=False, blit=True,
                                    fargs=(self.temp_plot, self.temp_data, self.ExecutionTimeArray, 'temp'))

            # Update highest CPU/GPU temps
            cpu_values = cpu_temps['Dynamic'].values()
            min_cpu = round(min(cpu_values, key=lambda k: k[1])[-1] * 2) / 2
            avg_cpu = round(np.array(list(cpu_values)).mean() * 2) / 2
            max_cpu = round(max(cpu_values, key=lambda k: k[1])[-1] * 2) / 2
            if min_cpu < self.clock_stats[0]: self.clock_stats[0] = min_cpu
            if avg_cpu > self.clock_stats[1]: self.clock_stats[1] = avg_cpu
            if max_cpu > self.clock_stats[2]: self.clock_stats[2] = max_cpu

            if cpu_temps['Dynamic']: max_cpu_temp = max_cpu
            if gpu_temps['Dynamic']: max_gpu_temp = max(gpu_temps['Dynamic'].values(), key=lambda k: k[1])[-1]

        # Temperature monitoring, notify if hardware is overheating
        if max_cpu_temp:
            is_stressed = None
            # If current maximum temp exceeds critical temperature while stressing
            if self.is_cpu_stressed and max_cpu_temp >= cpu_temps['Critical'] and not self.is_cpu_overheats:
                is_stressed = True
                self.is_cpu_overheats = True
            # If current maximum temp exceeds maximum temperature while idling
            elif not self.is_cpu_stressed and max_cpu_temp >= cpu_temps['Maximum'] and not self.is_cpu_overheats:
                is_stressed = False
                self.is_cpu_overheats = True
            # If cpu is overheating
            if self.is_cpu_overheats and not self.cpu_warning_text:
                if is_stressed:
                    text = ["CPU overheats while stressing! ", str(cpu_temps["Critical"])]
                else:
                    text = ["CPU overheats while idling! ", str(cpu_temps["Maximum"])]
                self.cpu_warning_text = text[0] + str(max_cpu_temp) + "C / " + text[1] + " C"
                self.cpu_at_overheat = max_cpu_temp
                self.gui_base.throw_error_win(_parent_win, "Overheating!", self.cpu_warning_text)
            tab_label += ("\nCPU " + str(max_cpu_temp) + " C")

        if max_gpu_temp:
            is_stressed = None
            # If current maximum temp exceeds critical temperature while stressing
            if self.is_gpu_stressed and max_gpu_temp >= gpu_temps['Critical'] and not self.is_gpu_overheats:
                is_stressed = True
                self.is_gpu_overheats = True
            # If current maximum temp exceeds maximum temperature while idling
            elif not self.is_gpu_stressed and max_gpu_temp >= gpu_temps['Maximum'] and not self.is_gpu_overheats:
                is_stressed = False
                self.is_gpu_overheats = True
            # If gpu is overheating
            if self.is_gpu_overheats and not self.gpu_warning_text:
                if is_stressed:
                    text = ["GPU overheats while stressing!", str(gpu_temps["Critical"])]
                else:
                    text = ["GPU overheats while idling!", str(gpu_temps["Maximum"])]
                self.gpu_warning_text = text[0] + str(max_gpu_temp) + "C / " + text[1] + " C"
                self.gpu_at_overheat = max_gpu_temp
                self.gui_base.throw_error_win(_parent_win, "Overheating!", self.gpu_warning_text)
            tab_label += ("\nGPU " + str(max_gpu_temp) + " C")

        _notebook.set_tab_label_text(self.page_box, tab_label)
        return True

    def save_stress(self, _button, _data=None):
        self.clock_figure.savefig('Clock_Figure.png', dpi=600)
        self.temp_figure.savefig('Temp_Figure.png', dpi=100)

    def stress_system(self, _button, _data=None):
        label = _button.get_label()
        timer = self.timer_spinbox.get_value() * 60 + self.cooldown_time
        if "CPU" in label:  # DONE
            _button.set_label(_button.get_label().replace('Stress', ''))
            _button.set_sensitive(False)
            self.is_cpu_stressed = True
            subprocess.Popen(["stress-ng", "--matrix", "0" "-c", "nproc", "--timeout", str(timer - self.cooldown_time)])
            self.stress_threads[0] = GLib.timeout_add(1000, self.cpu_stress_thread, 1, timer)
        elif "GPU" in label:
            if "1" in label:
                self.stress_threads[1] = GLib.timeout_add(1000, self.gpu_stress_thread, 1, timer, _button)
            elif "2" in label:
                self.stress_threads[2] = GLib.timeout_add(1000, self.gpu_stress_thread, 1, timer, _button)
                self.detect_dri_prime(self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"])
            self.is_gpu_stressed = True
            _button.set_sensitive(False)
            _button.set_label(_button.get_label().replace('Stress', '').replace('GPU', 'GPU |'))
            subprocess.Popen(["stressgpu", "/test=fur", "/display_osi"], env=self.gpu_offload)
        elif "ALL" in label:
            self.gpu_offload["DRI_PRIME"] = "1"
            subprocess.Popen(["stress-ng", "--matrix", "0" "-c", "nproc", "--timeout", str(timer - self.cooldown_time)])
            subprocess.Popen(["stressgpu", "/test=fur", "/display_osi"], env=self.gpu_offload)

            self.cpu_stress_bttn.set_sensitive(False)
            self.gpu_1_stress_bttn.set_sensitive(False)
            self.gpu_2_stress_bttn.set_sensitive(False)
            self.all_stress_bttn.set_sensitive(False)
            self.is_cpu_stressed = True
            self.is_gpu_stressed = True
            self.stress_threads[3] = GLib.timeout_add(1000, self.full_stress, 1, timer)
        elif "CANCEL" in label:
            subprocess.Popen(["pkill", "-9", "stress-ng"])
            subprocess.Popen(["pkill", "-9", "GpuTest"])

            for x in range(4):
                if self.stress_threads[x]:
                    GLib.source_remove(self.stress_threads[x])
                    self.stress_threads[x] = ''

            self.cpu_stress_bttn.set_sensitive(True)
            self.gpu_1_stress_bttn.set_sensitive(True)
            self.all_stress_bttn.set_sensitive(False)
            self.cancel_bttn.set_sensitive(True)

            self.cpu_stress_bttn.set_label("Stress CPU")
            self.gpu_1_stress_bttn.set_label("Stress 1 GPU")
            self.all_stress_bttn.set_label("Stress ALL")

            if not self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
                self.gpu_2_stress_bttn.set_sensitive(False)
            else:
                self.gpu_2_stress_bttn.set_label("Stress 2 GPU")
                self.gpu_2_stress_bttn.set_sensitive(True)

            self.cpu_timer = 0
            self.gpu_timer = 0

    def detect_dri_prime(self, _maf):
        manufacturer = _maf.lower()
        if "nvidia" in manufacturer or "amd" in manufacturer:
            self.gpu_offload["DRI_PRIME"] = "1"
        else:
            self.gpu_offload[""] = ""

    def cpu_stress_thread(self, _update_time, _stress_time):
        self.cpu_stress_alive += _update_time
        if self.cpu_stress_alive <= _stress_time:
            label = "CPU | " + str(_stress_time - self.cpu_stress_alive)
            self.cpu_stress_bttn.set_label(label)
        else:
            self.cancel_cpu_stress()
            return False
        return True

    def gpu_stress_thread(self, _update_time, _stress_time, _button):
        label = _button.get_label()
        if '1 GPU' in label:
            self.gpu_stress_alive[0] += _update_time
            gpu_timeleft = _stress_time - self.gpu_stress_alive[0]
        elif '2 GPU' in label:
            self.gpu_stress_alive[1] += _update_time
            gpu_timeleft = _stress_time - self.gpu_stress_alive[1]
        else:
            return False

        if self.cooldown_time > gpu_timeleft:
            subprocess.Popen(["pkill", "-9", "GpuTest"])

        if 0 <= gpu_timeleft:
            label = label.split('|')[0] + "| " + str(gpu_timeleft)
            _button.set_label(label)
        else:
            self.cancel_gpu_stress(_button)
            return False
        return True

    def full_stress(self, _update_time, _stress_time):
        self.full_stress_alive += _update_time
        gpu_timeleft = _stress_time - self.full_stress_alive

        if self.cooldown_time > gpu_timeleft:
            subprocess.Popen(["pkill", "-9", "GpuTest"])

        if self.full_stress_alive <= _stress_time:
            cpu_label = "CPU | " + str(_stress_time - self.full_stress_alive)
            gpu_label = str(gpu_timeleft)
            self.cpu_stress_bttn.set_label(cpu_label)
            self.gpu_1_stress_bttn.set_label("1 GPU | " + gpu_label)
            if self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
                self.gpu_2_stress_bttn.set_label("2 GPU | " + gpu_label)
        else:
            self.cpu_stress_bttn.set_label(" Stress CPU")
            self.cpu_stress_bttn.set_sensitive(True)
            self.gpu_1_stress_bttn.set_label("Stress 1 GPU")
            self.gpu_1_stress_bttn.set_sensitive(True)
            if not self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
                self.gpu_2_stress_bttn.set_sensitive(False)
            else:
                self.gpu_2_stress_bttn.set_label("Stress 2 GPU")
                self.gpu_2_stress_bttn.set_sensitive(True)
            self.all_stress_bttn.set_sensitive(True)

            self.full_stress_alive = 0
            self.is_cpu_stressed = False
            self.is_gpu_stressed = False
            return False
        return True

    def cancel_cpu_stress(self):
        self.cpu_stress_bttn.set_label("Stress CPU")
        self.cpu_stress_bttn.set_sensitive(True)
        self.is_cpu_stressed = False
        self.cpu_stress_alive = 0

    def cancel_gpu_stress(self, _button):
        label = _button.get_label()
        _button.set_label("Stress" + label.split(' |')[0])
        _button.set_sensitive(True)

        self.is_gpu_stressed = False
        if '1 GPU' in label:
            thread_id = 1
        elif '2 GPU' in label:
            thread_id = 2
        else:
            return False

        self.gpu_stress_alive[thread_id - 1] = 0
        if self.stress_threads[thread_id]:
            GLib.source_remove(self.stress_threads[thread_id])
            self.stress_threads[thread_id] = ''

    @staticmethod
    def create_figure_plot(figure_size_x, figure_size_y, dpi, hspace='0', wspace='0'):
        figure = Figure(figsize=(int(figure_size_x), int(figure_size_y)), dpi=int(dpi), facecolor='#f0f0f0')
        figure.subplots_adjust(hspace=int(hspace), wspace=int(wspace))
        return figure
