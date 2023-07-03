#!/usr/bin/env python3
"""
Plot the live microphone signal(s) with PyQtGraph.

I modified the code from example code of python-sounddevice
https://github.com/spatialaudio/python-sounddevice/blob/f148dc64c9eb043adcf8de3b34890e8f3df71636/examples/plot_input.py
"""
import argparse
import queue
import sys

import numpy as np
from scipy.fft import rfft, fftfreq
from scipy.stats import norm
from numba import njit
import sounddevice as sd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'channels', type=int, default=[1], nargs='*', metavar='CHANNEL',
    help='input channels to plot (default: the first)')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-w', '--window', type=float, default=200, metavar='DURATION',
    help='visible time slot (default: %(default)s ms)')
parser.add_argument(
    '-i', '--interval', type=float, default=30,
    help='minimum time between plot updates (default: %(default)s ms)')
parser.add_argument(
    '-b', '--blocksize', type=int, help='block size (in samples)')
parser.add_argument(
    '-r', '--samplerate', type=float, help='sampling rate of audio device')
parser.add_argument(
    '-n', '--downsample', type=int, default=8, metavar='N',
    help='display every Nth sample (default: %(default)s)')
parser.add_argument(
    '-bg', '--background_theme', type=str, default='light',
    help='background theme (default: %(default)s)')
parser.add_argument(
    '-lc', '--line_color', type=str, default='matplotlib_cmap',
    help='line color theme (default: %(default)s)')
parser.add_argument(
    '-t', '--transformer', type=str, default='fourier',
    help='spectrum transformer (default: %(default)s)')
parser.add_argument(
    '-s', '--sensitivity', type=float, default=0.1,
    help='sensitivity of Specirctrogram (default: %(default)s)')
parser.add_argument(
    '-dr', '--dynamic_radius', type=int, default=0,
    help='dynamic radius (default: %(default)s)')
args = parser.parse_args(remaining)
if any(c < 1 for c in args.channels):
    parser.error('argument CHANNEL: must be >= 1')
mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
q = queue.Queue()


def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Fancy indexing with mapping creates a (necessary!) copy:
    q.put(indata[::args.downsample, mapping])


def fourier(plotdata):
    rf = rfft(plotdata, axis=0)
    rf = np.abs(rf[:length//2])**2
    return rf

def filter4gabor(plotdata):
    length = len(plotdata)
    x_filter = np.arange(length)
    gaussian_filter = norm.pdf(x_filter,
                               loc=x_filter.mean(),
                               scale=length/2/Nsigma)
    gaussian_filter = gaussian_filter / gaussian_filter.max()
    gaussian_filter = np.vstack(gaussian_filter)
    return gaussian_filter

def gabor(plotdata):
    plotdata_gabor = plotdata*gaussian_filter
    rf = fourier(plotdata_gabor)
    return rf

## for exact wigner transform
#def preprocess4wigner(plotdata):
#    flat_plotdata = plotdata.copy()
#    flat_plotdata = flat_plotdata.flatten()
#    forward_shifted_plotdata  = np.zeros((length, length))
#    backward_shifted_plotdata = np.zeros((length, length))
#    for i in range (length):
#        forward_shifted_plotdata[:, i] = np.roll(flat_plotdata, i, axis=0)
#        backward_shifted_plotdata[:, i] = np.roll(flat_plotdata, -i, axis=0)
#    autocorrelation = forward_shifted_plotdata*backward_shifted_plotdata
#    #autocorrelation = np.roll(autocorrelation, length//2, axis=1)
#    return autocorrelation
#
## for exact wigner transform
#def wigner(plotdata):
#    autocorrelation = preprocess4wigner(plotdata)
#    rf = rfft(autocorrelation, axis=1)
#    rf = np.sum(rf, axis=0)
#    rf = np.abs(rf[:length//2])
#    rf = np.vstack(rf)
#    return rf

def wigner(plotdata):
    plotdata_wigner= np.roll(plotdata, length//2, axis=0)*np.roll(plotdata, -length//2, axis=0)
    rf = fourier(plotdata_wigner)
    return rf 

@njit
def original_radius(rf):
    return rf+r0f

@njit
def dynamic_radius(rf):
    return rf+r0f+rf[40:60].mean()

@njit
def postprocess(rf):
    #rf *= sensitivity
    #rf = rf**(power)
    rf = np.log10(1+rf)
    return rf

@njit
def polar2cartesian(r, theta):
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return x, y


def update_plot():
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata, spectrogramdata, curve, curvef, p, frames
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

    spectrum = transformer(plotdata)
    spectrum = postprocess(spectrum)
    spectrogramdata = np.roll(spectrogramdata, -1, axis=1)
    spectrogramdata[:, [-1]] = spectrum
    spectrogram.setImage(
        spectrogramdata.T,
        autoLevels=False
    )

    frames += 1





try:
    ########
    # python-sounddevice
    ########
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    wigner_match = False
    # to match the results of fourier and wigner, 
    # we need the two-times large window.
    #if args.transformer == "wigner":
    #    args.downsample = args.downsample//2
    #    wigner_match = True
    length = int(args.window * args.samplerate / (1000 * args.downsample))
    plotdata = np.zeros((length, len(args.channels)))
    Nplotframes = 30*16
    spectrogramdata= np.zeros((length//2, Nplotframes))


    ########
    # pyqtgraph
    ########
    color = None
    colorf = None
    if args.background_theme=="light":
        pg.setConfigOption('background', 'w')
        cmap = pg.colormap.getFromMatplotlib("Blues")
        #cmap = pg.colormap.get("CET-L2")
    elif args.background_theme=="dark":
        pg.setConfigOption('background', 'k')
        cmap = pg.colormap.getFromMatplotlib("viridis")
        #cmap = pg.colormap.get("CET-L1")
    else :
        raise ValueError("background_theme must be one of 'light' or 'dark'")

    # Enable antialiasing for prettier plots
    # Disable it for faster plot with line width>1.0
    #pg.setConfigOptions(antialias=True)
    # Enable numba acceleration
    pg.setConfigOptions(useNumba=True)


    ########
    # parameters
    ########
    r0 = 0.75
    r0f = r0*1.25
    sensitivity = args.sensitivity
    power = 1.0
    Nsigma = 1


    ########
    # plotting
    ########
    app = pg.mkQApp()
    win = pg.GraphicsLayoutWidget(show=True)
    win.resize(640, 640)
    win.setWindowTitle("Audircle & Specirctrogram")
    p = win.addPlot()
    vb = p.getViewBox()


    ########
    # Spectrogram 
    ########
    if args.transformer == "fourier":
        transformer = fourier
    elif args.transformer == "gabor":
        gaussian_filter =filter4gabor(plotdata)
        transformer = gabor
    elif args.transformer == "wigner":
        transformer = wigner
    spectrum = transformer(plotdata)
    spectrum = postprocess(spectrum)
    spectrogramdata[:, [-1]] = spectrum
    spectrogram = pg.ImageItem(
        spectrogramdata.T,
        levels=(0.0, 4.0),
        colorMap=cmap,
    )
    p.addItem(spectrogram)

    ########
    # graphics setting
    ########
    #p.setXRange(-r_max, r_max)
    #p.setYRange(-r_max, r_max)
    p.enableAutoRange('xy', False)
    #p.setAspectLocked()
    p.showAxis('bottom', False)
    p.showAxis('left', False)
    p.hideButtons()
    #p.setLimits(xMin=-2*r_max, xMax=2*r_max,
    #            minXRange=r_max, maxXRange=4*r_max,
    #            yMin=-2*r_max, yMax=2*r_max,
    #            minYRange=r_max, maxYRange=4*r_max)
    p.setMouseEnabled(x=False, y=False)

    frames = 0
    stream = sd.InputStream(
        device=args.device, channels=max(args.channels),
        samplerate=args.samplerate, callback=audio_callback)
    with stream:
        timer = QtCore.QTimer()
        timer.timeout.connect(update_plot)
        timer.start(50)
        if __name__ == '__main__':
            pg.exec()
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
