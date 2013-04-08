'''
Created on Jun 15, 2012

@author: Steven
'''
from hmf_calc.FindMF import mf
#import string
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
#from django.conf import settings
import logging
import cosmolopy.distance as cd
#import atpy
import pandas
from matplotlib.lines import Line2D

def hmf_output(data):
    """
    Uses find_mf to drive the calculations
    """
    log = logging.getLogger(__name__)
    
    ##########################################################
    # DATA MANIPULATION
    #########################################################
    
    #============= Break the cosmological quantities into separate elements =====#
    cosmo_quantities = [key for key,val in data.iteritems() if key.startswith('cp_')]
    #cosmo_quantities = ['sigma_8','n','crit_dens','hubble','omega_lambda','omega_baryon','omega_cdm','mean_dens','w','omega_neutrino']
    cosmo_labels = data['cp_label']
    n_cosmologies = len(cosmo_labels)
    
    cosmology_list = []
    for i in range(n_cosmologies):
        cosmology_list = cosmology_list + [{}]
        for quantity in cosmo_quantities:
            index = min(len(data[quantity])-1,i)
            cosmology_list[i][quantity[3:]] = data[quantity][index] 
            
            
        #Mean density has extra processing
        cosmology_list[i]['mean_dens'] = data['cp_mean_dens'][index]*(cosmology_list[i]['omega_baryon']+cosmology_list[i]['omega_cdm'])*10**11
    
    #=========== Set the Transfer Function File correctly ===== #
    transfer_file = data["transfer_file"]
    if transfer_file == 'custom':
        if data["transfer_file_upload"] == None:
            transfer_file = None
        else:
            transfer_file = data['transfer_file_upload']
            log.info("Uploaded transfer file at: "+transfer_file)
        
    #=========== Set a cosmological dictionary specifically for CAMB ===========#
    camb_dict = []   
    for i in range(n_cosmologies):
        camb_dict = camb_dict + [{"w"              : cosmology_list[i]["w"],
                                 "omega_baryon"   : cosmology_list[i]["omega_baryon"],
                                 "omega_cdm"      : cosmology_list[i]["omega_cdm"],
                                 "omega_lambda"   : cosmology_list[i]["omega_lambda"],
                                 "omega_neutrino" : cosmology_list[i]["omega_neutrino"],
                                 "hubble"         : 100.0*cosmology_list[i]["hubble"]} ]
    #=========== Set k-bounds as a list of tuples ==============================#
    min_k = data['k_begins_at']
    max_k = data['k_ends_at']
    num_k_bounds = max(len(min_k),len(max_k))
    k_bounds = []
    for i in range(num_k_bounds):
        mink = min_k[min(len(min_k)-1,i)]
        maxk = max_k[min(len(max_k)-1,i)] 
        k_bounds.append((mink,maxk))
           
    #============ Set other simpla data ========================================#
    z = data["z"]
    wdm = data["WDM"]
    approach = []
    overdensity = data['overdensity']
    
    if data['approach']:
        for i in data["approach"]:
            approach = approach+[str(i)]
       
    if data["alternate_model"]:
        approach = approach + ['user_model']
    
    
    #Function Evaluation Options
    extra_plots = {}
    for key,val in data.iteritems():
        if key.startswith('get_'):
            extra_plots[key] = val
    #get_ngtm = data["get_ngtm"]
    #get_mgtm = data["get_mgtm"]
    #get_nltm = data["get_nltm"]
    #get_mltm = data["get_mltm"]
    #get_L = data['get_L']
    
    ######################################################
    # THE CALCULATION
    ######################################################
    mass_data, k_data = mf(transfer_file,data["extrapolate"],k_bounds,z,wdm,approach,
                           overdensity,cosmology_list,
                           data["min_M"],data["max_M"],
                           data["M_step"],str(data["alternate_model"]),
                           camb_dict, cosmo_labels,extra_plots)
    
            
    ######################################################
    # COSMOGRAPHY
    ######################################################
    distances = []
    for i,cosmology in enumerate(cosmology_list):
        #Set a cosmology for cosmolopy
        cosmo = {'omega_M_0':cosmology['omega_baryon']+cosmology['omega_cdm'],
                 'omega_lambda_0':cosmology['omega_lambda'],
                 'h':cosmology['hubble'],
                 'omega_b_0':cosmology['omega_baryon'],
                 'omega_n_0':cosmology['omega_neutrino'],
                 'N_nu':0,
                 'n':cosmology['n'],
                 'sigma_8':cosmology['sigma_8']}
    
        cd.set_omega_k_0(cosmo)
        
        #Age of the Universe
        for z_a in z:
            distances = distances + [[cosmo_labels[i],
                                      z_a,
                                      cd.age(z_a, use_flat=False,**cosmo)/(3600*24*365.25*10**9),
                                      cd.comoving_distance(z_a,**cosmo)/1000,
                                      cd.comoving_volume(z_a,**cosmo)/10**9,
                                      cd.angular_diameter_distance(z_a,**cosmo)/1000,
                                      cd.luminosity_distance(z_a,**cosmo)/1000]]
        

           
    return mass_data,k_data,distances

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
