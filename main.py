import numpy as np
import librosa


x, sr = librosa.load('sounds/guitar_g.wav')

c = np.fft.fft(x)
c = c[0:len(c)//2]
c_abs = np.abs(c)
c_max = np.argmax(c_abs)
y = c_max / (len(c) / sr)
print(y)
