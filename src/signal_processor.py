import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as ss
from enum import auto, Enum

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
            self.zi[filter_type] = ss.lfilter_zi(b, a) * x #x[0]
        y, self.zi[filter_type] = ss.lfilter(b, a, [x], zi=self.zi[filter_type]) #x
        return y[0] #y

    def use_all_filters(self, data_point):
        data_point = self.filter_in_real_time(data_point, FilterType.highpass)
        data_point = self.filter_in_real_time(data_point, FilterType.bandstop)
        data_point = self.filter_in_real_time(data_point, FilterType.lowpass)
        return data_point

    def measure_heart_rate(self, s):
        peaks_indices, _ = ss.find_peaks(s, height=400, distance=66)
        distances = np.diff(peaks_indices)
        average_distance = np.mean(distances)
        return '{:.0f}'.format(self.Fs * NUMBER_OF_SEC_IN_ONE_MIN / average_distance)

def read_from_file(filename):
    with open(filename) as f:
        lines = [float(line.rstrip()) for line in f.readlines()]
    return np.array(lines)


def plot(s, Fs):
    #t = np.arange(0, len(s)/Fs, 1/Fs)
    x = np.arange(0,len(s))
    plt.plot(x, s)
    plt.grid('on')


# noinspection PyShadowingNames
def filter_signal_offline(s, Fs):
    [b, a] = ss.butter(N=2, Wn=0.5, btype='highpass', fs=Fs)
    # plot_filter_characteristics(b, a, Fs)
    s = ss.lfilter(b, a, s)
    [b, a] = ss.butter(N=5, Wn=(49, 51), btype='bandstop', fs=Fs)
    # plot_filter_characteristics(b, a, Fs)
    s = ss.lfilter(b, a, s)
    [b, a] = ss.butter(N=10, Wn=40, btype='lowpass', fs=Fs)
    #plot_filter_characteristics(b, a, Fs)
    s = ss.lfilter(b, a, s)
    return s

def plot_filter_characteristics(b, a, Fs):
    W, h = ss.freqz(b, a)
    f = W * Fs / (2 * np.pi)
    angle = np.unwrap(np.angle(h))
    plt.figure()
    plt.subplot(121)
    plt.plot(f, abs(h))
    plt.grid('on')
    plt.xlim([0, 64])
    plt.subplot(122)
    plt.plot(f, angle, 'g')
    plt.grid('on')
    plt.xlim([0, 64])


if __name__ == '__main__':
    # filename = r'..\data\2023-02-01_120409.txt' # BAD
    # filename = r'..\data\2023-02-01_120724.txt' # BAD
    # filename = r'..\data\2023-02-01_121032.txt' # OK
    # filename = r'..\data\2023-02-01_153643.txt' # OK
    # filename = r'..\data\2023-02-01_153853.txt' # OK
    # filename = r'..\data\2023-02-01_155235.txt' # OK
    # filename = r'..\data\2023-02-01_155325.txt' # MEH
    # filename = r'..\data\2023-02-01_155402.txt' # BAD
    # filename = r'..\data\2023-02-01_155958.txt' # MEH - MY ECG
    filename = r'..\data\2023-02-04_194943.txt'

    s = read_from_file(filename)
    Fs = 200
    print(s)
    s_filtered = filter_signal_offline(s, Fs)

    peaks_indices, _ = ss.find_peaks(s_filtered, height=400, distance=66)
    distances = np.diff(peaks_indices)
    average_distance = np.mean(distances)
    print('HR: {:.0f}'.format(Fs*NUMBER_OF_SEC_IN_ONE_MIN/average_distance))

    plt.figure()
    plt.subplot(2, 1, 1)
    plot(s, Fs)
    plt.subplot(2, 1, 2)
    plot(s_filtered, Fs)
    plt.plot(peaks_indices, s_filtered[peaks_indices], 'x')
    plt.show()

    # Test to check if filtering online and offline works in the same way
    # sp = SignalProcessor(Fs)
    # s_filtered2 = []
    # for x in s:
    #     s_filtered2.append(sp.use_all_filters(x))
    # s_filtered2 = np.array(s_filtered2)
    #
    # plt.figure()
    # plt.subplot(3, 1, 1)
    # plot(s, Fs)
    # plt.subplot(3, 1, 2)
    # plot(s_filtered, Fs)
    # plt.subplot(3, 1, 3)
    # plot(s_filtered2, Fs)
    # plt.show()

    # print(all(s_filtered[8400:] == s_filtered2[8400:]))
    # print(type(s_filtered))
    # print(type(s_filtered2))
    # print(len(s_filtered))
    # print(len(s_filtered2))
    # print(s_filtered[8400:])
    # print(s_filtered2[8400:])
    # for i, x in enumerate(s_filtered[8400:]):
    #     if x != s_filtered2[8400:][i]:
    #         print(x, s_filtered2[8400:][i])


