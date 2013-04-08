'''
Created on Jun 15, 2012

@author: Steven
'''

from django.contrib import admin
from django.forms   import TextInput, Textarea
from django.db      import models
#from hmf_finder.models import plot_mf

#class plot_mf_admin(admin.ModelAdmin):
#    fieldsets = [
#                 (None   , {'fields':['name',('z','WDM'),'approach','alternate_model',('transfer_file','transfer_file_upload')]}),
#                 ('Run Parameters', {'fields':[('k_begins_at','k_ends_at','extrapolate'),('min_M','max_M','M_step')]}),
#                 ('Cosmological Parameters',{'fields':[('mean_dens','crit_dens','n'),('sigma_8','hubble','omega_lambda'),('omega_baryon','omega_cdm',"overdensity"),('omega_neutrino','w')],'classes':['collapse']})#,
#                 ('Parameters for CAMB (only if using non-default camb run)', {'fields':['do_nonlinear','use_physical','ombh2','omch2','omnuh2',
#                                                                                         'omk','omega_baryon','omega_cdm','omega_lambda','omega_neutrino',
#                                                                                         'w','temp_cmb','helium_fraction','initial_condition',
 #                                                                                        'transfer_high_precision','transfer_kmax','transfer_k_per_logint',
  #                                                                                       'high_accuracy_default','accuracy_boost'],
   #                                                                            'classes':['collapse']})
 #                ]

#admin.site.register(plot_mf, plot_mf_admin)
