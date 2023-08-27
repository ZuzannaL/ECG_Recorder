import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as ss
from enum import auto, Enum
from port_handler import convert_units_to_volts

matplotlib_plots_params = {'font.family': 'Calibri',
                           'font.size': 12,
                           'legend.fontsize': 12,
                           'axes.labelsize': 14,
                           'axes.titlesize': 20,
                           'xtick.labelsize': 12,
                           'ytick.labelsize': 12}
plt.rcParams.update(matplotlib_plots_params)

NUMBER_OF_SEC_IN_ONE_MIN = 60


class FilterType(Enum):
    highpass = auto()
    bandstop = auto()
    lowpass = auto()


class SignalProcessor:
    def __init__(self, Fs):
        self.Fs = Fs
        self.zi = {
            FilterType.highpass: None,
            FilterType.bandstop: None,
            FilterType.lowpass: None,
        }
        self.ba = {
            FilterType.highpass: ss.butter(N=2, Wn=0.5, btype='highpass', fs=self.Fs),
            FilterType.bandstop: ss.butter(N=5, Wn=(49, 51), btype='bandstop', fs=self.Fs),
            FilterType.lowpass: ss.butter(N=10, Wn=40, btype='lowpass', fs=self.Fs),
        }

    def filter_in_real_time(self, x, filter_type):
        [b, a] = self.ba[filter_type]
        if self.zi[filter_type] is None:
            self.zi[filter_type] = ss.lfilter_zi(b, a) * x
        y, self.zi[filter_type] = ss.lfilter(b, a, [x], zi=self.zi[filter_type])
        return y[0]

    def use_all_filters(self, data_point):
        data_point = self.filter_in_real_time(data_point, FilterType.highpass)
        data_point = self.filter_in_real_time(data_point, FilterType.bandstop)
        data_point = self.filter_in_real_time(data_point, FilterType.lowpass)
        return data_point

    @staticmethod
    def moving_average(x, w):
        z = np.zeros(w // 2 - 1)
        ma = np.convolve(x, np.ones(w), 'valid') / w
        con = np.concatenate([z, ma, z])
        return con

    def find_R_peaks(self, s, window_size=21):
        s_ma = self.moving_average(s, 5)
        diff_abs2 = np.abs(np.diff(s_ma))**2
        peaks_indices, _ = ss.find_peaks(diff_abs2, height=5000, distance=66)

        maximized_peaks_indices = []
        mid = window_size // 2
        for i in peaks_indices:
            # handle edge case of the peak found
            # at the beginning of the signal
            window_start_index = max(0, i - mid)
            # handle edge case of the peak found
            # at the end of the signal
            window_end_index = min(len(s), i + mid + 1)
            windowed_s = s[window_start_index:window_end_index]
            argmax_index = np.argmax(np.array(windowed_s))
            new_peak_index = window_start_index + argmax_index
            maximized_peaks_indices.append(new_peak_index)
        return np.array(maximized_peaks_indices)

    def find_hr_from_peaks_indices(self, peaks_indices):
        distances = np.diff(peaks_indices)
        average_distance = np.mean(distances)
        return self.Fs * NUMBER_OF_SEC_IN_ONE_MIN / average_distance

    def find_hr(self, s):
        peaks_indices = self.find_R_peaks(s)
        hr = self.find_hr_from_peaks_indices(peaks_indices)

        if hr < 30 or hr > 200:
            hr = np.nan
        if not np.isnan(hr):
            hr = int(hr)
        return hr

    def make_ecg_analysis_on_peaks_indices(self, peaks_indices):
        distances = np.diff(peaks_indices) # distances in number of samples

        rr_list = (1000/self.Fs)*distances # distances in miliseconds
        rr_diff = np.diff(rr_list)
        rr_sqdiff = np.power(rr_diff, 2)

        keys = ['bpm', 'ibi', 'sdnn', 'sdsd', 'rmssd', 'pnn20', 'pnn50']
        measures = {}
        for key in keys:
            measures[key] = np.nan

        measures['bpm'] = 60000 / np.mean(rr_list)
        measures['ibi'] = np.mean(rr_list)
        measures['sdnn'] = np.std(rr_list)
        measures['sdsd'] = np.std(rr_diff)
        measures['rmssd'] = np.sqrt(np.mean(rr_sqdiff))

        nn20 = rr_diff[np.where(rr_diff > 20.0)]
        try:
            measures['pnn20'] = float(len(nn20)) / float(len(rr_diff))
        except:
            measures['pnn20'] = np.nan

        nn50 = rr_diff[np.where(rr_diff > 50.0)]
        try:
            measures['pnn50'] = float(len(nn50)) / float(len(rr_diff))
        except:
            measures['pnn50'] = np.nan

        return measures

    def make_ecg_analysis(self, s):
        peaks_indices = self.find_R_peaks(s)
        return self.make_ecg_analysis_on_peaks_indices(peaks_indices)


def read_from_file(filename):
    with open(filename) as f:
        lines = [float(line.rstrip()) for line in f.readlines()]
    return np.array(lines)


def plot_filter_characteristics(b, a, Fs):
    W, h = ss.freqz(b, a)
    f = W * Fs / (2 * np.pi)
    angle = np.unwrap(np.angle(h))
    plt.figure()
    plt.subplot(121)
    plt.plot(f, abs(h))
    plt.grid('on')
    plt.xlim([0, 64])
    plt.xlabel('Częstotliwość [Hz]') # Frequency Częstotliwość
    plt.ylabel('Moduł transmitancji') # Transfer function module Moduł transmitancji
    plt.subplot(122)
    plt.plot(f, angle, 'g')
    plt.grid('on')
    plt.xlim([0, 64])
    plt.xlabel('Częstotliwość [Hz]') # Frequency Częstotliwość
    plt.ylabel('Faza') # Phase Faza
    plt.tight_layout()


def plot_all_filters_characteristics(sp):
    [b, a] = sp.ba[FilterType.highpass]
    plot_filter_characteristics(b, a, sp.Fs)
    [b, a] = sp.ba[FilterType.bandstop]
    plot_filter_characteristics(b, a, sp.Fs)
    [b, a] = sp.ba[FilterType.lowpass]
    plot_filter_characteristics(b, a, sp.Fs)
    plt.show()


def main():
    filename = r'..\data\example_ecg_data1.txt'
    # filename = r'..\data\example_ecg_data2.txt'

    s = read_from_file(filename)
    Fs = 200
    sp = SignalProcessor(Fs)
    # plot_all_filters_characteristics(sp)

    s = s[149*Fs:161*Fs]

    s_filtered = []
    for x in s:
        s_filtered.append(sp.use_all_filters(x))
    s_filtered = np.array(s_filtered)

    peaks_indices = sp.find_R_peaks(s_filtered)
    measures = sp.make_ecg_analysis_on_peaks_indices(peaks_indices)
    for measure, value in measures.items():
        print(f'{measure}: {value:.2f}')

    # Plots
    x = np.arange(0, len(s))

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(x/Fs, convert_units_to_volts(s)*1000)
    plt.grid('on')
    plt.ylabel('Amplituda [mV]')
    plt.subplot(2, 1, 2)
    plt.plot(x/Fs, convert_units_to_volts(s_filtered)*1000)
    plt.grid('on')
    plt.xlabel('Czas [s]')
    plt.ylabel('Amplituda [mV]')
    plt.tight_layout()

    plt.figure()
    plt.plot(x/Fs, convert_units_to_volts(s_filtered)*1000)
    plt.plot(peaks_indices/Fs, convert_units_to_volts(s_filtered[peaks_indices])*1000, 'x')
    plt.grid('on')
    plt.xlabel('Czas [s]')
    plt.ylabel('Amplituda [mV]')
    plt.tight_layout()

    plt.show()


if __name__ == '__main__':
    main()
