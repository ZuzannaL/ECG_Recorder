import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as ss
from enum import auto, Enum
import heartpy as hp

NUMBER_OF_SEC_IN_ONE_MIN = 60

PQRST = np.array([4.41482618, 7.85653347, 25.84121989, 46.75581946,
                  50.83381902, 25.41901536, -21.75812795, -63.20311102,
                  -72.71279981, -49.03472082, -14.95439925, 5.94865221,
                  5.69025298, -11.97565694, -39.29386757, -62.58525323,
                  -62.18350527, -27.1123294 , 30.26955494, 83.6813986 ,
                  119.3501638 , 148.00364559, 190.94392147, 257.55508791,
                  331.10815039, 370.08128652, 330.45363897, 200.44193852,
                  18.54102904, -145.31094118, -231.24356965, -221.43951018,
                  -143.46839843, -49.05906436, 15.0990981 , 29.59255684,
                  8.23979074, -17.33185772, -26.64900458, -26.45151322,
                  -34.86402437, -53.59551358, -65.25699953, -56.96484008,
                  -35.5089768 , -16.86804537, -9.44232856, -10.58153935,
                  -13.33518165, -13.70277696, -13.69744726, -16.73186356,
                  -18.52018119, -7.24943199, 21.62926674, 53.52362217,
                  65.43013106, 51.37006101, 31.77874084, 30.54725165,
                  44.09921493, 44.09364219, 16.65507698, -11.82429386,
                  -2.42588301, 45.62498402, 88.27266985, 86.79908517,
                  53.06914133, 33.27271388, 51.99795055, 86.88320704,
                  101.13653957, 87.98311107, 73.708675  , 83.34929361,
                  113.35665489, 138.4958345 , 140.62061425, 127.54477317,
                  122.8357265 , 138.62161937, 162.14910028, 170.54434796,
                  155.73033006, 131.75245786, 118.30226917, 119.2560339 ,
                  118.51852173, 97.49440898, 56.02420801, 13.2350197 ,
                  -13.57605165, -26.59750229, -39.83234258, -57.98907405,
                  -71.12318426, -69.86009931, -57.86404449, -46.70979571,
                  -44.14492647, -50.46549323, -62.11563712, -74.20305195,
                  -80.76699439, -78.21436995, -71.41308061, -71.58789709,
                  -82.27676596, -91.51961739, -86.81422007, -74.3902697 ,
                  -70.78878169, -75.81167473, -69.98258559, -44.16270243,
                  -16.9745266 , -13.39573078, -35.78296381, -64.82923264,
                  -81.86114117, -81.08559281, -65.28942429, -42.44229945,
                  -27.72473111, -34.39385761, -53.15643835, -52.92739546,
                  -18.4739059 , 20.1553234])

QRS = np.array([ -62.18350527,  -27.1123294 ,   30.26955494,   83.6813986 ,
        119.3501638 ,  148.00364559,  190.94392147,  257.55508791,
        331.10815039,  370.08128652,  330.45363897,  200.44193852,
         18.54102904, -145.31094118])

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

    def find_hr_using_find_peaks(self, s):
        peaks_indices, _ = ss.find_peaks(s, height=350, distance=66)
        distances = np.diff(peaks_indices)
        average_distance = np.mean(distances)
        hr = self.Fs * NUMBER_OF_SEC_IN_ONE_MIN / average_distance
        return hr

    def find_hr_using_heartpy(self, s):
        _, measures = self.make_ecg_analysis(np.array(s))
        if measures is None:
            return np.nan
        hr = float(measures['bpm'])
        return hr

    def find_hr_using_find_peaks_and_correlation(self, s, peak=PQRST):
        correlation = np.correlate(s, peak) # todo test ss.correlate
        normalized_correlation = correlation / max(correlation)
        peaks_indices, _ = ss.find_peaks(normalized_correlation, height=0.5, distance=66)
        distances = np.diff(peaks_indices)
        average_distance = np.mean(distances)
        hr = self.Fs * NUMBER_OF_SEC_IN_ONE_MIN / average_distance
        return hr

    def measure_heart_rate(self, s):
        option = 3
        if option == 1:
            hr = self.find_hr_using_find_peaks(s)
        elif option == 2:
            hr = self.find_hr_using_heartpy(s)
        elif option == 3:
            hr = self.find_hr_using_find_peaks_and_correlation(s)

        if hr < 30 or hr > 200:
            hr = np.nan
        if not np.isnan(hr):
            hr = int(hr)
        return hr

    def make_ecg_analysis(self, s):
        try:
            working_data, measures = hp.process(s, self.Fs, clean_rr=True, windowsize=1.5)
            return working_data, measures
        except hp.exceptions.BadSignalWarning:
            return None, None

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
    filename = r'..\data\2023-02-01_155235.txt' # OK
    # filename = r'..\data\2023-02-01_155325.txt' # MEH
    # filename = r'..\data\2023-02-01_155402.txt' # BAD
    # filename = r'..\data\2023-02-01_155958.txt' # MEH - MY ECG

    # filename = r'..\data\2023-02-04_193616.txt'
    # filename = r'..\data\2023-02-04_194228.txt'
    # filename = r'..\data\2023-02-04_194943.txt'
    # filename = r'..\data\2023-02-05_034912.txt'
    # filename = r'..\data\2023-02-05_035049.txt'


    s = read_from_file(filename)
    Fs = 200

    working_data, measures = hp.process(s, Fs, report_time=True)
    # print(measures['bpm'])  # returns BPM value
    # print(measures['rmssd'])  # returns RMSSD HRV measure
    for x in measures.items():
        print(x)

    print(s)
    s_filtered = filter_signal_offline(s, Fs)

    plt.figure()
    plt.plot(np.fft.rfftfreq(len(s_filtered), 1./Fs), abs(np.fft.rfft(s_filtered))**2)
    plt.show()

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


