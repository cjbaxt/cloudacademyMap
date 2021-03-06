#! /usr/bin/env python

# G.K.H. Lee : Basic plotting routine to map a variable at a chosen pressure level
# requires the basemap plotting package
# install with anaconda using: conda install -c conda-forge basemap

# 2018.09.26 - Modified by L. R. Corrales (liac@umich.edu)
# To map the cloud depth (distance from top, where dust tau=1)
# 2018.11.09 - Modified to use maplib

# Requires:
# ---------
# numpy, matplotlib, basemap
# Custom library of python functions: 'maplib'

## --------
## TO USE:
##
## In an interactive python session, one can import the main functions:
##
## >>> from map_cloud_depth import map_cloud_depth
## >>> map_cloud_depth[0]
##
## Or you can run the file as a script, and it will save all of the maps to a pdf
## 
## $ ./map_cloud_depth.py
## 
## Be sure to modify the `OUTPUT_DIR` variable to point to your desired output folder
## -------


import numpy as np
import matplotlib.pylab as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LogNorm

from maplib import get_wavel, cloud_depth, stringy

file_root = 'static_weather_results/HATP_7b' # root name for profile folders
nlay  = 53 # number of vertical layers
Teff = 2700.0 # eff/eq temperature

OUTPUT_DIR = 'Cloud_Opt_Depth/'

MAX_DEPTH = 10000 # km

## ---- Load the data

lons  = np.arange(-180., 180.01, 15) # deg
lats  = np.arange(0., 67.51, 22.5) # deg
nprof = len(lons) * len(lats) # number of (lon, lat) profiles

#lons  = np.arange(-180., 180.01, 45) # deg
#lats  = np.arange(0., 67.51, 22.5) # deg
#nprof = len(lons) * len(lats) # number of (lon, lat) profiles

# Get the wavelengths of interest. Assume all files are the same
wavel_file = file_root + '_Phi{}Theta{}/out3_extinction.dat'.format(stringy(lons[0]), stringy(lats[0]))
wavel = get_wavel(wavel_file) # um

# Read in the cloud depth values for each file.
# Make a 3D array with dimensions (lon, lat, wavel)
NLO, NLA, NWA = len(lons), len(lats), len(wavel)
Z = np.zeros((NLO, NLA, NWA))
for i in range(NLO):
    for j in range(NLA):
        w, d = cloud_depth(stringy(lons[i]), stringy(lats[j]))
        Z[i,j,:] = d

# The 180 longitude is same as -180
#Z[0,:,:] = Z[-1,:,:]

## ---- Mapping and plotting part

# Mesh grid to use for the map
X, Y = np.meshgrid(lons,lats)

# Default contour levels to use
nlev = 21
lev  = np.linspace(0, MAX_DEPTH, nlev)

def map_cloud_depth(i, levels=lev, cmap=plt.cm.RdYlBu_r, log=False):
    """
    Makes a plot of HAT-P-7b cloud depth at some wavelength
    
    Parameters
    ---------
    i : int
        Index to use from wavelength array

    levels : numpy.ndarray
        Contour levels to use for the map

    cmap : matplotlib.pyplot.colormap object
        Color map to use

    log : bool --> Not implemented as of now!!
        If True, uses logarithmically spaced colorbar

    Returns
    -------
    Results of Basemap.contourf for the northern hemisphere of the planet

    Also produces a plot.
    """
    m        = Basemap(projection='kav7', lon_0=0, resolution=None)
    CS_north = m.contourf(X, Y, Z[:,:,i].T,
                          levels=levels, extend='both', cmap=cmap, latlon=True)
    CS_south = m.contourf(X, -Y, Z[:,:,i].T,
                          levels=levels, extend='both', cmap=cmap, latlon=True)
    plt.colorbar(label='Cloud Depth (km)')
    plt.title('{:.1f} $\mu$m'.format(wavel[i]))
    
    ## -- Plot lat-lon lines on map
    # String formatting function
    def fmtfunc(inlon):
        string = r'{:g}'.format(inlon)+r'$^{\circ}$'
        #print string
        return string

    meridians = np.arange(0., 360., 90)
    m.drawmeridians(meridians, labels=[False,False,False,True],
                    labelstyle=None, fmt=fmtfunc, dashes=[3,3], color='k', fontsize=14)
    parallels = np.arange(-90., 90, 30)
    m.drawparallels(parallels, labels=[True,False,False,False],
                    labelstyle='+/-', dashes=[3,3], color='k',fontsize=14)

    # and we're done!
    return CS_north

## ------ 
## Plot everything and save it, if running this file as a script

def save_plot(i, root_string=OUTPUT_DIR+'cloud_depth_', verbose=True):
    filename = root_string + '{:.1f}um.pdf'.format(wavel[i])
    if verbose:
        print("Saving map to file: {}".format(filename))
    
    map_cloud_depth(i)
    plt.savefig(filename)
    plt.clf()
    return

if __name__ == '__main__':
    for i in range(len(wavel)):
        save_plot(i)
