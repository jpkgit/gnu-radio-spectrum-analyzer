#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: spectrum_analyzer
# Author: JK
# GNU Radio version: v3.11.0.0git-682-gdd442bda

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
import sip
from threading import Thread



class spectrum_analyzer(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "spectrum_analyzer", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("spectrum_analyzer")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "spectrum_analyzer")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.variable_qtgui_range_sweep_speed = variable_qtgui_range_sweep_speed = 0.005
        self.variable_qtgui_check_box_sweep = variable_qtgui_check_box_sweep = 0
        self.sample_rate = sample_rate = 1000000
        self.samp_rate = samp_rate = 1000000
        self.if_gain = if_gain = 7
        self.gain = gain = 15
        self.freq = freq = 1e6
        self.bandwidth = bandwidth = 10000000

        ##################################################
        # Blocks
        ##################################################

        self._if_gain_range = qtgui.Range(0, 40, 1, 7, 200)
        self._if_gain_win = qtgui.RangeWidget(self._if_gain_range, self.set_if_gain, "IF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._if_gain_win)
        self._gain_range = qtgui.Range(0, 62, 1, 15, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "VGA Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
        self._freq_range = qtgui.Range(1000000, 6000000000, 8000000, 2400000000, 200)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "freq", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self._bandwidth_range = qtgui.Range(1000, 10000000, 1000, 10000000, 200)
        self._bandwidth_win = qtgui.RangeWidget(self._bandwidth_range, self.set_bandwidth, "Bandwidth", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._bandwidth_win)
        self._variable_qtgui_range_sweep_speed_range = qtgui.Range(0.001, 100, 0.001, 0.005, 200)
        self._variable_qtgui_range_sweep_speed_win = qtgui.RangeWidget(self._variable_qtgui_range_sweep_speed_range, self.set_variable_qtgui_range_sweep_speed, "Sweep Speed (ms)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._variable_qtgui_range_sweep_speed_win)
        _variable_qtgui_check_box_sweep_check_box = Qt.QCheckBox("Sweep")
        self._variable_qtgui_check_box_sweep_choices = {True: True, False: False}
        self._variable_qtgui_check_box_sweep_choices_inv = dict((v,k) for k,v in self._variable_qtgui_check_box_sweep_choices.items())
        self._variable_qtgui_check_box_sweep_callback = lambda i: Qt.QMetaObject.invokeMethod(_variable_qtgui_check_box_sweep_check_box, "setChecked", Qt.Q_ARG("bool", self._variable_qtgui_check_box_sweep_choices_inv[i]))
        self._variable_qtgui_check_box_sweep_callback(self.variable_qtgui_check_box_sweep)
        _variable_qtgui_check_box_sweep_check_box.stateChanged.connect(lambda i: self.set_variable_qtgui_check_box_sweep(self._variable_qtgui_check_box_sweep_choices[bool(i)]))
        self.top_layout.addWidget(_variable_qtgui_check_box_sweep_check_box)
        self._sample_rate_range = qtgui.Range(1000000, 20000000, 1000000, 1000000, 200)
        self._sample_rate_win = qtgui.RangeWidget(self._sample_rate_range, self.set_sample_rate, "Sample Rate", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._sample_rate_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            4096, #fftsize
            window.WIN_HAMMING, #wintype
            freq, #fc
            bandwidth, #bw
            "Spectrum Analyzer", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/20)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + "hackrf=0"
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(gain, 0)
        self.osmosdr_source_0.set_if_gain(if_gain, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(bandwidth, 0)

        # Start the background thread
        self.running = True
        self.thread = Thread(target=self.update_freq)
        self.thread.start()


        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.qtgui_sink_x_0, 0))

    def update_freq(self):
        counter = 0

        freqs_to_scan = [1.727e9, 1.775e9, 1.902e9] 
        index = 0

        while self.running:

            if index < 0  or index > 2:
                index = 0
                     
            self.set_freq(freqs_to_scan[index])
            index = index + 1
            time.sleep(5)

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "spectrum_analyzer")
        self.settings.setValue("geometry", self.saveGeometry())

        self.running = False
        self.thread.join()
        #self.root.destroy()

        self.stop()
        self.wait()

        event.accept()

    def get_variable_qtgui_range_sweep_speed(self):
        return self.variable_qtgui_range_sweep_speed

    def set_variable_qtgui_range_sweep_speed(self, variable_qtgui_range_sweep_speed):
        self.variable_qtgui_range_sweep_speed = variable_qtgui_range_sweep_speed

    def get_variable_qtgui_check_box_sweep(self):
        return self.variable_qtgui_check_box_sweep

    def set_variable_qtgui_check_box_sweep(self, variable_qtgui_check_box_sweep):
        self.variable_qtgui_check_box_sweep = variable_qtgui_check_box_sweep
        self._variable_qtgui_check_box_sweep_callback(self.variable_qtgui_check_box_sweep)

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.osmosdr_source_0.set_if_gain(self.if_gain, 0)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.osmosdr_source_0.set_gain(self.gain, 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.bandwidth)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.osmosdr_source_0.set_bandwidth(self.bandwidth, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.bandwidth)




def main(top_block_cls=spectrum_analyzer, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start(1)

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
