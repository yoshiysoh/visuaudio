import numpy as np
from scipy.fft import rfft, fftfreq
from scipy.stats import norm
from numba import njit

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text + 'Value error, input could not be parsed as int'

def fourier(plotdata, length):

    rf = rfft(plotdata, axis=0)
    rf = np.abs(rf[:length//2])**2
    return rf

def gaussianFilter(length, Nsigma):  # before filter4gabor
    x_filter = np.arange(length)
    gaussian_filter = norm.pdf(x_filter,
                               loc=x_filter.mean(),
                               scale=length/2/Nsigma)
    gaussian_filter = gaussian_filter / gaussian_filter.max()
    gaussian_filter = np.vstack(gaussian_filter)
    return gaussian_filter

def gabor(plotdata, gaussian_filter_precalculated):
    plotdata_gabor = plotdata*gaussian_filter_precalculated
    rf = fourier(plotdata_gabor)
    return rf

# exact wigner transform
def preprocess4wigner(plotdata):
   flat_plotdata = plotdata.copy()
   flat_plotdata = flat_plotdata.flatten()
   forward_shifted_plotdata  = np.zeros((length, length))
   backward_shifted_plotdata = np.zeros((length, length))
   for i in range (length):
       forward_shifted_plotdata[:, i] = np.roll(flat_plotdata, i, axis=0)
       backward_shifted_plotdata[:, i] = np.roll(flat_plotdata, -i, axis=0)
   autocorrelation = forward_shifted_plotdata*backward_shifted_plotdata
   #autocorrelation = np.roll(autocorrelation, length//2, axis=1)
   return autocorrelation

def wigner(plotdata):
   autocorrelation = preprocess4wigner(plotdata)
   rf = rfft(autocorrelation, axis=1)
   rf = np.sum(rf, axis=0)
   rf = np.abs(rf[:length//2])
   rf = np.vstack(rf)
   return rf

# approx wigner transform
def wigner(plotdata, length):
    plotdata_wigner= np.roll(plotdata, length//2, axis=0)*np.roll(plotdata, -length//2, axis=0)
    rf = fourier(plotdata_wigner)
    return rf 

@njit
def original_radius(rf, r0f):
    return rf+r0f

@njit
def dynamic_radius(rf, r0f):
    return rf+r0f+rf[40:60].mean()

@njit
def postprocess(rf,r0f, sensitivity, radius_processor):
    rf *= sensitivity
    #rf = rf**(power)
    rf = np.log10(1+rf)
    rf = radius_processor(rf, r0f)
    return rf

@njit
def polar2cartesian(r, theta):
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return x, y
