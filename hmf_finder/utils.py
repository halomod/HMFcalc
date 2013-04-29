'''
Created on Jun 15, 2012

@author: Steven
'''
from hmf.Perturbations import Perturbations
#import string
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
#from django.conf import settings
import logging
import cosmolopy.distance as cd
import pandas
import os

def hmf_driver(transfer_file,  #File produced by CAMB containing the transfer function.
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
               cosmo_labels,   #Labels for each of the cosmologies
               extra_plots):   #A dictionary of bools for optional extra plots.
    
    # Change directory to this file (for picking up transfer files if pre-made)
    os.chdir(os.path.dirname(__file__))
    
    #Set-up array of masses    
    masses = np.arange(min_M,max_M,M_step)
            
    #Create a dataframe to hold the mass-based data
    mass_data = pandas.DataFrame({"M":10**masses})
    
    #Create a table to hold the k-based data
    k_data = pandas.DataFrame(index=range(4097))
    
    labels = {}
    warnings = {}
    
    pert = Perturbations(M = masses,
                         transfer_file = transfer_file,
                         z = z_list[0],
                         WDM = None,
                         k_bounds = k_bounds[0],
                         extrapolate = extrapolate,
                         reion__use_optical_depth = True,
                         **cosmology_list[0])
     
    #Loop through all the different cosmologies
    for cosmo_i,cosmo_dict in enumerate(cosmology_list):
        #Save the cosmo_label to the column label
        labels['cosmo'] = cosmo_labels[cosmo_i]
        #Loop through all WDM models (CDM first)
        for k_bound in k_bounds:
            #Save the k_bounds to the label
            if len(k_bounds)>1:
                labels['k'] = 'k{'+str(k_bound[0])+','+str(k_bound[1])+'}'
            for wdm in [None]+WDM_list:
                #Add WDM label
                if len(WDM_list)>0:
                    if wdm is None:
                        labels['wdm'] = 'CDM'
                    else:
                        labels['wdm'] = 'WDM='+str(wdm)
                #Loop over all redshifts
                for z in z_list:
                    #Define a column-name extension for the table
                    if len(z_list)>1:
                        labels['z'] = 'z='+str(z)
                    
                    print cosmo_dict
                    #Update pert object optimally with new variables    
                    pert.update(k_bounds = k_bound,WDM=wdm,z=z,**cosmo_dict)
                        
                    
                    #Save k-based data
                    k_data["k_"+getname(labels,excl=['deltavir','fsig'])]= pert.k
                    k_data["P(k)_"+getname(labels,excl=['deltavir','fsig'])]= pert.power_spectrum
                    
                    #Save Mass-Based data
                    mass_data["sigma_"+getname(labels,excl=['deltavir','fsig'])] = pert.sigma  
                    mass_data["lnsigma_"+getname(labels,excl=['deltavir','fsig'])] = pert.lnsigma
                    mass_data["neff_"+getname(labels,excl=['deltavir','fsig'])] = pert.n_eff 
                    
                    #Loop over fitting functions
                    for approach in approaches:
                        labels['fsig'] = approach
                        for overdensity in overdensities:
                            if len(overdensities)>1:
                                labels['deltavir'] = 'Dvir='+str(overdensity)
                             
                            #Save the data
                            mass_func = pert.MassFunction(fsigma=approach,overdensity=overdensity,delta_c=cosmo_dict['delta_c'])
                            
                            mass_data["hmf_"+getname(labels)] = mass_func
                            mass_data["f(sig)_"+getname(labels)] = pert.vfv
                            mass_data["M*hmf_"+getname(labels)] = mass_func*pert.M
                            
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
            
            if pert.max_error:
                warnings[getname(labels,excl=['deltavir','fsig','z','wdm'])] = [pert.max_error]
            if pert.min_error:    
                warnings[getname(labels,excl=['deltavir','fsig','z','wdm'])].append(pert.min_error)
            
          
    return mass_data, k_data,warnings

 
def cosmography(cosmology_list,cosmo_labels,redshifts):   
            
    ######################################################
    # COSMOGRAPHY
    ######################################################
    distances = []
    for i,cosmology in enumerate(cosmology_list):
        #Set a cosmology for cosmolopy
        cosmo = {'omega_M_0':cosmology['omegab']+cosmology['omegac'],
                 'omega_lambda_0':cosmology['omegav'],
                 'h':cosmology['H0']/100.0,
                 'omega_b_0':cosmology['omegab'],
                 'omega_n_0':cosmology['omegan'],
                 'N_nu':0,
                 'n':cosmology['n'],
                 'sigma_8':cosmology['sigma_8']}
    
        cd.set_omega_k_0(cosmo)
        
        #Age of the Universe
        for z in redshifts:
            distances = distances + [[cosmo_labels[i],
                                      z,
                                      cd.age(z, use_flat=False,**cosmo)/(3600*24*365.25*10**9),
                                      cd.comoving_distance(z,**cosmo)/1000,
                                      cd.comoving_volume(z,**cosmo)/10**9,
                                      cd.angular_diameter_distance(z,**cosmo)/1000,
                                      cd.luminosity_distance(z,**cosmo)/1000]]
        

           
    return distances

def create_canvas(masses,mass_data,title,xlab,ylab,yscale):
    ######################################################
    # IMAGE (CANVAS) PLOTTING
    ######################################################
    fig = Figure(figsize=(12,6.7),edgecolor='white', facecolor='white')
    ax = fig.add_subplot(111)

    ax.set_title(title)
    ax.grid(True)  
    ax.set_xlabel(xlab)  
    ax.set_ylabel(ylab) 
    
    linecolours = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    lines = ["-","--","-.",":"]                                                                                                                                                                                                 
    
    counter = 0
    for column in mass_data.columns:
        ax.plot(masses,mass_data[column],
                color=linecolours[(counter/4)%7],
                linestyle=lines[counter%4],
                label=column.split("_",1)[1].replace("_",", "))
        counter = counter+1
#    num_done = 0
#    for dat,cosmos in enumerate(cosmo_labels):
#        for cosmo_i in range(mass_func[dat].shape[0]): #Cosmology                                                                                                                                                                                                           
#            for i in range(mass_func[dat].shape[1]):   #Approach                                                                                                                                                                                                     
#                for j in range(mass_func[dat].shape[2]): #Redshift                                                                                                                                                                                             
#                    for k in range(mass_func[dat].shape[3]):#WDM mass/CDM  
#                        #USE THE FOLLOWING TO SORT IT
#                        quantities, varieties = (list(t) for t in zip(*sorted(zip([cosmo_i,i,j,k], mass_func[0].shape))))
#                
#                        if k == 0:
#                            ax.plot(masses,mass_func[dat][cosmo_i,i,j,k,:], 
#                                    color=linecolours[num_done+quantities[3]],
#                                    linestyle=linetypes[num_done + quantities[2]],
#                                    lw=0.5*(num_done+varieties[0]*quantities[1]+quantities[0]+1),
#                                    label = "CDM, "+approach[dat][i]+", z = "+str(pmfz[dat][j])+", "+cosmos[cosmo_i])
#                        else:
#                            ax.plot(masses,mass_func[dat][cosmo_i,i,j,k,:], color=linecolours[num_done+quantities[3]],
#                                    linestyle=linetypes[quantities[2]],
#                                    lw=0.5*(varieties[0]*quantities[1]+quantities[0]+1),
#                                    label = "WDM "+str(pmfwdm[dat][k-1])+"keV,"+approach[dat][i]+" z = "+str(pmfz[dat][j])+", "+cosmos[cosmo_i])
#                
#        num_done = num_done + mass_func[dat][:,:,:,:,0].size
            
    # Shrink current axis by 30%
    ax.set_xscale('log')
    ax.set_yscale(yscale)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    canvas = FigureCanvas(fig)
    return canvas


def create_k_canvas(k_data,k_keys,p_keys,title,xlab,ylab):
    fig = Figure(figsize=(12,6.7),edgecolor='white', facecolor='white')
    ax = fig.add_subplot(111)

    ax.set_title(title)
    ax.grid(True)  
    ax.set_xlabel(xlab)  
    ax.set_ylabel(ylab)
    
    linecolours = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    lines = ["-","--","-.",":"]
    
    counter = 0
    for j,k_key in enumerate(k_keys):
        ax.plot(np.exp(k_data[k_key]),np.exp(k_data[p_keys[j]]),
                    color=linecolours[counter/4],
                    linestyle=lines[counter%4],
                    label=k_key.split("_",1)[1].replace("_",", "))
        counter = counter+1
        
#    for dat,cosmos in enumerate(cosmo_labels): #Data-set
#        for cosmo_i in range(function[dat].shape[0]):#cosmology
#            for i in range(function[dat].shape[1]): #WDM
#                if i==0:
#                    ax.plot(np.exp(k[dat]),np.exp(function[dat][cosmo_i,i,:]),color = linecolours[num_done+i],
#                            linestyle=linetypes[num_done+cosmo_i],
#                            label="CDM, "+cosmos[i])
#                else:
#                    ax.plot(k[dat],function[dat][cosmo_i,i,:],color = linecolours[num_done+i],
#                            linestyle=linetypes[num_done+cosmo_i],
#                            label="WDM, "+str(wdm[dat][i-1])+"keV, "+cosmos[i])
#        num_done = num_done + function[dat][:,:,0].size
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
