import numpy as np
import pyaudio
from scipy import signal

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024 * 4

pa = pyaudio.PyAudio()

# set up audio device
stream = pa.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = CHUNK
)



# set up frequency array
x = np.fft.fftfreq(CHUNK, d = 1.0 / RATE)

while True:
    # read chunk of data
    data = stream.read(CHUNK)
    data = np.frombuffer(data, np.float32)

    # reduce data
    y = np.abs(np.fft.fft(data)) / (RATE / CHUNK)

    # get peaks of array
    max_ind,_ = signal.find_peaks(y, prominence=1)

    # separate peak values
    r = y[max_ind]
    r = np.unique(r)
    if (len(r) > 0):
        
        # gather frequency values
        freq = []
        for val in r:
            freq.append(np.abs(np.where(y == val)[0][0] / CHUNK * RATE))
        
        # due to the frequency range looping around, we might get duplicates
        freq = np.unique(freq)

        
        # false positives occur at extreme frequencies due to low data density
        # human hearing stops at around 8kHz, thus 10kHz is a good filter
        freq = freq[freq < 10000]

        # print frequencies
        print(freq)
