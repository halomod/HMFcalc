'''
Created on Jun 15, 2012

@author: Steven
'''
from hmf import Perturbations
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import logging
import cosmolopy.distance as cd
#import pandas
import os
import matplotlib.ticker as tick

#TODO: labels across adds are allllll wrong.
#TODO: cosmography doesn't do all redshifts if added at once on an add??

def hmf_driver(transfer_file,  #File produced by CAMB containing the transfer function.
              # extrapolate,  #Bool - whether to extrapolate power spectrum
               k_bounds,  #Bounds to extrpolate powe spec to.
               z_list,  #Redshifts
               WDM_list,  #WDM masses
               approaches,  #Fitting Functions
               overdensities,  #Virial overdensity parameters
               cosmology_list,  #List of cosmology dictionaries
               min_M, max_M,  #Minimum and Maximum mass to calculate for
               M_step,  #Step size in log10(M_sun)
               user_model,  #An optional mass function model from the user
               cosmo_labels,  #Labels for each of the cosmologies
               extra_plots,
               hmf_form,
               transfer_fit):  #A dictionary of bools for optional extra plots.

    # Change directory to this file (for picking up transfer files if pre-made)
    os.chdir(os.path.dirname(__file__))

    #Set-up array of masses
    masses = np.arange(min_M, max_M, M_step)

    #Create a dataframe to hold the mass-based data
    mass_data = {'M':10 ** masses}

#    if not extrapolate:
#        for i, bound in enumerate(k_bounds):
#            k_bounds[i] = None

    #Create a table to hold the k-based data
    k_data = {}

    labels = {}
    warnings = {}
    growths = []
    pert = Perturbations(M=masses,
                         transfer_file=transfer_file,
                         z=z_list[0],
                         wdm_mass=None,
                         k_bounds=k_bounds[0],
                         delta_vir=overdensities[0],
                         mf_fit=approaches[0],
                         user_fit=user_model,
                         reion__use_optical_depth=True,
                         transfer_fit=transfer_fit,
                         **cosmology_list[0])

    #Loop through all the different cosmologies
    for cosmo_i, cosmo_dict in enumerate(cosmology_list):
        growths.append([])
        #Save the cosmo_label to the column label
        if len(cosmology_list) > 1 or max(len(cosmology_list), len(k_bounds), len(z_list), len(approaches), len(overdensities)) == 1:
            labels['cosmo'] = cosmo_labels[cosmo_i]
        labels["cosmo_fallback"] = cosmo_labels[cosmo_i]

        #Loop through all WDM models (CDM first)
        for k_bound in k_bounds:
            #Save the k_bounds to the label
            if len(k_bounds) > 1:
                labels['k'] = 'k{' + str(k_bound[0]) + ',' + str(k_bound[1]) + '}'
            for wdm in [None] + WDM_list:
                #Add WDM label
                if len(WDM_list) > 0:
                    if wdm is None:
                        labels['wdm'] = 'CDM'
                    else:
                        labels['wdm'] = 'WDM=' + str(wdm)
                #Loop over all redshifts
                for z in z_list:
                    #Define a column-name extension for the table
                    if len(z_list) > 1 or z > 0:
                        labels['z'] = 'z=' + str(z)

                    #Update pert object optimally with new variables
                    pert.update(k_bounds=k_bound, wdm_mass=wdm, z=z, **cosmo_dict)

                    growths[cosmo_i].append(pert.growth)
                    #Save k-based data
                    excludes = ['deltavir', 'fsig', "cosmo_fallback"]
                    k_data["ln(k)_" + (getname(labels, excl=excludes)or getname(labels, excl=excludes[:-1]))] = pert.lnk
                    k_data["ln(P(k))_" + (getname(labels, excl=excludes)or getname(labels, excl=excludes[:-1]))] = pert.power

                    #Save Mass-Based data
                    mass_data["sigma_" + (getname(labels, excl=excludes) or getname(labels, excl=excludes[:-1]))] = pert.sigma
                    mass_data["lnsigma_" + (getname(labels, excl=excludes)or getname(labels, excl=excludes[:-1]))] = pert.lnsigma
                    mass_data["neff_" + (getname(labels, excl=excludes)or getname(labels, excl=excludes[:-1]))] = pert.n_eff

                    #Loop over fitting functions
                    for approach in approaches:
                        if len(approaches) > 1:
                            labels['fsig'] = approach
                        for overdensity in overdensities:
                            if len(overdensities) > 1:
                                labels['deltavir'] = 'Dvir=' + str(overdensity)

                            #Save the data
                            pert.update(mf_fit=approach, delta_vir=overdensity, delta_c=cosmo_dict['delta_c'])
                            mass_data["f(sig)_" + getname(labels, excl="cosmo_fallback")] = pert.fsigma

                            # ----- Mass Functions -----
                            if hmf_form == 'dndlnm':
                                mass_data["dndlnm_" + getname(labels, excl=['cosmo_fallback'])] = pert.dndlnm
                                mass_data["M*dndlnm_" + getname(labels, excl="cosmo_fallback")] = pert.dndlnm * pert.M
                            elif hmf_form == 'dndlog10m':
                                mass_data["dndlog10m_" + getname(labels, excl=['cosmo_fallback'])] = pert.dndlog10m
                                mass_data["M*dndlog10m_" + getname(labels, excl="cosmo_fallback")] = pert.dndlog10m * pert.M
                            elif hmf_form == 'dndm':
                                mass_data["dndm_" + getname(labels, excl=['cosmo_fallback'])] = pert.dndm
                                mass_data["M*dndm_" + getname(labels, excl="cosmo_fallback")] = pert.dndm * pert.M

                            #Extra Plots: Easily add more when you need to
                            if 'get_ngtm' in extra_plots:
                                mass_data["ngtm_" + getname(labels, excl="cosmo_fallback")] = pert.ngtm
                            if 'get_mgtm' in extra_plots:
                                mass_data["mgtm_" + getname(labels, excl="cosmo_fallback")] = pert.mgtm
                            if 'get_nltm' in extra_plots:
                                mass_data["nltm_" + getname(labels, excl="cosmo_fallback")] = pert.nltm
                            if 'get_mltm' in extra_plots:
                                mass_data["mltm_" + getname(labels, excl="cosmo_fallback")] = pert.mltm
                            if 'get_L' in extra_plots:
                                mass_data["L(N=1)_" + getname(labels, excl="cosmo_fallback")] = pert.how_big

            if pert.max_error:
                warnings[getname(labels, excl=['deltavir', 'fsig', 'z', 'wdm'])] = [pert.max_error]
            else:
                warnings[getname(labels, excl=['deltavir', 'fsig', 'z', 'wdm'])] = []
            if pert.min_error:
                warnings[getname(labels, excl=['deltavir', 'fsig', 'z', 'wdm'])].append(pert.min_error)


    return mass_data, k_data, growths, warnings


def cosmography(cosmology_list, cosmo_labels, redshifts, growth):

    ######################################################
    # COSMOGRAPHY
    ######################################################
    distances = []
    for i, cosmology in enumerate(cosmology_list):
        #Set a cosmology for cosmolopy
        cosmo = {'omega_M_0':cosmology['omegab'] + cosmology['omegac'],
                 'omega_lambda_0':cosmology['omegav'],
                 'h':cosmology['H0'] / 100.0,
                 'omega_b_0':cosmology['omegab'],
                 'omega_n_0':0,  #cosmology['omegan'],
                 'N_nu':0,
                 'n':cosmology['n'],
                 'sigma_8':cosmology['sigma_8']}

        cd.set_omega_k_0(cosmo)

        #Age of the Universe
        for j, z in enumerate(redshifts):
            distances = distances + [[cosmo_labels[i],
                                      z,
                                      cd.age(z, use_flat=False, **cosmo) / (3600 * 24 * 365.25 * 10 ** 9),
                                      cd.comoving_distance(z, **cosmo) / 1000,
                                      cd.comoving_volume(z, **cosmo) / 10 ** 9,
                                      cd.angular_diameter_distance(z, **cosmo) / 1000,
                                      cd.luminosity_distance(z, **cosmo) / 1000,
                                      growth[i][j]],
                                     ]



    return distances

def create_canvas(masses, mass_data, title, xlab, ylab, yscale, keep, base2=False):
    #TODO: make log scaling automatic
    fig = Figure(figsize=(11, 6), edgecolor='white', facecolor='white', dpi=100)
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.grid(True)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    linecolours = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    lines = ["-", "--", "-.", ":"]

    counter = 0
    for column in keep:
        ax.plot(masses, mass_data[column],
                color=linecolours[(counter / 4) % 7],
                linestyle=lines[counter % 4],
                label=column.split("_", 1)[1].replace("_", ", ")
                )
        print column.split("_", 1)[1].replace("_", ", ")
        counter = counter + 1



    # Shrink current axis by 30%
    ax.set_xscale('log')
    if not base2:
        ax.set_yscale(yscale)
    else:
        ax.set_yscale(yscale, basey=2)
        ax.yaxis.set_major_formatter(tick.ScalarFormatter())
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #fig.tight_layout()

    canvas = FigureCanvas(fig)
    return canvas


def create_k_canvas(k_data, k_keys, p_keys, title, xlab, ylab):
    fig = Figure(figsize=(12, 6.7), edgecolor='white', facecolor='white')
    ax = fig.add_subplot(111)

    ax.set_title(title)
    ax.grid(True)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    linecolours = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    lines = ["-", "--", "-.", ":"]

    counter = 0
    for j, k_key in enumerate(k_keys):
        ax.plot(np.exp(k_data[k_key]), np.exp(k_data[p_keys[j]]),
                    color=linecolours[counter / 4],
                    linestyle=lines[counter % 4],
                    label=k_key.split("_", 1)[1].replace("_", ", "))
        counter = counter + 1

    #Make the axes logarithmic
    ax.set_yscale('log')
    ax.set_xscale('log')
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    canvas = FigureCanvas(fig)
    return canvas

def getname(names, excl=[]):
    """
    Compiles the individual labels from a dictionary to a string label
    """
    label = ''
    for key, val in names.iteritems():
        if key not in excl:
            label = label + val + '_'

    label = label[:-1]

    return label
