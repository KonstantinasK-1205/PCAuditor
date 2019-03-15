import os
import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure


class NBStress:
    def __init__(self, gui_base, infocollector):
        self.gui_base = gui_base
        self.infocollector = infocollector
        self.stressThread = ['', '', '']

        self.page_box = None
        self.timer_spinbox = None
        self.cpu_stress_bttn = None
        self.gpu_1_stress_bttn = None
        self.gpu_2_stress_bttn = None
        self.all_stress_bttn = None
        self.cancel_bttn = None
        self.temp_plot = None
        self.clock_plot = None
        self.cpu_timer = 0
        self.gpu_timer = 0

        self.ExecutionTime = 0
        self.cpuStressTimer = 0
        self.gpuStressTimer = 0
        self.cooloff_time = 10

        self.isStressingCPU = False
        self.isStressingGPU = False

        self.cpuOverheatingText = ''
        self.gpuOverheatingText = ''

        self.isCPUOverheating = False
        self.isGPUOverheating = False

        self.cpuTempAtOverheat = 0
        self.gpuTempAtOverheat = 0

        self.gpuOffload = os.environ.copy()

        self.cpuClockPlotCol = ["#FF1493", "#F4A460", "#FFFFFF", "#A9A9A9", "#BDB76B", "#CD5C5C", "#008B8B", "#7FFFD4",
                                "#FFA500", "#00FFFF", "#E9967A", "#8B008B", "#B0E0E6", "#4169E1", "#8B4513", "#F5FFFA"]
        self.cpuPlotColors = ["#00d800", "#00b193", "#00c4a4", "#00d8b4", "#00ebc5", "#00b1a2", "#00c4b4", "#00d8c6",
                              "#00ebd8"]
        self.gpuPlotColors = ["#f60000", "#f600f6", "#fff600"]

        self.infocollector.debug_info("Information", "Stress - Variables Initilizated")

    def create_page(self):
        self.page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button_box = Gtk.Box()
        self.timer_spinbox = self.gui_base.create_spin_button(10, 1, 60, 1)
        self.cpu_stress_bttn = self.gui_base.create_button(_text="Start CPU Stress", _function=self.stress_system)
        self.gpu_1_stress_bttn = self.gui_base.create_button(_text="Start 1 GPU Stress", _function=self.stress_system)
        self.gpu_2_stress_bttn = self.gui_base.create_button(_text="Start 2 GPU Stress", _function=self.stress_system)
        self.all_stress_bttn = self.gui_base.create_button(_text="Start ALL Stress", _function=self.stress_system)
        self.all_stress_bttn.set_sensitive(False)
        self.cancel_bttn = self.gui_base.create_button(_text="CANCEL Stress", _function=self.stress_system)
        if not self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
            self.gpu_2_stress_bttn.set_sensitive(False)

        button_box.pack_start(self.timer_spinbox, True, True, 0)
        button_box.pack_start(self.cpu_stress_bttn, True, True, 0)
        button_box.pack_start(self.gpu_1_stress_bttn, True, True, 0)
        button_box.pack_start(self.gpu_2_stress_bttn, True, True, 0)
        button_box.pack_start(self.all_stress_bttn, True, True, 0)
        button_box.pack_start(self.cancel_bttn, True, True, 0)
        self.page_box.pack_start(button_box, False, False, 0)

        temp_plot_figure = self.create_figure_plot(2, 2, 75)
        self.temp_plot = temp_plot_figure.add_subplot(211)
        self.temp_plot.set_facecolor('#262626')

        self.clock_plot = temp_plot_figure.add_subplot(212)
        self.clock_plot.set_facecolor('#262626')

        self.page_box.pack_start(FigureCanvas(temp_plot_figure), True, True, 0)

    def stress_thread(self, update_time, notebook, parent):
        self.ExecutionTime += update_time / 1000
        maximum_cpu_value = 0
        maximum_gpu_value = 0

        self.infocollector.get_sensors_output()
        self.infocollector.get_temperature("CPU")
        self.infocollector.get_temperature("GPU")
        self.infocollector.get_core_clock()
        label = "Stress"

        # Get CPU Clock's in MHz
        if self.infocollector.cpu_Dict["Stats"]['Clock']:
            color_index = 0
            self.clock_plot.clear()
            for _key, _value in self.infocollector.cpu_Dict["Stats"]['Clock'].items():
                self.clock_plot.plot(_value, label=_key, color=self.cpuClockPlotCol[color_index])
                color_index += 1

        # Get CPU Temperature
        if self.infocollector.cpu_Dict["Stats"]['Temps']["Dynamic"]:
            color_index = 0
            self.temp_plot.clear()
            for _key, _value in self.infocollector.cpu_Dict["Stats"]['Temps']['Dynamic'].items():
                if maximum_cpu_value < _value[-1]:
                    maximum_cpu_value = _value[-1]
                self.temp_plot.plot(_value, label=_key, color=self.cpuPlotColors[color_index])
                color_index += 1

            label = ("  Stress\nCPU " + str(maximum_cpu_value) + " C")
            # If Stress is launched on CPU, compare it with max allowed critical temperature
            if self.isStressingCPU and maximum_cpu_value >= self.infocollector.cpu_Dict['Stats']['Temps']["Critical"]:
                if not self.isCPUOverheating:
                    self.cpuTempAtOverheat = maximum_cpu_value
                    self.cpuOverheatingText = "CPU is overheating! Allowed ' " + str(
                        self.infocollector.cpu_Dict['Stats']['Temps'][
                            "Critical"]) + " C' - At the moment it was overheating '" + str(maximum_cpu_value) + "'C"
                    self.gui_base.throw_error_win(parent, "Overheating!", "CPU is overheating!\nAllowed ' " + str(
                        self.infocollector.cpu_Dict['Stats']['Temps']["Critical"]) + " C' - Currently '" + str(
                        maximum_cpu_value) + "'C")
                self.isCPUOverheating = True
            # If Stress isn't launched on CPU, compare it with max allowed temperature
            elif not self.isStressingCPU and maximum_cpu_value >= self.infocollector.cpu_Dict['Stats']['Temps'][
                "Maximum"]:
                if not self.isCPUOverheating:
                    self.cpuTempAtOverheat = maximum_cpu_value
                    self.cpuOverheatingText = "CPU is overheating! Allowed ' " + str(
                        self.infocollector.cpu_Dict['Stats']['Temps'][
                            "Maximum"]) + " C' - At the moment it was overheating '" + str(maximum_cpu_value) + "'C"
                    self.gui_base.throw_error_win(parent, "Overheating!", "CPU is overheating!\nAllowed ' " + str(
                        self.infocollector.cpu_Dict['Stats']['Temps']["Maximum"]) + " C' - Currently '" + str(
                        maximum_cpu_value) + "'C")
                self.isCPUOverheating = True

        # GPU Temperature handling block, adjust label color and throw error if CPU overheats (75c.)
        if self.infocollector.gpu_Dict["Stats"]['Temps']["Dynamic"]:
            color_index = 0
            for _key, _value in self.infocollector.gpu_Dict["Stats"]['Temps']['Dynamic'].items():
                if maximum_gpu_value < _value[-1]:
                    maximum_gpu_value = _value[-1]
                self.temp_plot.plot(_value, label=_key, color=self.gpuPlotColors[color_index])
                color_index += 1

            label += ("\nGPU " + str(maximum_gpu_value) + " C")
            # If Stress is launched on GPU, compare it with max allowed critical temperature
            if self.isStressingGPU and maximum_gpu_value >= self.infocollector.gpu_Dict['Stats']['Temps']["Critical"]:
                if not self.isGPUOverheating:
                    self.gpuTempAtOverheat = maximum_gpu_value
                    self.gpuOverheatingText = "GPU is overheating! Allowed ' " + str(
                        self.infocollector.gpu_Dict['Stats']['Temps'][
                            "Critical"]) + " C' - At the moment it was overheating '" + str(maximum_gpu_value) + "'C"
                    self.gui_base.throw_error_win(parent, "Overheating!", "GPU is overheating!\nAllowed ' " +
                                                  self.infocollector.gpu_Dict['Stats']['Temps'][
                                                      "Critical"] + " C' - Currently '" + str(maximum_gpu_value) + "'C")
                self.isGPUOverheating = True
            # If Stress is launched on GPU, compare it with max allowed critical temperature
            elif not self.isStressingGPU and maximum_gpu_value >= self.infocollector.gpu_Dict['Stats']['Temps'][
                "Maximum"]:
                if not self.isGPUOverheating:
                    self.gpuTempAtOverheat = maximum_gpu_value
                    self.gpuOverheatingText = "GPU is overheating! Allowed ' " + str(
                        self.infocollector.gpu_Dict['Stats']['Temps'][
                            "Maximum"]) + " C' - At the moment it was overheating '" + str(maximum_gpu_value) + "'C"
                    self.gui_base.throw_error_win(parent, "Overheating!", "GPU is overheating!\nAllowed '  " +
                                                  self.infocollector.gpu_Dict['Stats']['Temps'][
                                                      "Maximum"] + " C' - Currently '" + str(maximum_gpu_value) + "'C")
                self.isGPUOverheating = True

        notebook.set_tab_label_text(self.page_box, label)

        self.temp_plot.legend(loc=2)
        self.temp_plot.set_ylim(0, 120)
        self.temp_plot.grid(b=True, which='major', color='#4c4c4c', linestyle='-')

        self.clock_plot.legend(loc=2)
        self.clock_plot.set_ylim(0, self.infocollector.cpu_Dict["Collected"]["Maximum Clock INT"] + 500)
        self.clock_plot.grid(b=True, which='major', color='#4c4c4c', linestyle='-')

        return True

    # THIS FUNCTION NEEDS HEAVY LOOK AND CRYING IN DESPAIR FOR CLEANING IT
    def stress_system(self, button='', _data=''):  # check for crashes when thread amount is bad
        if isinstance(button, Gtk.Button):
            label = button.get_label()
        else:
            label = ''
        timer = self.timer_spinbox.get_value() * 60 + self.cooloff_time
        if "CPU" in label:
            subprocess.Popen(
                ["stress-ng", "--matrix", "0" "-c", self.infocollector.cpu_Dict["GUI"]["Thread Amount"].get_text(),
                 "--timeout", str(timer - self.cooloff_time)])

            self.stressThread[0] = GLib.timeout_add(1000, self.cpu_stress, 1, timer)
            self.cpu_stress_bttn.set_sensitive(False)
            self.isStressingCPU = True
        elif "1 GPU" in label:
            try:
                subprocess.Popen(["/root/GUI/Stress/GpuTest", "/test=fur", "/display_osi"])
            except FileNotFoundError:
                subprocess.Popen(["/home/konstantin/Programs/Stress/GpuTest", "/test=fur", "/display_osi"])

            self.stressThread[1] = GLib.timeout_add(1000, self.gpu_stress, 1, timer, self.gpu_1_stress_bttn,
                                                    "Start 1 GPU Stress")
            self.gpu_1_stress_bttn.set_sensitive(False)
            self.isStressingGPU = True
        elif "2 GPU" in label:
            self.detect_dri_prime(self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"])

            subprocess.Popen(["/root/GUI/Stress/GpuTest", "/test=fur", "/display_osi"], env=self.gpuOffload)

            self.stressThread[1] = GLib.timeout_add(1000, self.gpu_stress, 1, timer, self.gpu_2_stress_bttn,
                                                    "Start 2 GPU Stress")
            self.gpu_2_stress_bttn.set_sensitive(False)
            self.isStressingGPU = True
        elif "ALL" in label:
            if self.gpuOffload == "":
                self.detect_dri_prime(self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"])
            if self.gpuOffload == "":
                self.detect_dri_prime(self.infocollector.gpu_Dict["Collected"]["1 Manufacturer"])

            subprocess.Popen(["stress-ng", "-c", self.infocollector.cpu_Dict["GUI"]["Thread Amount"].get_text(),
                              "--timeout", str(timer - self.cooloff_time)])
            subprocess.Popen(["/root/GUI/Stress/GpuTest", "/test=fur", "/display_osi"], env=self.gpuOffload)

            self.stressThread[2] = GLib.timeout_add(1000, self.full_stress, 1, timer)
            self.cpu_stress_bttn.set_sensitive(False)
            self.gpu_1_stress_bttn.set_sensitive(False)
            self.gpu_2_stress_bttn.set_sensitive(False)
            self.all_stress_bttn.set_sensitive(False)
            self.isStressingCPU = True
            self.isStressingGPU = True
        elif "CANCEL" in label:
            subprocess.Popen(["pkill", "-9", "stress-ng"])
            subprocess.Popen(["pkill", "-9", "GpuTest"])

            if self.stressThread[0]:
                GLib.source_remove(self.stressThread[0])
                self.stressThread[0] = ''
            if self.stressThread[1]:
                GLib.source_remove(self.stressThread[1])
                self.stressThread[1] = ''
            if self.stressThread[2]:
                GLib.source_remove(self.stressThread[2])
                self.stressThread[2] = ''

            self.cpu_stress_bttn.set_sensitive(True)
            self.gpu_1_stress_bttn.set_sensitive(True)
            if not self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
                self.gpu_2_stress_bttn.set_sensitive(False)
            else:
                self.gpu_2_stress_bttn.set_sensitive(True)
            self.all_stress_bttn.set_sensitive(False)
            self.cancel_bttn.set_sensitive(True)

            self.cpu_stress_bttn.set_label("Start CPU Stress")
            self.gpu_1_stress_bttn.set_label("Start 1 GPU Stress")
            self.gpu_2_stress_bttn.set_label("Start 2 GPU Stress")
            self.all_stress_bttn.set_label("Start ALL Stress")

            self.cpu_timer = 0
            self.gpu_timer = 0

    def detect_dri_prime(self, string):
        if "nvidia" in string.lower() or "amd" in string.lower():
            self.gpuOffload["DRI_PRIME"] = "1"
        else:
            self.gpuOffload[""] = ""

    def cpu_stress(self, update_time, timer):
        self.cpuStressTimer += update_time
        if self.cpuStressTimer >= timer:
            self.cancel_cpu_stress()
            return False
        else:
            label = "CPU Stress | " + str(timer - self.cpuStressTimer)
            self.cpu_stress_bttn.set_label(label)
        return True

    def gpu_stress(self, update_time, timer, button, _text):
        self.gpuStressTimer += update_time
        gpu_timeleft = timer - self.gpuStressTimer
        if self.cooloff_time > gpu_timeleft:
            subprocess.Popen(["pkill", "-9", "GpuTest"])
        if 0 >= gpu_timeleft:
            self.cancel_gpu_stress()
            return False
        else:
            label = "GPU Stress | " + str(timer - self.gpuStressTimer)
            button.set_label(label)
        return True

    def full_stress(self, update_time, timer):
        self.cpuStressTimer += update_time
        self.gpuStressTimer += update_time
        gpu_timeleft = timer - self.gpuStressTimer
        if self.cooloff_time > gpu_timeleft:
            subprocess.Popen(["pkill", "-9", "GpuTest"])
        if self.cpuStressTimer >= timer and self.gpuStressTimer >= timer:
            self.cpu_stress_bttn.set_label("Start CPU Stress")
            self.gpu_1_stress_bttn.set_label("Start 1 GPU Stress")
            self.gpu_2_stress_bttn.set_label("Start 2 GPU Stress")
            self.cpu_stress_bttn.set_sensitive(True)
            self.gpu_1_stress_bttn.set_sensitive(True)
            self.gpu_2_stress_bttn.set_sensitive(True)
            #            self.all_stress_bttn.set_sensitive(True)
            self.cpuStressTimer = 0
            self.gpuStressTimer = 0
            self.isStressingCPU = False
            self.isStressingGPU = False
            return False
        else:
            cpu_label = "CPU Stress | " + str(timer - self.cpuStressTimer)
            gpu_label = "GPU Stress | " + str(timer - self.gpuStressTimer)
            self.cpu_stress_bttn.set_label(cpu_label)
            self.gpu_1_stress_bttn.set_label(gpu_label)
            self.gpu_2_stress_bttn.set_label(gpu_label)
        return True

    def cancel_cpu_stress(self):
        self.cpu_stress_bttn.set_label("Start CPU Stress")
        self.cpu_stress_bttn.set_sensitive(True)
        self.isStressingCPU = False
        self.cpuStressTimer = 0

    def cancel_gpu_stress(self):
        self.gpu_1_stress_bttn.set_label("Start 1 GPU Stress")
        self.gpu_1_stress_bttn.set_sensitive(True)
        self.gpu_2_stress_bttn.set_label("Start 2 GPU Stress")
        if not self.infocollector.gpu_Dict["Collected"]["2 Manufacturer"]:
            self.gpu_2_stress_bttn.set_sensitive(False)
        else:
            self.gpu_2_stress_bttn.set_sensitive(True)

        self.isStressingGPU = False
        self.gpuStressTimer = 0
        if self.stressThread[1]:
            GLib.source_remove(self.stressThread[1])
            self.stressThread[1] = None

    @staticmethod
    def create_figure_plot(figure_size_x, figure_size_y, dpi, hspace='0', wspace='0'):
        figure = Figure(figsize=(int(figure_size_x), int(figure_size_y)), dpi=int(dpi), facecolor='#f0f0f0')
        figure.subplots_adjust(hspace=int(hspace), wspace=int(wspace))
        return figure
