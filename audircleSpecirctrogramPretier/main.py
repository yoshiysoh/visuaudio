#!/usr/bin/env python3
"""
Plot the live microphone signal(s) with PyQtGraph.

I modified the code from example code of python-sounddevice
https://github.com/spatialaudio/python-sounddevice/blob/f148dc64c9eb043adcf8de3b34890e8f3df71636/examples/plot_input.py
"""
import argparse
import queue
import sys
import sounddevice as sd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from utils import *

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Fancy indexing with mapping creates a (necessary!) copy:
    q.put(indata[::args.downsample, mapping])


def update_plot():
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata, curve, curvef, p, frames, q
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

    r = plotdata+r0
    x, y = polar2cartesian(r, theta)
    curve.setData(np.hstack((x, y)))

    rf = transformer(plotdata, **transformer_kwargs)
    rf = postprocess(rf,r0f, sensitivity, radius_processor)
    xf, yf = polar2cartesian(rf, thetaf)
    curvef.setData(np.hstack((xf, yf)))

    frames += 1


def main():
    ########
    # setting global variables
    ########
    global plotdata, curve, curvef, p, frames, q, length, r0, theta, thetaf, r0f, sensitivity, radius_processor, transformer, transformer_kwargs, mapping, args

    ########
    # parse args
    ########

    def parse_args():
        # parse arguments
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        
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
            '-r', '--samplerate', type=float, help='sampling rate of audio device', )
        parser.add_argument(
            '-n', '--downsample', type=int, default=10, metavar='N',
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
            '-s', '--sensitivity', type=float, default=0.01,
            help='sensitivity of Specirctrogram (default: %(default)s)')
        parser.add_argument(
            '-dr', '--dynamic_radius', type=int, default=0,
            help='dynamic radius (default: %(default)s)')
        
        args = parser.parse_args()
        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        if any(c < 1 for c in args.channels):
            parser.error('argument CHANNEL: must be >= 1')
        
        return args

    args = parse_args()
    mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
    q = queue.Queue()


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


    ########
    # pyqtgraph
    ########
    color = None
    colorf = None
    if args.background_theme=="light":
        pg.setConfigOption('background', 'w')
        if args.line_color == "matplotlib_cmap":
            import matplotlib.pyplot as plt
            color  = np.array(plt.cm.tab10(0)) * 255
            colorf = np.array(plt.cm.tab10(1)) * 255
    elif args.background_theme=="dark":
        pg.setConfigOption('background', 'k')
        if args.line_color == "matplotlib_cmap":
            import matplotlib.pyplot as plt
            color  = np.array(plt.cm.Set3(0)) * 255
            colorf = np.array(plt.cm.Set3(1)) * 255
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
    r0 = 0.75  # inner radius
    r0f = r0*1.25  # outer radius
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

    ########
    # Audircle
    ########
    theta = np.linspace(0, 2*np.pi, length)
    theta = np.vstack(theta)
    r = plotdata+r0
    x, y = polar2cartesian(r, theta)
    curve = p.plot(np.hstack((x, y)), skipFiniteCheck=True)
    color = 'white' if color is None else color
    curve.setPen(color,
                    width=4,
                    capStyle="FlatCap",
                    joinStyle="MiterJoin")

    ########
    # Specirctrogram
    ########
    thetaf = fftfreq(length, args.window)[:length//2]
    thetaf = thetaf/thetaf.max() * 2*np.pi
    if args.transformer == "wigner" and wigner_match:
        thetaf = np.linspace(0, 2*np.pi, length//4 + (length+1)%2)
    thetaf = np.vstack(thetaf)

    # select transformer function
    func_dict = {
        "fourier" : {'func': fourier, 'kwargs': {'length' : length}},
        "gabor"   : {'func': gabor,   'kwargs': {'gaussian_filter_precalculated' : gaussianFilter(length, Nsigma)}},
        "wigner"  : {'func': wigner,  'kwargs': {'length' : length}},
    }
    (transformer, transformer_kwargs) = (func_dict[args.transformer][key] for key in ['func', 'kwargs'])
    rf = transformer(plotdata, **transformer_kwargs)
    


    if args.dynamic_radius :
        radius_processor = dynamic_radius
    else :
        radius_processor = original_radius
    rf = postprocess(rf, r0f, sensitivity, radius_processor)
    xf, yf = polar2cartesian(rf, thetaf)
    curvef = p.plot(np.hstack((xf, yf)), skipFiniteCheck=True)
    if colorf is None:
        curvef.setPen(width=4,
                    capStyle="FlatCap",
                    joinStyle="MiterJoin")
    else :
        curvef.setPen(colorf,
                    width=4,
                    capStyle="FlatCap",
                    joinStyle="MiterJoin")

    ########
    # graphics setting
    ########
    r_max = r0f + 0.5
    p.setXRange(-r_max, r_max)
    p.setYRange(-r_max, r_max)
    p.enableAutoRange('xy', False)
    p.setAspectLocked()
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
 
if __name__ == '__main__':
    main()