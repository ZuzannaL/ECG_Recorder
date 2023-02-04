import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as ss


class SignalProcessor:
    def __init__(self, Fs):
        self.Fs = Fs
        self.highpass_zi = None
        self.bandstop_zi = None
        self.lowpass_zi = None
        self.highpass_ba = ss.butter(N=2, Wn=0.5, btype='highpass', fs=self.Fs)
        self.bandstop_ba = ss.butter(N=5, Wn=(49, 51), btype='bandstop', fs=self.Fs)
        self.lowpass_ba = ss.butter(N=10, Wn=40, btype='lowpass', fs=self.Fs)

    def filter_highpass(self, x):
        [b, a] = self.highpass_ba
        if self.highpass_zi is None:
            self.highpass_zi = ss.lfilter_zi(b, a) * x #x[0]
        y, self.highpass_zi = ss.lfilter(b, a, [x], zi=self.highpass_zi) #x
        return y[0] #y

    def filter_bandstop(self, x):
        [b, a] = self.bandstop_ba
        if self.bandstop_zi is None:
            self.bandstop_zi = ss.lfilter_zi(b, a) * x #x[0]
        y, self.bandstop_zi = ss.lfilter(b, a, [x], zi=self.bandstop_zi) #x
        return y[0] #y

    def filter_lowpass(self, x):
        [b, a] = self.lowpass_ba
        if self.lowpass_zi is None:
            self.lowpass_zi = ss.lfilter_zi(b, a) * x #x[0]
        y, self.lowpass_zi = ss.lfilter(b, a, [x], zi=self.lowpass_zi) #x
        return y[0] #y

    def filter_in_real_time(self, data_point):
        data_point = self.filter_highpass(data_point)
        data_point = self.filter_bandstop(data_point)
        data_point = self.filter_lowpass(data_point)
        return data_point

def read_from_file(filename):
    with open(filename) as f:
        lines = [int(line.rstrip()) for line in f.readlines()]
    return np.array(lines)


def plot(s, Fs):
    t = np.arange(0, len(s)/Fs, 1/Fs)
    plt.plot(t[2*Fs:10*Fs], s[2*Fs:10*Fs])
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
    filename = r'..\data\2023-02-01_153643.txt' # OK
    # filename = r'..\data\2023-02-01_153853.txt' # OK
    # filename = r'..\data\2023-02-01_155235.txt' # OK
    # filename = r'..\data\2023-02-01_155325.txt' # MEH
    # filename = r'..\data\2023-02-01_155402.txt' # BAD
    # filename = r'..\data\2023-02-01_155958.txt' # MEH - MY ECG

    s = read_from_file(filename)
    Fs = 200
    #print(s)
    s_filtered = filter_signal_offline(s, Fs)

    sp = SignalProcessor(Fs)
    s_filtered2 = []
    for x in s:
        s_filtered2.append(sp.filter_in_real_time(x))
    s_filtered2 = np.array(s_filtered2)

    plt.figure()
    plt.subplot(3, 1, 1)
    plot(s, Fs)
    plt.subplot(3, 1, 2)
    plot(s_filtered, Fs)
    plt.subplot(3, 1, 3)
    plot(s_filtered2, Fs)
    plt.show()

    # Test to check if filtering online and offline works in the same way
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


