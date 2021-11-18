import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024 * 4

pa = pyaudio.PyAudio()

stream = pa.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = CHUNK
)


data = stream.read(CHUNK)
data = np.frombuffer(data, np.float32)

x = np.fft.fftfreq(CHUNK, d = 1.0 / RATE)
y = np.abs(np.fft.fft(data))/ (RATE / CHUNK)
y[y < 2.5] = 0


plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(x, y)
ax.set_xlim(0,2000)
ax.set_ylim(0,20)

while True:
    data = stream.read(CHUNK)
    data = np.frombuffer(data, np.float32)

    y = np.abs(np.fft.fft(data))/ (RATE / CHUNK)
    y[y < 2.5] = 0

    line.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()

    max_ind = argrelextrema(y, np.greater)
    r = y[max_ind]
    if (len(r) > 0):
        print(np.abs(x[np.where(y == r[0])[0][0]]))