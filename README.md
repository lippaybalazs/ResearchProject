# I. Research process description
## Experiment Plan
1. Single-note waveform analysis and instrument accuracy level
2. Multi-note waveform analysis and instrument accuracy level 

## Input data
The experiment inputs shall be from various instruments through non-professional input devices (microphones).

## Output validation
The experiment outputs shall be validated against pitch-tables.

## Algorithmic model
We assume that T is a vector containing the waveform of a recorded sound interval of length CHUNK with an input rate of RATE.

We apply Fast Fourier Transformation (FFT) on T, thus we get a vector of complex numbers C.

We calculate the absolute value of the elements of C, and we get a vector of real numbers P.

The indexes of P are the separate sound waves, and their values are the loudness of that wave.

We apply a noise gate to P. eliminating background noise under a set strength.

We define M as a vector of the indexes of peaks in P.

For M we calculate H = | M / CHUNK * RATE |, which is a vector of the ringing frequencies in the sound chunk.



