from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render  # ,get_object_or_404, render_to_response, redirect
# from django.utils.encoding import iri_to_uri
# from django.core.context_processors import csrf
# from django.template import RequestContext
import utils
import forms
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import numpy as np
import datetime
# import logging
import StringIO
import HMF.settings as settings
import zipfile
import time
import os
# import atpy
import pandas
from tabination.views import TabView
from hmf.Perturbations import version

# def index(request):
#   return HttpResponseRedirect('/admin/')

class BaseTab(TabView):
    """Base class for all main navigation tabs."""
    tab_group = 'main'
    top = True

class home(BaseTab):
    """
    The home-page. Should just be simple html with links to what to do.
    """

    _is_tab = True
    tab_id = '/'
    tab_label = 'Home'
    template_name = 'home.html'


class InfoParent(BaseTab):
    _is_tab = True
    tab_id = 'info'
    tab_label = 'Info'
    template_name = 'doesnt_exist.html'
    my_children = ['/hmf_parameters/', '/hmf_resources/', '/hmf_acknowledgments/', '/hmf_parameter_discussion/', '/contact_info/']

class InfoChild(BaseTab):
    """Base class for all child navigation tabs."""
    tab_parent = InfoParent

class parameters(InfoChild):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    _is_tab = True
    tab_id = '/hmf_parameters/'
    tab_label = 'Parameter Defaults'
    template_name = 'parameters.html'
    top = False

class contact(InfoChild):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    _is_tab = True
    tab_id = '/contact_info/'
    tab_label = 'Contact Info'
    template_name = 'contact_info.html'
    top = False

class resources(InfoChild):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    _is_tab = True
    tab_id = '/hmf_resources/'
    tab_label = 'Extra Resources'
    template_name = 'resources.html'
    top = False

class acknowledgments(InfoChild):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    _is_tab = True
    tab_id = '/hmf_acknowledgments/'
    tab_label = 'Acknowledgments'
    template_name = 'acknowledgments.html'
    top = False

class param_discuss(InfoChild):
    _is_tab = True
    tab_id = '/hmf_parameter_discussion/'
    tab_label = 'Parameter Info'
    template_name = 'parameter_discuss.html'
    top = False


class HMFInputBase(FormView):
    """
    The form for input. 
    """

    #Define the needed variables for FormView class
    form_class = forms.HMFInput
    success_url = '../../hmf_image_page/'
    template_name = 'hmfform.html'

    #Define what to do if the form is valid.
    def form_valid(self, form):
        # log = logging.getLogger(__name__)

        ###############################################################
        # FORM DATA MANIPULATION
        ###############################################################
        #===================== First we save the uploaded file to the server (if there is one) ===============================
        if form.cleaned_data["co_transfer_file_upload"] != None:

            # Add the time to the front of the filename so it doesn't conflict with other uploads
            localtime = time.asctime(time.localtime(time.time())).replace(" ", "").replace(":", "")
            thefile = self.request.FILES["co_transfer_file_upload"]
            default_storage.save(settings.ROOT_DIR + '/public/media/transfer_functions/' + localtime + '_custom_transfer.dat', ContentFile(thefile.read()))
            # Change the name of the file in the form data for later access.
            form.cleaned_data['co_transfer_file_upload'] = settings.ROOT_DIR + '/public/media/transfer_functions/' + localtime + '_custom_transfer.dat'

        #==================== Now save and merge the cosmology ===============================================================
        cosmo_quantities = [key for key in form.cleaned_data.keys() if key.startswith('cp_')]
        n_cosmologies = len(form.cleaned_data['cp_label'])


        cosmology_list = []
        for i in range(n_cosmologies):
            cosmology_list = cosmology_list + [{}]
            for quantity in cosmo_quantities:
                index = min(len(form.cleaned_data[quantity]) - 1, i)
                cosmology_list[i][quantity[3:]] = form.cleaned_data[quantity][index]

        #==================== We make sure the cosmologies are all unique (across adds) =================================
        if self.request.path.endswith('create/'):
            # If we are creating for the first time, just save the labels to the session
            self.request.session["cosmo_labels"] = form.cleaned_data["cp_label"]  # A compressed list of all unique labels
            self.request.session["cosmologies"] = cosmology_list  # A compressed list of dicts of unique parameters.

        elif self.request.path.endswith('add/'):
            # Go through each new label/cosmology added to check uniqueness
            for i, label in enumerate(form.cleaned_data["cp_label"]):
                counter = 0

                # If the label is not unique across adds
                if label in self.request.session['cosmo_labels']:
                    # Extract the cosmological parameters associated with this label from the previous add
                    cosmology = self.request.session['cosmologies'][self.request.session['cosmo_labels'].index(label)]

                    same = True
                    # Check if all the parameters from the old add are the same as the new add. If not, same = False.
                    for key in cosmology_list[i].keys():
                        same = same and cosmology_list[i][key] == cosmology[key]

                    # If the cosmologies aren't the same, then we modify the label to be unique by suffixing a unique integer
                    while label in self.request.session['cosmo_labels'] and not same:
                        counter = counter + 1

                        if counter == 1:
                            # Add a number to the end to make it unique
                            label = label + '(' + str(counter) + ')'
                        else:
                            label = label[:-3] + '(' + str(counter) + ')'

                    # If the cosmologies are unique, the labels are now also unique, so save the new cosmology/label to session.
                    if not same:
                        self.request.session["cosmo_labels"].append(label)
                        self.request.session['cosmologies'].append(cosmology_list[i])

                else:
                    # The label is already unique so just append it to session
                    self.request.session["cosmo_labels"].append(label)
                    self.request.session['cosmologies'].append(cosmology_list[i])

                # Change the label in the form
                form.cleaned_data["cp_label"][i] = label


            form.cleaned_data['min_M'] = self.request.session['min_M']
            form.cleaned_data['max_M'] = self.request.session['max_M']
            form.cleaned_data['M_step'] = self.request.session['M_step']

        #=========== Set the Transfer Function File correctly ===== #
        transfer_file = form.cleaned_data["co_transfer_file"]
        if transfer_file == 'custom':
            if form.cleaned_data["co_transfer_file_upload"] == None:
                transfer_file = None
            else:
                transfer_file = form.cleaned_data['co_transfer_file_upload']

        #=========== Set k-bounds as a list of tuples ==============================#
        min_k = form.cleaned_data['k_begins_at']
        max_k = form.cleaned_data['k_ends_at']
        num_k_bounds = max(len(min_k), len(max_k))
        k_bounds = []
        for i in range(num_k_bounds):
            mink = min_k[min(len(min_k) - 1, i)]
            maxk = max_k[min(len(max_k) - 1, i)]
            k_bounds.append((mink, maxk))

        #============ Set other simple data ========================================#
        approach = []
        if form.cleaned_data['approach']:
            for i in form.cleaned_data["approach"]:
                approach = approach + [str(i)]

        if form.cleaned_data["alternate_model"]:
            approach = approach + ['user_model']

        # DO THE CALCULATIONS
        mass_data, k_data, warnings = utils.hmf_driver(transfer_file=transfer_file,
                                            extrapolate=form.cleaned_data['extrapolate'],
                                            k_bounds=k_bounds,
                                            z_list=form.cleaned_data['z'],
                                            WDM_list=form.cleaned_data['WDM'],
                                            approaches=approach,
                                            overdensities=form.cleaned_data['overdensity'],
                                            cosmology_list=cosmology_list,
                                            min_M=form.cleaned_data['min_M'], max_M=form.cleaned_data['max_M'],
                                            M_step=form.cleaned_data['M_step'],
                                            user_model=form.cleaned_data['alternate_model'],
                                            cosmo_labels=form.cleaned_data['cp_label'],
                                            extra_plots=form.cleaned_data['extra_plots'])

        distances = utils.cosmography(cosmology_list, form.cleaned_data['cp_label'], form.cleaned_data['z'])

        # Delete the uploaded file. Not needed anymore. Maybe should leave it here for adds??.
        if form.cleaned_data["co_transfer_file_upload"] != None:
            os.system("rm " + form.cleaned_data["co_transfer_file_upload"])

        if self.request.path.endswith('add/'):
            self.request.session["mass_data"] = pandas.concat([self.request.session["mass_data"], mass_data], join='inner', axis=1)
            self.request.session["k_data"] = pandas.concat([self.request.session["k_data"], k_data], join='inner', axis=1)
            self.request.session['distances'] = self.request.session['distances'] + [distances]
            self.request.session['input_data'] = self.request.session['input_data'] + [form.cleaned_data]
            self.request.session['warnings'].update(warnings)
            self.request.session['extra_plots'] = list(set(form.cleaned_data['extra_plots'] + self.request.session['extra_plots']))

        elif self.request.path.endswith('create/'):
            self.request.session["mass_data"] = mass_data
            self.request.session["k_data"] = k_data
            self.request.session['distances'] = [distances]
            self.request.session['input_data'] = [form.cleaned_data]
            self.request.session['min_M'] = form.cleaned_data['min_M']
            self.request.session['max_M'] = form.cleaned_data['max_M']
            self.request.session['M_step'] = form.cleaned_data['M_step']
            self.request.session['warnings'] = warnings
            self.request.session['extra_plots'] = form.cleaned_data['extra_plots']


        return super(HMFInputBase, self).form_valid(form)


class HMFInputParent(BaseTab):
    _is_tab = True
    tab_id = 'form-parent'
    tab_label = 'Calculate'
    template_name = 'also_doesnt_exist.html'
    my_children = ['/hmf_finder/form/create/', '/hmf_finder/form/add/']


class HMFInputChild(BaseTab):
    """Base class for all child navigation tabs."""
    tab_parent = HMFInputParent


class HMFInputCreate(HMFInputBase, HMFInputChild):

    #This defines whether to add the M-bounds fields to the form (here we do)
    def get_form_kwargs(self):
        kwargs = super(HMFInputBase, self).get_form_kwargs()
        kwargs.update({
            'add' : 'create'
        })
        return kwargs

    #We must define 'get' as TabView is based on TemplateView which has a different form for get (form variable lost).
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    #TabView-specific things
    _is_tab = True
    tab_id = '/hmf_finder/form/create/'
    tab_label = 'Begin New'
    top = False



class HMFInputAdd(HMFInputBase, HMFInputChild):

    def get_form_kwargs(self):
        kwargs = super(HMFInputBase, self).get_form_kwargs()
        kwargs.update({
             'add' : 'add',
             'minm' : self.request.session['min_M'],
             'maxm' : self.request.session['max_M']
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    _is_tab = True
    tab_id = '/hmf_finder/form/add/'
    top = False
    tab_label = "Add Plots"
    def tab_visible(self):
        return "extrapolate" in self.request.session


class ViewPlots(BaseTab):

    def collect_dist(self, distances):
        final_d = []
        collected_cosmos = []
        collected_z = []
        for dist in distances:  # dist is one matrix of distances
            for d in dist:  # d is one vector (different calculations - a row of final table)
                if d[0] in collected_cosmos and d[1] in collected_z:
                    b = [item for item in range(len(collected_cosmos)) if collected_cosmos[item] == d[0]]
                    if d[1] in b:
                        break
                    else:
                        collected_cosmos = collected_cosmos + [d[0]]
                        collected_z = collected_z + [d[1]]
                collected_cosmos = collected_cosmos + [d[0]]
                collected_z = collected_z + [d[1]]
                final_d = final_d + [d]
        return final_d

    def get(self, request, *args, **kwargs):
        self.form = forms.PlotChoice(request)
        distances = request.session['distances']
        self.warnings = request.session['warnings']
        self.final_dist = self.collect_dist(distances)
        return self.render_to_response(self.get_context_data(form=self.form, distances=self.final_dist, warnings=self.warnings))

    template_name = 'hmf_image_page.html'
    _is_tab = True
    tab_id = '/hmf_finder/hmf_image_page/'
    tab_label = 'View Plots'
    top = True

    def tab_visible(self):
        return "extrapolate" in self.request.session

def plots(request, filetype, plottype):
    """
    Chooses the type of plot needed and the filetype (pdf or png) and outputs it
    """
    # Definitions of plot-types
    mass_plots = ['hmf', 'f', 'ngtm', 'mhmf', 'comparison_hmf',
                  'comparison_f', 'Mgtm', 'nltm', 'Mltm', 'L',
                  'sigma', 'lnsigma', 'n_eff']

    k_plots = ['power_spec']
    print plottype
    # Get data from session object
    if plottype in mass_plots:
        mass_data = request.session["mass_data"]
        masses = mass_data["M"]
        xlab = r'Mass $(M_{\odot}h^{-1})$'
    elif plottype in k_plots:
        k_data = request.session["k_data"]

    # DEFINE THE FUNCTION TO BE PLOTTED
    if plottype in mass_plots:
        if plottype == 'hmf':
            keep = [string for string in mass_data.columns if string.startswith("hmf_")]
            mass_data = mass_data[keep]
            title = 'Mass Function'
            ylab = r'Logarithmic Mass Function $\log_{10} \left( \frac{dn}{d \ln M} \right) h^3 Mpc^{-3}$'
            yscale = 'log'

        elif plottype == 'f':
            keep = [string for string in mass_data.columns if string.startswith("f(sig)_")]
            # mass_data[i].keep_columns(keep)
            mass_data = mass_data[keep]
            title = 'Fraction of Mass Collapsed'
            ylab = r'Fraction of Mass Collapsed, $f(\sigma)$'
            yscale = 'linear'

        elif plottype == 'ngtm':
            keep = [string for string in mass_data.columns if string.startswith("NgtM_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = 'n(>M)'
            ylab = r'$\log_{10}(n(>M)) h^3 Mpc^{-3}$'
            yscale = 'linear'

        elif plottype == 'Mgtm':
            keep = [string for string in mass_data.columns if string.startswith("MgtM_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = 'Total Bound Mass in Haloes Greater Than M'
            ylab = r'Mass(>M), $\log_{10} M_{sun}h^{2}Mpc^{-3}$'
            yscale = 'linear'

        elif plottype == 'nltm':
            keep = [string for string in mass_data.columns if string.startswith("NltM_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = 'n(<M)'
            ylab = r'$\log_{10}(n(>M)) h^3 Mpc^{-3}$'
            yscale = 'linear'

        elif plottype == 'Mltm':
            keep = [string for string in mass_data.columns if string.startswith("MltM_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = 'Total Bound Mass in Haloes Smaller Than M'
            ylab = r'Mass(<M), $\log_{10} M_{sun}h^{2}Mpc^{-3}$'
            yscale = 'linear'

        elif plottype == 'mhmf':
            keep = [string for string in mass_data.columns if string.startswith("M*hmf_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = 'Mass by Mass Function'
            ylab = r'Mass by Mass Function $\left( M\frac{dn}{d \ln M} \right) M_{sun} h^3 Mpc^{-3}$'
            yscale = 'linear'

        elif plottype == 'comparison_hmf':
            keep = [string for string in mass_data.columns if string.startswith("hmf_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            mass_data = mass_data
            first_column = mass_data.columns[0]
            mass_data = mass_data.div(mass_data[first_column], axis=0)
            yscale = 'linear'
            title = 'Comparison of Mass Functions'
            ylab = r'Ratio of Logarithmic Mass Functions $ \left(\frac{dn}{d \ln M}\right) / \left( \frac{dn}{d \ln M} \right)_0 $'

        elif plottype == 'comparison_f':
            keep = [string for string in mass_data.columns if string.startswith("f(sig)_")]
            mass_data = mass_data[keep]

            first_column = mass_data.columns[0]
            mass_data = mass_data.div(mass_data[first_column], axis=0)
            mass_data = mass_data
            yscale = 'linear'
            title = 'Comparison of Fitting Function(s)'
            ylab = r'Fitting Function $ (f(\sigma)/ f(\sigma)_0)$'



        elif plottype == 'L':
            keep = [string for string in mass_data.columns if string.startswith("L(N=1)_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = "Box Size, L, required to expect one halo"
            ylab = "Box Size, L (Mpc/h)"
            yscale = 'log'

        elif plottype == 'sigma':
            keep = [string for string in mass_data.columns if string.startswith("sigma_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = "Mass Variance"
            ylab = r'Mass Variance, $\sigma$'
            yscale = 'linear'

        elif plottype == 'lnsigma':
            keep = [string for string in mass_data.columns if string.startswith("lnsigma_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = "Logarithm of Inverse Sigma"
            ylab = r'$\ln(\sigma^{-1})$'
            yscale = 'linear'

        elif plottype == 'n_eff':
            keep = [string for string in mass_data.columns if string.startswith("neff_")]
            # mass_data.keep_columns(keep)
            mass_data = mass_data[keep]
            title = "Effective Spectral Index"
            ylab = r'Effective Spectral Index, $n_{eff}$'
            yscale = 'linear'

        canvas = utils.create_canvas(masses, mass_data, title, xlab, ylab, yscale)

    else:
        xlab = "Wavenumber"
        if plottype == 'power_spec':
            k_keys = [string for string in k_data.columns if string.startswith("k_")]
            p_keys = [string for string in k_data.columns if string.startswith("P(k)_")]

            title = "Power Spectra"
            ylab = "Power"

        canvas = utils.create_k_canvas(k_data, k_keys, p_keys, title, xlab, ylab)


    # How to output the image
    if filetype == 'png':
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)
    elif filetype == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response["Content-Disposition"] = "attachment;filename=" + plottype + ".pdf"
        canvas.print_pdf(response)

    elif filetype == 'zip':
        response = StringIO.StringIO()
        canvas.print_pdf(response)

    return response

def header_txt(request):
    # Set up the response object as a text file
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=parameters.dat'

    # Import all the input form data so it can be written to file
    formdata = request.session['input_data']

    # Write the parameter info
    response.write('# File Created On: ' + str(datetime.datetime.now()) + '\n')
    response.write('# With version ' + settings.version + ' of HMFcalc \n')
    response.write('# And version ' + version + ' of hmf (backend) \n')
    response.write('# \n')
    response.write('# SETS OF PARAMETERS USED \n')
    response.write('# The following blocks indicate sets of parameters that were used in all combinations' + '\n')
    for data in formdata:
        response.write('# =====================================================\n')
        response.write('# Redshifts: ' + str(data['z']) + '\n')
        response.write('# WDM Masses: ' + str(data['WDM']) + '\n')
        response.write('# Fitting functions: ' + str(data['approach']) + '\n')
        response.write('# Virial Overdensity: ' + str(data['overdensity']) + '\n')
        response.write('# Transfer Function: ' + str(data['co_transfer_file']) + '\n')
        if data['extrapolate']:
            response.write('# Minimum k: ' + str(data['k_begins_at']) + '\n')
            response.write('# Maximum k: ' + str(data['k_ends_at']) + '\n')

        response.write('# Cosmologies: \n')
        response.write('# \n')
        for j, cosmo in enumerate(data['cp_label']):
            response.write('# ' + cosmo + ': \n')
            response.write('# -----------------------------------------------------\n')
            response.write('# Critical Overdensity: ' + str(data['cp_delta_c'][min(j, len(data['cp_delta_c']) - 1)]) + '\n')
            response.write('# Power Spectral Index: ' + str(data['cp_n'][min(j, len(data['cp_n']) - 1)]) + '\n')
            response.write('# Sigma_8: ' + str(data['cp_sigma_8'][min(j, len(data['cp_sigma_8']) - 1)]) + '\n')
            response.write('# Hubble Parameter: ' + str(data['cp_H0'][min(j, len(data['cp_H0']) - 1)]) + '\n')
            response.write('# Omega_b: ' + str(data['cp_omegab'][min(j, len(data['cp_omegab']) - 1)]) + '\n')
            response.write('# Omega_CDM: ' + str(data['cp_omegac'][min(j, len(data['cp_omegac']) - 1)]) + '\n')
            response.write('# Omega_Lambda: ' + str(data['cp_omegav'][min(j, len(data['cp_omegav']) - 1)]) + '\n')
            response.write('# w: ' + str(data['cp_w_lam'][min(j, len(data['cp_w_lam']) - 1)]) + '\n')
            response.write('# Omega_nu: ' + str(data['cp_omegan'][min(j, len(data['cp_omegan']) - 1)]) + '\n')
            response.write('# -----------------------------------------------------\n')
        response.write('# =====================================================\n')
        response.write('# \n')

        return response

def hmf_txt(request):
    # Import all the data we need
    mass_data = request.session["mass_data"]

    # Set up the response object as a text file
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=mass_functions.dat'

    table = mass_data.to_string(index_names=False, index=False)
    response.write(table)

    return response

def power_txt(request):
    # Import all the data we need
    k_data = request.session["k_data"]

    # Set up the response object as a text file
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=power_spectra.dat'

    table = k_data.to_string(index_names=False, index=False)
    response.write(table)

    return response

def hmf_all_plots(request):


    # First make all the canvases...
    mass_func_file_like = plots(request, filetype='zip', plottype='hmf')
    f_file_like = plots(request, filetype='zip', plottype='f')
    ngtm_file_like = plots(request, filetype='zip', plottype='ngtm')
    mhmf_file_like = plots(request, filetype='zip', plottype='mhmf')
    comparison_mf_file_like = plots(request, filetype='zip', plottype='comparison_hmf')
    comparison_f_file_like = plots(request, filetype='zip', plottype='comparison_f')
    mgtm_file_like = plots(request, filetype='zip', plottype='Mgtm')
    sigma_file_like = plots(request, filetype='zip', plottype='sigma')
    lnsigma_file_like = plots(request, filetype='zip', plottype='lnsigma')
    n_eff_file_like = plots(request, filetype='zip', plottype='n_eff')
    power_spec_file_like = plots(request, filetype='zip', plottype='power_spec')

    # ZIP THEM UP
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=all_plots.zip'

    buff = StringIO.StringIO()
    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)
    archive.writestr('mass_functions.pdf', mass_func_file_like.getvalue())
    archive.writestr('fitting_functions.pdf', f_file_like.getvalue())
    archive.writestr('n_gt_m.pdf', ngtm_file_like.getvalue())
    archive.writestr('mass_by_mass_functions.pdf', mhmf_file_like.getvalue())
    archive.writestr('mass_function_comparison.pdf', comparison_mf_file_like.getvalue())
    archive.writestr('fitting_function_comparison.pdf', comparison_f_file_like.getvalue())
    archive.writestr('mgtm_comparison.pdf', mgtm_file_like.getvalue())
    archive.writestr('mass_variance.pdf', sigma_file_like.getvalue())
    archive.writestr('log_one_on_sigma.pdf', lnsigma_file_like.getvalue())
    archive.writestr('effective_spectral_index.pdf', n_eff_file_like.getvalue())
    archive.writestr('power_spectrum.pdf', power_spec_file_like.getvalue())
    archive.close()
    buff.flush()
    ret_zip = buff.getvalue()
    buff.close()
    response.write(ret_zip)
    return response
