#!/usr/bin/env python3
from glob import glob
import pathlib

import matplotlib.pyplot as plot
from matplotlib.animation import FuncAnimation


def read_first_line(filename):
    with open(filename) as f:
        return f.readline().strip()


thermal_zones = {
    # path: caption

    (path := pathlib.Path(p)):

        '{} ({})'.format(path.name, read_first_line(path / 'type'))

    for p in glob('/sys/class/thermal/thermal_zone*')
}


all_regulators = {
    # path: caption
    (path := pathlib.Path(p)):

        '{} ({})'.format(read_first_line(path / 'name'),
                         read_first_line(path / 'type'))

    for p in glob('/sys/class/regulator/regulator.*')
}

regulators = {
    path: caption

    for path, caption in all_regulators.items()
    if (path / 'microvolts').exists()
}


cpu_freqs = {
    # path: caption

    (path := pathlib.Path(p).parent):

        path.name

    for p in glob('/sys/devices/system/cpu/cpu*/cpufreq')
}


def now():
    from datetime import datetime
    return datetime.now()


def parse_celsius(zone_path):
    string = read_first_line(zone_path / 'temp')
    return float(string) / 1e3

def parse_hertz(cpu_path):
    string = read_first_line(cpu_path / 'cpufreq/scaling_cur_freq')
    return float(string)

def parse_volts(reg_path):
    string = read_first_line(reg_path / 'microvolts')
    return float(string) / 1000



SAMPLING_PERIOD_MS = 100

(fig, (ax1, ax2, ax3)) = plot.subplots(1, 3, figsize=(12, 8))


thermal_meas = {path: list() for path in thermal_zones.keys()}
regulator_meas = {path: list() for path in regulators.keys()}
cpu_freq_meas = {path: list() for path in cpu_freqs.keys()}

def animate_figure(frame):
    ax1.cla()
    ax2.cla()
    ax3.cla()

    ax1.set_title('Thermal zones (Celsius)')
    ax2.set_title('Regulators (volts)')
    ax3.set_title('CPU Frequency (Hz)')

    for key, meas in thermal_meas.items():
        meas.append(parse_celsius(key))
        ax1.plot(meas, label=thermal_zones[key])
        ax1.legend()

    for key, meas in regulator_meas.items():
        meas.append(parse_volts(key))
        ax2.plot(meas, label=regulators[key])
        ax2.legend()

    for key, meas in cpu_freq_meas.items():
        meas.append(parse_hertz(key))
        ax3.plot(meas, label=cpu_freqs[key])
        ax3.set_ylim(0)
        ax3.legend()

animation = FuncAnimation(fig, animate_figure, interval=SAMPLING_PERIOD_MS)

plot.show()
