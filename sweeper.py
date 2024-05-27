#!/usr/bin/env python3
from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import osmosdr
import time
import sip

from gnuradio import gr, blocks, analog
from gnuradio import filter
from gnuradio.eng_option import eng_option
from gnuradio import uhd
#from gnuradio import hackrf
import time

class SpectrumSweeper(gr.top_block):
    def __init__(self, start_freq=100e6, end_freq=400e6, step_freq=10e6, samp_rate=10e6, duration=1):
        gr.top_block.__init__(self, "Spectrum Sweeper")

        self.start_freq = start_freq
        self.end_freq = end_freq
        self.step_freq = step_freq
        self.samp_rate = samp_rate
        self.duration = duration
        
        # HackRF source
        self.hackrf_source = hackrf.source('', samp_rate, True)
        self.hackrf_source.set_sample_rate(samp_rate)
        self.hackrf_source.set_center_freq(start_freq)
        self.hackrf_source.set_gain(20)
        
        # Throttle
        self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)

        # File sink
        self.sink = blocks.file_sink(gr.sizeof_gr_complex, 'sweep_output.dat')

        # Connections
        self.connect((self.hackrf_source, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.sink, 0))
    
    def sweep(self):
        current_freq = self.start_freq
        while current_freq <= self.end_freq:
            print(f"Setting frequency to {current_freq / 1e6} MHz")
            self.hackrf_source.set_center_freq(current_freq)
            self.start()
            time.sleep(self.duration)
            self.stop()
            self.wait()
            current_freq += self.step_freq

if __name__ == "__main__":
    start_freq = 100e6   # 100 MHz
    end_freq = 400e6     # 400 MHz
    step_freq = 10e6     # 10 MHz step
    samp_rate = 10e6     # 10 MS/s
    duration = 1         # 1 second per frequency step

    sweeper = SpectrumSweeper(start_freq, end_freq, step_freq, samp_rate, duration)
    sweeper.sweep()
