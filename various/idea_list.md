# General idea
- From spectral information of the audio, create something cool.
- This project approach creative area between generative art and math/physics.
- Also this code become very visual for party.
## Idea
- spectral as input for the system
- spectral as potential landscape for the system
- spectral as a noise

# TODO
## Section 0 (general stuff)
- [x] deciding the name of this project
- [x] fixing the general concept of this project
- [x] make the logo of this project
## Section 1 (spectral analysis of input audio)
- [ ] ~~PyAudio~~ (does not work Python>=3.7)
- [x] python-sounddevice (Faster alternative of PyAudio)
- [x] STFT
- [ ] Gabor
- [ ] Wigner-Ville
### Reference
1. http://arxiv.org/abs/2101.06707
2. https://www.generativehut.com/post/using-processing-for-music-visualization
3. https://www.henryschmale.org/2021/01/07/pygame-linein-audio-viz.html
3. https://youtu.be/aQKX3mrDFoY
## Section 2 (visualizing software)
- [x] Matplotlib
- [ ] pyqtgraph (fast!)
### Reference
1. https://youtu.be/RHmTgapLu4s
## Section 3 (various visualization)
### Mathematical model
- [ ] phasescope
- [ ] draw line by vector representation of spectral
- [ ] fractal
- [ ] Mandelbrot set
- [ ] Lissajous curve
- [ ] Bezier curve
- [ ] kaleidoscope
- [ ] Harmonograph
- [ ] Rose
- [ ] Voronoi
#### Reference
1. https://youtu.be/spUNpyF58BY
2. https://stackoverflow.com/questions/66309353/kaleidoscope-effect-using-python-and-opencv
### Classical mechanics
- [ ] double pendulum
- [ ] planetary system
- [ ] Hamiltonian map
- [ ] wave interference
#### Reference
1. http://irobutsu.a.la9.jp/movingtext/index.html
2. https://galileo-unbound.blog/
### Electromagnetics
- [ ] electric/magnetic field by spectral
- [ ] electric/magnetic field by moving electron
#### Reference
1. http://irobutsu.a.la9.jp/movingtext/index.html
### Thermodynamics
- [ ] molecular dynamics
#### Reference
1. http://irobutsu.a.la9.jp/movingtext/index.html
### Statistical mechanics
- [ ] Ising model
- [ ] lattice gas
- [ ] Fermi-Pasta-Ulam
### Quantum mechanics
- [ ] Schrödinger equation
- [ ] Wigner function
- [ ] Quantum carpet
- [ ] Quantum scar
### Fluid mechanics
- [ ] stable fluid
#### Reference
1. https://gfm.aps.org/
### Complex systems
- [ ] strange attractor
- [ ] cellular automata
    - [ ] Wolfram
        - [ ] Rule 90
        - [ ] Rule 140
    - [ ] Game of Life
        - [ ] Brian's brain
        - [ ] Seeds
    - [ ] Turing pattern
    - [ ] Self-organized criticality
    - [ ] Langton's ant
    - [ ] Belousov-Zhabotinsky reaction
    - [ ] Lenia
    - [ ] CoDi
- [ ] Vicsek model
- [ ] Kuramoto model
- [ ] active matter
    - [ ] cell moving vector field by active matter
- [ ] Network signalling
- [ ] Voter model
## Section 4 (parameter tuning)
