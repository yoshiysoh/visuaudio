#!/usr/bin/env python3
"""
Plot the live microphone signal(s) with Matplotlib.

Original code is from example of code of python-sounddevice
https://github.com/spatialaudio/python-sounddevice/blob/f148dc64c9eb043adcf8de3b34890e8f3df71636/examples/plot_input.py
"""
import argparse
import queue
import sys

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fft import rfft, fftfreq
from scipy.stats import norm
import sounddevice as sd


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
    '-bg', '--background_theme', type=str, default='light',
    help='background theme (default: %(default)s)')
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
    yf = np.abs(yf[:length//2])**2
    return yf

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
    yf = fourier(plotdata_gabor)
    return yf

def shifter4wigner(plotdata):
    shifter = len(plotdata)//2
    return shifter

def wigner(plotdata):
    plotdata_wigner = plotdata*np.roll(plotdata, -shifter, axis=0)
    yf = rfft(plotdata_wigner, axis=0)
    yf = np.abs(yf[:length//2]) * 10
    return yf

def original_radius(yf):
    return yf+r0f

def dynamic_radius(yf):
    return yf+r0f+yf[40:60].mean()

def postprocess(yf):
    yf *= sensitivity
    #yf = yf**(power)
    yf = np.log10(1+yf)
    rf = radius_processor(yf)
    return rf



def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

    #for column, line in enumerate(lines):
    #    line.set_ydata(plotdata[:, column]+r)
    r = plotdata[:, 0]+r0
    lines.set_ydata(r)

    yf = transformer(plotdata)
    rf = postprocess(yf)
    #for column, linef in enumerate(linesf):
    #    linef.set_ydata(yf[:, column])
    linesf.set_ydata(rf)
    return lines, linesf

mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['figure.constrained_layout.use'] = True
if args.background_theme=="light":
    plt.style.use('fast')
elif args.background_theme=="dark":
    plt.style.use('dark_background')
    plt.style.use('fast')

r0 = 0.75
r0f = r0*1.25
sensitivity = 0.01
power = 1.0
Nsigma = 1



try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    length = int(args.window * args.samplerate / (1000 * args.downsample))
    plotdata = np.zeros((length, len(args.channels)))

    fig, ax = plt.subplots(figsize = (6.4, 6.4),
                           subplot_kw={'projection': 'polar'})

    theta = np.linspace(0, 2*np.pi, length)
    r = plotdata + r0
    lines, = ax.plot(theta, r, animated=True)
    if len(args.channels) > 1:
        ax.legend([f'channel {c}' for c in args.channels],
                  loc='lower left', ncol=len(args.channels))

    xf = fftfreq(length, args.window)[:length//2]
    thetaf = xf/xf.max() * 2*np.pi
    if args.transformer == "fourier":
        transformer = fourier
    elif args.transformer == "gabor":
        gaussian_filter =filter4gabor(plotdata)
        transformer = gabor
    elif args.transformer == "wigner":
        shifter = shifter4wigner(plotdata)
        transformer = wigner
    yf = transformer(plotdata)
    if args.dynamic_radius :
        radius_processor = dynamic_radius
    else :
        radius_processor = original_radius
    rf = postprocess(yf)
    linesf, = ax.plot(thetaf, rf, animated=True)

    plt.get_current_fig_manager().set_window_title('Audircle & Specirctrogram')
    ax.axis('off')
    ax.axis((0, 2*np.pi, 0, r0f+0.7))

    stream = sd.InputStream(
        device=args.device, channels=max(args.channels),
        samplerate=args.samplerate, callback=audio_callback)
    ani = FuncAnimation(fig, update_plot, interval=args.interval, blit=True, cache_frame_data=False)
    with stream:
        plt.show(block=True)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
