#!/usr/bin/env python3
"""
Plot the live microphone signal(s) with PyQtGraph.

Original code is from example of code of python-sounddevice
https://github.com/spatialaudio/python-sounddevice/blob/f148dc64c9eb043adcf8de3b34890e8f3df71636/examples/plot_input.py
"""
import argparse
import queue
import sys

import numpy as np
from scipy.fft import rfft, fftfreq
from scipy.stats import norm
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
    '-n', '--downsample', type=int, default=10, metavar='N',
    help='display every Nth sample (default: %(default)s)')
parser.add_argument(
    '-c', '--theme', type=str, default='light',
    help='color theme (default: %(default)s)')
parser.add_argument(
    '-t', '--transformer', type=str, default='fourier',
    help='spectrum transformer (default: %(default)s)')
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
    yf = rfft(plotdata, axis=0)
    yf = np.abs(yf[:length//2])*0.05
    return yf

def filter4gabor(plotdata):
    length = len(plotdata)
    x_filter = np.arange(length)
    gaussian_filter = norm.pdf(x_filter,
                               loc=x_filter.mean(),
                               scale=length/2/Nsigma)
    gaussian_filter = np.vstack(gaussian_filter)
    return gaussian_filter

def gabor(plotdata):
    yf = rfft(plotdata*gaussian_filter, axis=0)
    yf = np.abs(yf[:length//2])*100
    return yf

def shifter4wigner(plotdata):
    shifter = len(plotdata)//2
    return shifter

def wigner(plotdata):
    yf = rfft(plotdata*np.roll(plotdata, -shifter, axis=0), axis=0)
    yf = np.abs(yf[:length//2])
    return yf

def original_radius(yf):
    return yf+r0f

def dynamic_radius(yf):
    return yf+r0f+yf[40:60].mean()


def update_plot():
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata, curve, curvef, p, frames
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

    r = plotdata+r0
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    curve.setData(np.hstack((x, y)))

    rf = transformer(plotdata)
    rf = rf**(power)
    rf = radius_processor(rf)
    xf = rf*np.cos(thetaf)
    yf = rf*np.sin(thetaf)
    curvef.setData(np.hstack((xf, yf)))

    frames += 1


r0 = 0.75
r0f = r0*1.25
power = 1.0
Nsigma = 1



try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    length = int(args.window * args.samplerate / (1000 * args.downsample))
    plotdata = np.zeros((length, len(args.channels)))

    app = pg.mkQApp()

    win = pg.GraphicsLayoutWidget(show=True)
    win.resize(640, 640)
    win.setWindowTitle("Audircle & Specirctrogram")

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)

    p = win.addPlot()


    theta = np.linspace(0, 2*np.pi, length)
    theta = np.vstack(theta)
    r = plotdata+r0
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    curve = p.plot(np.hstack((x, y)))

    thetaf = fftfreq(length, args.window)[:length//2]
    thetaf = thetaf/thetaf.max() * 2*np.pi
    thetaf = np.vstack(thetaf)
    if args.transformer == "fourier":
        transformer = fourier
    elif args.transformer == "gabor":
        gaussian_filter =filter4gabor(plotdata)
        transformer = gabor
    elif args.transformer == "wigner":
        shifter = shifter4wigner(plotdata)
        transformer = wigner
    rf = transformer(plotdata)
    rf = rf**(power)
    if args.dynamic_radius :
        radius_processor = dynamic_radius
    else :
        radius_processor = original_radius
    rf = radius_processor(rf)
    xf = rf*np.cos(thetaf)
    yf = rf*np.sin(thetaf)
    curvef = p.plot(np.hstack((xf, yf)))

    p.setAspectLocked()
    r_max = r0f + 0.7
    p.setXRange(-r_max, r_max)
    p.setYRange(-r_max, r_max)
    p.setLimits(xMin=-2*r_max, xMax=2*r_max, 
                minXRange=r_max, maxXRange=4*r_max, 
                yMin=-2*r_max, yMax=2*r_max,
                minYRange=r_max, maxYRange=4*r_max)
    p.enableAutoRange('xy', False)
    p.showAxis('bottom', False)
    p.showAxis('left', False)

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
