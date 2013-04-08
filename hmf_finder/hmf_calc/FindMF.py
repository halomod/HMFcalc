'''
Created on May 4, 2012

@author: smurray

This module contains one function "mf()", which uses both 
MassFunctionClasses and SetupFunctions to find the mass
function for several parameters (z,WDM,approach).

Ie. This file is basically a script to use the other modules.
'''

#===================================================================
#    IMPORT LOCAL MODULES AND CONFIG FILES
#===================================================================
import Perturbations
import SetupFunctions as setup

#===================================================================
#    IMPORT EXTERNAL MODULES
#===================================================================    
import numpy as np
import os
#import atpy -- want to use this but its not working at the moment?
import pandas
#import logging

#===================================================================                      
#    THE ACTUAL FUNCTION 
#===================================================================     
def mf(transfer_file,  #File produced by CAMB containing the transfer function.
       extrapolate,    #Bool - whether to extrapolate power spectrum
       k_bounds,       #Bounds to extrpolate powe spec to.
       z_list,         #Redshifts
       WDM_list,       #WDM masses
       approaches,     #Fitting Functions
       overdensities,  #Virial overdensity parameters
       cosmology_list, #List of cosmology dictionaries
       min_M, max_M,   #Minimum and Maximum mass to calculate for
       M_step,         #Step size in log10(M_sun)
       user_model,     #An optional mass function model from the user
       camb_dict_list, #The parameters for camb to use    
       cosmo_labels,   #Labels for each of the cosmologies
       extra_plots):   #A dictionary of bools for optional extra plots.
    
    #----------------- SETUP THE CALCULATIONS-----------------------     
    # Use the convenience function Setup() to import the transfer
    # function, set up a vector of radii, establish a step-size for
    # Romberg integration, and create output directories.
    # If use_camb is true, then CAMB operations will also be performed
    os.chdir(os.path.dirname(setup.__file__))
        
    masses = np.arange(min_M,max_M,M_step)
    masses = 10**masses
            
    #Create a dataframe to hold the mass-based data
    #mass_data = atpy.Table()
    #mass_data.add_column("M", masses, unit='log10(M_sun)/h')
    
    mass_data = pandas.DataFrame({"M":masses})
    #Create a table to hold the k-based data
    #k_data = atpy.Table()
    k_data = pandas.DataFrame(index=range(4097))
    
    print WDM_list
    print z_list
    print approaches
    print overdensities
    print k_bounds
    print camb_dict_list
    labels = {}
    #Loop through all the different cosmologies
    for cosmo_i,camb_dict in enumerate(camb_dict_list):
        #Each cosmology has a different transfer function
        k_vector, transfer = setup.Setup(transfer_file,camb_dict)

        #Save the cosmo_label to the column label
        labels['cosmo'] = cosmo_labels[cosmo_i]
        
        #Loop through all WDM models (CDM first)
        for k_bound in k_bounds:
            
            #Save the k_bounds to the label
            if len(k_bounds)>1:
                labels['k'] = 'k{'+str(k_bound[0])+','+str(k_bound[1])+'}'
            
            for wdm in [None]+WDM_list:
            
                #This gives us enough to initialize the Perturbation class (interpolate power spec)
                pert = Perturbations.Perturbations(masses,k_vector,transfer,0.0,cosmology_list[cosmo_i],
                                                   wdm,200,k_bound,"ST",user_model,extrapolate)
            
                #Add WDM label
                if len(WDM_list)>0:
                    if wdm is None:
                        labels['wdm'] = 'CDM'
                    else:
                        labels['wdm'] = 'WDM='+str(wdm)
                
                #Loop over all redshifts
                for z in z_list:
                    #Re-set the redshift in pert
                    if z>0:
                        pert.set_z(z)
                    
                    #Define a column-name extension for the table
                    if len(z_list)>1:
                        labels['z'] = 'z='+str(z)
                        
                    #k_data.add_column("k_"+name_ext, k_now, unit='h/Mpc',dtype='int')
                    #k_data.add_column("P(k)_"+name_ext, pert.power_spectrum, unit='h^3/Mpc^3') 
                    
                    k_data["k_"+getname(labels,excl=['deltavir','fsig'])]= pert.k
                    k_data["P(k)_"+getname(labels,excl=['deltavir','fsig'])]= pert.power_spectrum
                    
                    #mass_data.add_column("sigma_"+name_ext, pert.sigma, unit="M_sun/h" )
                    #mass_data.add_column("lnsigma_"+name_ext,pert.lnsigma)
                    #mass_data.add_column("neff_"+name_ext, pert.n_eff)
                     
                    mass_data["sigma_"+getname(labels,excl=['deltavir','fsig'])] = pert.sigma  
                    mass_data["lnsigma_"+getname(labels,excl=['deltavir','fsig'])] = pert.lnsigma
                    mass_data["neff_"+getname(labels,excl=['deltavir','fsig'])] = pert.n_eff 
                    
                    #Loop over fitting functions
                    for approach in approaches:
                        #Set the fitting function in the class 
                        pert.approach = approach
                        
                        labels['fsig'] = approach
                        
                        for overdensity in overdensities:
                            if len(overdensities)>1:
                                labels['deltavir'] = 'Dvir='+str(overdensity)
                             
                            pert.overdensity = overdensity
                            
                            #Save the data
                            mass_func = pert.MassFunction()
                            #mass_data.add_column("hmf_"+name_ext, mass_func, unit="log10(dn/dlogM) h^3/Mpc^3")
                            #mass_data.add_column("f(sig)_"+name_ext, pert.vfv)
                            #mass_data.add_column("M*hmf_", mass_func+np.log10(masses), unit="log10(M*dn/dlogM) M_sun h^2/Mpc^3")
                            
                            mass_data["hmf_"+getname(labels)] = mass_func
                            mass_data["f(sig)_"+getname(labels)] = pert.vfv
                            mass_data["M*hmf_"+getname(labels)] = mass_func+np.log10(masses)
                            
                            #Easily add more when you need to 
                            if extra_plots['get_ngtm']:
                                #mass_data.add_column("NgtM_"+name_ext, pert.NgtM(mass_func),unit="h^3/Mpc^3")
                                mass_data["NgtM_"+getname(labels)] = pert.NgtM(mass_func)
                            if extra_plots['get_mgtm']:
                                #mass_data.add_column("MgtM_"+name_ext, pert.MgtM(mass_func),unit="log10(M_sun) h^2/Mpc^3")
                                mass_data["MgtM_"+getname(labels)] = pert.MgtM(mass_func)
                            if extra_plots['get_nltm']:
                                #mass_data.add_column("NltM_"+name_ext, pert.NltM(mass_func),unit="h^3/Mpc^3")
                                mass_data["NltM_"+getname(labels)] = pert.NltM(mass_func)
                            if extra_plots['get_mltm']:
                                #mass_data.add_column("MltM_"+name_ext, pert.MltM(mass_func),unit="log10(M_sun) h^3/Mpc^3")
                                mass_data["MltM_"+getname(labels)] = pert.MltM(mass_func)
                            if extra_plots['get_L']:
                                mass_data["L(N=1)_"+getname(labels)] = pert.how_big(mass_func)
        
    return mass_data, k_data
        
                    
def getname(names,excl=[]):
    """
    Compiles the individual labels from a dictionary to a string label
    """
    label = ''
    for key,val in names.iteritems():
        if key not in excl:
            label = label+val+'_'
        
    label = label[:-1]
    
    return label

            
        
    
    
    
    
