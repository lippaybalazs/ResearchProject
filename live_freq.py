import numpy as np
import pyaudio
import matplotlib.pyplot as plt

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


plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(x, y)
ax.set_xlim(0,2000)
ax.set_ylim(0,20)

last5 = [0, 0, 0, 0, 0]
def most_frequent(List):
    counter = 0
    num = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
 
    return num

while True:
    data = stream.read(CHUNK)
    data = np.frombuffer(data, np.float32)

    y = np.abs(np.fft.fft(data))/ (RATE / CHUNK)
    
    last5 = last5[1:]
    last5.append(np.abs(x[np.argmax(y)]))
    print("guess: " + str(most_frequent(last5)))
    
    line.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()