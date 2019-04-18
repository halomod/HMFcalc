from django.http import HttpResponse , HttpResponseRedirect
# from django.shortcuts import render  # ,get_object_or_404, render_to_response, redirect
# from django.utils.encoding import iri_to_uri
# from django.core.context_processors import csrf
# from django.template import RequestContext
import utils
import forms
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# import numpy as np
import datetime
# import logging
import StringIO
import zipfile
# import time
import os

from tabination.views import TabView
from hmf.hmf import version
from django.conf import settings
from . import version as calc_version
import django
from django.core.mail.backends.smtp import EmailBackend
from django.template import RequestContext
import numpy as np
import json
import pickle
import copy
# TODO: figure out why some pages don't display the navbar menu

# def index(request):
#   return HttpResponseRedirect('/admin/')

# class BaseTab(TabView):
#     """Base class for all main navigation tabs."""
#     tab_group = 'main'
#     top = True

class Home(TemplateView):
    """
    The home-page. Should just be simple html with links to what to do.
    """
    template_name = 'home.html'


class InfoParent(TemplateView):
    template_name = 'doesnt_exist.html'

class Help(TemplateView):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    template_name = 'help.html'

class Contact(TemplateView):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    template_name = 'contact_info.html'

class Resources(TemplateView):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    template_name = 'resources.html'

class Acknowledgments(TemplateView):
    """
    A simple html 'end-page' which shows information about parameters used.
    """
    template_name = 'acknowledgments.html'

class Calculator(TemplateView):
    template_name = 'calculator.html'

    def render_to_response(self, context, **response_kwargs):
        """
        Here we instantiate the objects properly so that there is something
        drawn straight away.
        """
        if "models" not in self.request.session:
            self.request.session = initialise(self.request.session)

        return super(Calculator, self).render_to_response(context, **response_kwargs)



def refresh(request, new=None):
    plotdict = get_plot_dict(request.session, new)
    tabdict = refresh_table_dict(request.session)
    plotdict.update(tabdict)
    return HttpResponse(json.dumps(plotdict), content_type='application/json')

def redraw_plot(request, new=None):
    plotdict = get_plot_dict(request.session, new)
    return HttpResponse(json.dumps(plotdict), content_type='application/json')

def get_plot_dict(session, new=None):
    """
    Re-draws everything from the session. Called on page-(re)load
    """
    x, y = session["axes"]

    if new is None:
        new = [l for l in session['models']]

    outdict = utils.make_json_data(x, y, session['models'],
                                   session['compare_mod'] if session['compare'] else None,
                                   new)
    return outdict

def remake_table(request):
    tabdict = refresh_table_dict(request.session)
    return HttpResponse(json.dumps(tabdict), content_type='application/json')

def refresh_table_dict(session):
    columns = session['scalar_columns']
    outdict = utils.create_table(columns, session['models'])
    return outdict


def set_compare_model(request):
    """
    Sets clicked model as model which is compared to.
    """
    model = request.POST['label']
    request.session['compare_mod'] = model
    response = redraw_plot(request)
    return response

def switch_compare(request):
    request.session["compare"] = not request.session['compare']
    response = redraw_plot(request)
    return response

class Input(FormView):
    template_name = 'input.html'
    form_class = forms.HMFInput
    success_url = reverse_lazy('hmf-calculator')

    def form_valid(self, form):
        #========= Set the Transfer Function File correctly ===== #
        transfer_file = form.cleaned_data.pop("transfer_file")
        transfer_options = {}
        transfer_fit = form.cleaned_data.pop("transfer_fit")
        tfile = form.cleaned_data.pop('transfer_file_upload')
        if transfer_file == 'custom':
            if transfer_fit == "FromFile":
                transfer_options = {"fname":tfile}
        else:
            transfer_fit = "FromFile"
            transfer_options = {"fname":transfer_file}

        # possibly need to fix this later
        del form.cleaned_data['wdm_model']


        label = form.cleaned_data.pop('label')

        # Calculate all objects
        objects, labels, warnings = utils.hmf_driver(label, transfer_fit, transfer_options, **form.cleaned_data)

        # Save the model
        fparams = utils.save_form_object(objects, labels, form,
                                         # the rest are added directly
                                         transfer_file=transfer_file,
                                         transfer_fit=transfer_fit, transfer_file_upload=tfile,
                                         mu=form.cleaned_data['wdm_params']['mu'],
                                         g_x=form.cleaned_data['wdm_params']['g_x'])

        new = {labels[i]:{"data":objects[i], "form":fparams[i]} for i in range(len(objects))}  # No warnings as yet


#         if self.kwargs['mode'] == "add":
#             self.request.session['objects'] += objects
#             self.request.session['labels'] += labels
#             self.request.session['warnings'] += warnings
#             self.request.session['form_params'] += fparams
#         elif self.kwargs['mode'] == "edit":
#             self.request.session['objects'][ind] = objects[0]
#             self.request.session['labels'][ind] = labels[0]
#             self.request.session['warnings'] = warnings  # #obviously wrong
#             self.request.session['form_params'][ind] = fparams[0]
#         else:
#             raise ValueError("Mode should be add or edit, got" + self.kwargs['mode'])

        if self.kwargs['mode'] == "add":
            self.request.session["models"].update(new)
            response = refresh(self.request, labels)
#             out = utils.make_json_data(x, y, self.request.session["models"],
#                                        self.request.session['compare_mod'] if self.request.session['compare'] else None,
#                                        labels)
        elif self.kwargs['mode'] == "edit":
            del self.request.session['models'][self.kwargs['label']]
            self.request.session["models"].update(new)
            # Don't add new modelbar elements
            response = refresh(self.request, labels[0])
#             out = utils.make_json_data(x, y, self.request.session["models"],
#                                        self.request.session['compare_mod'] if self.request.session['compare'] else None, labels[0])
            # Need to re-set primary if this is it
            if self.request.session['compare_mod'] == self.kwargs['label']:
                self.request.session['compare_mod'] = labels[0]

        else:
            raise ValueError("Mode should be add or edit, got" + self.kwargs['mode'])

        return response

    def get_initial(self):
        """
        Optionally add dynamic initial data to the form based on "edited" model
        """
        try:
            # apparently need to copy it or it alters the session!
            initial = copy.copy(self.request.session['models'][self.kwargs['label']]['form'])
        except KeyError:
            raise

        if self.kwargs['mode'] == "add":
            initial['label'] = "new-" + initial['label']
        return initial

    def get_form_kwargs(self):
        kwargs = super(Input, self).get_form_kwargs()
        kwargs['labels'] = [l for l in self.request.session['models']]
        if self.kwargs['mode'] == "add":
            kwargs['add'] = True
        else:
            kwargs['add'] = False
        return kwargs

class Axes(FormView):
    template_name = 'axes.html'
    form_class = forms.Axes
    success_url = reverse_lazy('hmf-calculator')

    def form_valid(self, form):
        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        self.request.session['axes'] = (x, y)


#         out = utils.make_json_data(x, y, self.request.session['models'],
#                                    self.request.session['compare_mod'] if self.request.session['compare'] else None)
        return redraw_plot(self.request, [])

class Download(FormView):
    template_name = 'download.html'
    form_class = forms.Download
    success_url = reverse_lazy('hmf-calculator')

    def form_valid(self, form):
        self.request.session['data-download'] = {"m":form.cleaned_data['m'],
                                                 "k":form.cleaned_data['k']}
        return HttpResponse("")

class TabEdit(FormView):
    template_name = 'table_edit.html'
    form_class = forms.EditTable
    success_url = reverse_lazy('hmf-calculator')

    def form_valid(self, form):
        self.request.session['scalar_columns'] = form.cleaned_data["quantities"]
        response = remake_table(self.request)
        return response

    def get_form_kwargs(self):
        kwargs = super(TabEdit, self).get_form_kwargs()
        kwargs['current'] = self.request.session['scalar_columns']
        return kwargs

def downloader(request):
    # Open up file-like objects for response
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=HMFcalc_data.zip'
    buff = StringIO.StringIO()
    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

    # Write out mass-based and k-based data files
    for k, v in request.session['models'].iteritems():
        s = StringIO.StringIO()
        o = v['data']

        # MASS BASED
        if len(request.session['data-download']['m']) > 0:
            for i, q in enumerate(request.session['data-download']['m']):
                s.write("# [%s] %s\n" % (i, utils.labels_txt[q]))

            out = np.array([getattr(o, q) for q in request.session['data-download']['m']]).T
            np.savetxt(s, out)
            archive.writestr('mVector_%s.txt' % k, s.getvalue())
            s.close()

        s = StringIO.StringIO()

        # K BASED
        if len(request.session['data-download']['k']) > 0:
            for i, q in enumerate(request.session['data-download']['k']):
                s.write("# [%s] %s\n" % (i, utils.labels_txt[q]))

            out = np.array([getattr(o, q) for q in request.session['data-download']['k']]).T
            np.savetxt(s, out)
            archive.writestr('kVector_%s.txt' % k, s.getvalue())

    archive.close()
    buff.flush()
    ret_zip = buff.getvalue()
    buff.close()
    response.write(ret_zip)
    return response

def y_selector(request):
    xval = request.POST['xval']

    mchoices = [a[0] for a in forms.Axes.m_choices]

    if xval in mchoices:
        thevars = forms.Axes.m_choices
    else:
        thevars = forms.Axes.k_choices

    response = ""
    for var, label in thevars:
        if var != xval:
            response += '<option value="%s">%s</option>\n' % (var, label)

    return HttpResponse(response)

def remove_single_entry(request):
    key = request.POST['label']
    try:
        del request.session['models'][key]
    except:
        pass

    return refresh(request, [])

def clear_all(request):
    request.session = initialise(request.session)
    print "CLEARING"
    return refresh(request)


# class HMFInputParent(BaseTab):
#     _is_tab = True
#     tab_id = 'form-parent'
#     tab_label = 'Calculate'
#     template_name = 'also_doesnt_exist.html'
#     my_children = ['/hmf_finder/form/create/', '/hmf_finder/form/add/']
#
#
# class HMFInputChild(BaseTab):
#     """Base class for all child navigation tabs."""
#     # tab_parent = HMFInputParent
#     pass
#
# class HMFInputCreate(HMFInputBase, HMFInputChild):
#
#     # This defines whether to add the M-bounds fields to the form (here we do)
#     def get_form_kwargs(self):
#         kwargs = super(HMFInputBase, self).get_form_kwargs()
#         kwargs.update({
#             'add' : 'create'
#         })
#         return kwargs
#
#     # We must define 'get' as TabView is based on TemplateView which has a different form for get (form variable lost).
#     def get(self, request, *args, **kwargs):
#         """
#         Handles GET requests and instantiates a blank version of the form.
#         """
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         return self.render_to_response(self.get_context_data(form=form))
#
#     # TabView-specific things
#     _is_tab = True
#     tab_id = '/hmf_finder/form/create/'
#     tab_label = 'Begin New'
#     top = False
#
#
#
# class HMFInputAdd(HMFInputBase, HMFInputChild):
#
#     def get_form_kwargs(self):
#         kwargs = super(HMFInputBase, self).get_form_kwargs()
#         kwargs.update({
#              'add' : 'add',
#              'minm' : self.request.session['Mmin'],
#              'maxm' : self.request.session['Mmax'],
#              'labels': self.request.session['base_labels']
#         })
#         return kwargs
#
#     def get(self, request, *args, **kwargs):
#         """
#         Handles GET requests and instantiates a blank version of the form.
#         """
#         if 'Mmin' not in self.request.session:
#             return HttpResponseRedirect('/hmf_finder/form/create/')
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         return self.render_to_response(self.get_context_data(form=form))
#
#     _is_tab = True
#     tab_id = '/hmf_finder/form/add/'
#     top = False
#     tab_label = "Add Extra Plots"
#
#     @property
#     def tab_visible(self):
#         return "Mmin" in self.current_tab.request.session and "Mmax" in self.current_tab.request.session

#
# class ViewPlots(BaseTab):
#
# #     def collect_dist(self, distances):
# #         final_d = []
# #         collected_cosmos = []
# #         collected_z = []
# #         for dist in distances:  # dist is one matrix of distances
# #             for d in dist:  # d is one vector (different calculations - a row of final table)
# #                 if d[0] in collected_cosmos and d[1] in collected_z:
# #                     b = [item for item in range(len(collected_cosmos)) if collected_cosmos[item] == d[0]]
# #                     if d[1] in b:
# #                         break
# #                     else:
# #                         collected_cosmos = collected_cosmos + [d[0]]
# #                         collected_z = collected_z + [d[1]]
# #                 collected_cosmos = collected_cosmos + [d[0]]
# #                 collected_z = collected_z + [d[1]]
# #                 final_d = final_d + [d]
# #         return final_d
#
#     def get(self, request, *args, **kwargs):
#         if 'objects' in request.session:
#             self.form = forms.PlotChoice(request)
#         else:
#             return HttpResponseRedirect('/hmf_finder/form/create/')
# #         distances = request.session['distances']
#         self.warnings = request.session['warnings']
# #         self.final_dist = self.collect_dist(distances)
#         return self.render_to_response(self.get_context_data(form=self.form, warnings=self.warnings))
#
#     template_name = 'hmf_image_page.html'
#     _is_tab = True
#     tab_id = '/hmf_finder/hmf_image_page/'
#     tab_label = 'View Plots'
#     top = True
#
#     @property
#     def tab_visible(self):
#         return "objects" in self.current_tab.request.session

def plots(request, filetype, plottype):
    """
    Chooses the type of plot needed and the filetype (pdf or png) and outputs it
    """
    # TODO: give user an option for ylim dynamically?
    if "objects" not in request.session:
        return HttpResponseRedirect('/hmf_finder/form/create/')
    else:
        pass

    objects = request.session["objects"]
    labels = request.session['labels']

    keymap = {"dndm":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Mass Function $\left( \frac{dn}{dM} \right) h^4 Mpc^{-3}$',
                      "yscale":'log'},
              "dndlnm":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Mass Function $\left( \frac{dn}{d\ln M} \right) h^3 Mpc^{-3}$',
                      "yscale":'log'},
              "dndlog10m":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Mass Function $\left( \frac{dn}{d\log_{10}M} \right) h^3 Mpc^{-3}$',
                      "yscale":'log'},
              "fsigma":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'$f(\sigma) = \nu f(\nu)$',
                      "yscale":'linear'},
              "ngtm":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'$n(>M) h^3 Mpc^{-3}$',
                      "yscale":'log'},
              "rho_gtm":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'$\rho(>M)$, $M_{\odot}h^{2}Mpc^{-3}$',
                      "yscale":'log'},
              "rho_ltm":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'$\rho(<M)$, $M_{\odot}h^{2}Mpc^{-3}$',
                      "yscale":'linear'},
              "how_big":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Box Size, $L$ Mpc$h^{-1}$',
                      "yscale":'log'},
              "sigma":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Mass Variance, $\sigma$',
                      "yscale":'linear'},
              "lnsigma":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'$\ln(\sigma^{-1})$',
                      "yscale":'linear'},
              "n_eff":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Effective Spectral Index, $n_{eff}$',
                      "yscale":'linear'},
              "power":{"xlab":r"Wavenumber, $k$ [$h$/Mpc]",
                      "ylab":r'$\ln(P(k))$, [Mpc$^3 h^{-3}$]',
                      "yscale":'linear'},
              "transfer":{"xlab":r"Wavenumber, $k$ [$h$/Mpc]",
                      "ylab":r'$\ln(T(k))$, [Mpc$^3 h^{-3}$]',
                      "yscale":'linear'},
              "delta_k":{"xlab":r"Wavenumber, $k$ [$h$/Mpc]",
                      "ylab":r'$\ln(\Delta(k))$',
                      "yscale":'linear'},
              "comparison_dndm":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Ratio of Mass Functions $ \left(\frac{dn}{dM}\right) / \left( \frac{dn}{dM} \right)_{%s} $' % labels[0],
                      "yscale":'log',
                      "basey":2},
              "comparison_fsigma":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
                      "ylab":r'Ratio of Fitting Functions $f(\sigma)/ f(\sigma)_{%s}$' % labels[0],
                      "yscale":'log',
                      "basey":2}
              }

    canvas = utils.create_canvas(objects, labels, plottype, keymap[plottype])

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
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=parameters.txt'

    # Import all the input form data so it can be written to file
    objects = request.session["objects"]
    labels = request.session['labels']

    # Write the parameter info
    response.write('File Created On: ' + str(datetime.datetime.now()) + '\n')
    response.write('With version ' + calc_version + ' of HMFcalc \n')
    response.write('And version ' + version + ' of hmf (backend) \n')
    response.write('\n')
    response.write('SETS OF PARAMETERS USED \n')
#     response.write('The following blocks indicate sets of parameters that were used in all combinations' + '\n')
    for i, o in enumerate(objects):
        response.write('=====================================================\n')
        response.write("   %s\n" % (labels[i]))
        response.write('=====================================================\n')
        for k in o._Cache__recalc_par_prop.keys():
            response.write("%s: %s \n" % (k, getattr(o, k)))
        response.write("\n")
#
#     for data in formdata:
#         response.write('=====================================================\n')
#         response.write('Redshifts: ' + str(data['z']) + '\n')
#         response.write('WDM Masses: ' + str(data['WDM']) + '\n')
#         response.write('Fitting functions: ' + str(data['approach']) + '\n')
#         response.write('Virial Overdensity: ' + str(data['overdensity']) + '\n')
#         response.write('Transfer Function: ' + str(data['co_transfer_file']) + '\n')
#         response.write('Minimum k: ' + str(data['k_begins_at']) + '\n')
#         response.write('Maximum k: ' + str(data['k_ends_at']) + '\n')
#
#         response.write('Cosmologies: \n')
#         response.write('\n')
#         for j, cosmo in enumerate(data['cp_label']):
#             response.write('' + cosmo + ': \n')
#             response.write('-----------------------------------------------------\n')
#             response.write('Critical Overdensity: ' + str(data['cp_delta_c'][min(j, len(data['cp_delta_c']) - 1)]) + '\n')
#             response.write('Power Spectral Index: ' + str(data['cp_n'][min(j, len(data['cp_n']) - 1)]) + '\n')
#             response.write('Sigma_8: ' + str(data['cp_sigma_8'][min(j, len(data['cp_sigma_8']) - 1)]) + '\n')
#             response.write('Hubble Parameter: ' + str(data['cp_H0'][min(j, len(data['cp_H0']) - 1)]) + '\n')
#             response.write('Omega_b: ' + str(data['cp_omegab'][min(j, len(data['cp_omegab']) - 1)]) + '\n')
#             response.write('Omega_CDM: ' + str(data['cp_omegac'][min(j, len(data['cp_omegac']) - 1)]) + '\n')
#             response.write('Omega_Lambda: ' + str(data['cp_omegav'][min(j, len(data['cp_omegav']) - 1)]) + '\n')
# #            response.write('# w: ' + str(data['cp_w_lam'][min(j, len(data['cp_w_lam']) - 1)]) + '\n')
# #            response.write('# Omega_nu: ' + str(data['cp_omegan'][min(j, len(data['cp_omegan']) - 1)]) + '\n')
#             response.write('-----------------------------------------------------\n')
#         response.write('=====================================================\n')
#         response.write('\n')

        return response

def data_output(request):

    # TODO: output HDF5 format
    # Import all the data we need
    objects = request.session["objects"]
    labels = request.session['labels']

    # Open up file-like objects for response
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=all_plots.zip'
    buff = StringIO.StringIO()
    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

    # Write out mass-based and k-based data files
    for i, o in enumerate(objects):
        s = StringIO.StringIO()

        # MASS BASED
        s.write("# [1] m:            [M_sun/h] \n")
        s.write("# [2] sigma \n")
        s.write("# [3] ln(1/sigma) \n")
        s.write("# [4] n_eff \n")
        s.write("# [5] f(sigma) \n")
        s.write("# [6] dn/dm:        [h^4/(Mpc^3*M_sun)] \n")
        s.write("# [7] dn/dlnm:      [h^3/Mpc^3] \n")
        s.write("# [8] dn/dlog10m:   [h^3/Mpc^3] \n")
        s.write("# [9] n(>m):        [h^3/Mpc^3] \n")
        s.write("# [11] rho(>m):     [M_sun*h^2/Mpc^3] \n")
        s.write("# [11] rho(<m):     [M_sun*h^2/Mpc^3] \n")
        s.write("# [12] Lbox(N=1):   [Mpc/h]\n")

        out = np.array([o.M, o.sigma, o.lnsigma, o.n_eff, o.fsigma, o.dndm, o.dndlnm,
                        o.dndlog10m, o.ngtm, o.rho_gtm, o.rho_ltm, o.how_big]).T
        np.savetxt(s, out)

        archive.writestr('mVector_%s.txt' % labels[i], s.getvalue())

        s.close()
        s = StringIO.StringIO()

        # K BASED
        s.write("# [1] k:    [h/Mpc] \n")
        s.write("# [2] P:    [Mpc^3/h^3] \n")
        s.write("# [3] T:    [Mpc^3/h^3] \n")  # FIXME probably wrong units
        s.write("# [4] Delta_k \n")

        out = np.exp(np.array([o.lnk, o.power, o.transfer, o.delta_k]).T)
        np.savetxt(s, out)
        archive.writestr('kVector_%s.txt' % labels[i], s.getvalue())

    archive.close()
    buff.flush()
    ret_zip = buff.getvalue()
    buff.close()
    response.write(ret_zip)
    return response


# def hmf_all_plots(request):
#
#
#     # First make all the canvases...
#     mass_func_file_like = plots(request, filetype='zip', plottype='hmf')
#     f_file_like = plots(request, filetype='zip', plottype='f')
#     ngtm_file_like = plots(request, filetype='zip', plottype='ngtm')
#     mhmf_file_like = plots(request, filetype='zip', plottype='mhmf')
#     comparison_mf_file_like = plots(request, filetype='zip', plottype='comparison_hmf')
#     comparison_f_file_like = plots(request, filetype='zip', plottype='comparison_f')
#     mgtm_file_like = plots(request, filetype='zip', plottype='Mgtm')
#     sigma_file_like = plots(request, filetype='zip', plottype='sigma')
#     lnsigma_file_like = plots(request, filetype='zip', plottype='lnsigma')
#     n_eff_file_like = plots(request, filetype='zip', plottype='n_eff')
#     power_spec_file_like = plots(request, filetype='zip', plottype='power_spec')
#
#     # ZIP THEM UP
#     response = HttpResponse(mimetype='application/zip')
#     response['Content-Disposition'] = 'attachment; filename=all_plots.zip'
#
#     buff = StringIO.StringIO()
#     archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)
#     archive.writestr('mass_functions.pdf', mass_func_file_like.getvalue())
#     archive.writestr('fitting_functions.pdf', f_file_like.getvalue())
#     archive.writestr('n_gt_m.pdf', ngtm_file_like.getvalue())
#     archive.writestr('mass_by_mass_functions.pdf', mhmf_file_like.getvalue())
#     archive.writestr('mass_function_comparison.pdf', comparison_mf_file_like.getvalue())
#     archive.writestr('fitting_function_comparison.pdf', comparison_f_file_like.getvalue())
#     archive.writestr('mgtm_comparison.pdf', mgtm_file_like.getvalue())
#     archive.writestr('mass_variance.pdf', sigma_file_like.getvalue())
#     archive.writestr('log_one_on_sigma.pdf', lnsigma_file_like.getvalue())
#     archive.writestr('effective_spectral_index.pdf', n_eff_file_like.getvalue())
#     archive.writestr('power_spectrum.pdf', power_spec_file_like.getvalue())
#     archive.close()
#     buff.flush()
#     ret_zip = buff.getvalue()
#     buff.close()
#     response.write(ret_zip)
#     return response


from django.core.mail import send_mail

class ContactFormView(FormView):

    form_class = forms.ContactForm
    template_name = "email_form.html"
    success_url = '/email-sent/'

    def form_valid(self, form):
        message = "{name} / {email} said: ".format(
            name=form.cleaned_data.get('name'),
            email=form.cleaned_data.get('email'))
        message += "\n\n{0}".format(form.cleaned_data.get('message'))
        send_mail(
            subject=form.cleaned_data.get('subject').strip(),
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECIPIENTS],
        )
        return super(ContactFormView, self).form_valid(form)


class EmailSuccess(TemplateView):
    template_name = "email_sent.html"


#===============================================================================
# Some views that just return downloadable content
#===============================================================================
def get_code(request, name):
    suffix = name.split('.')[-1]
    file = os.path.join(settings.ROOT_DIR, "static")
    file = os.path.join(file, name)
    with open(name, 'r') as f:
        if suffix == 'pdf':
            response = HttpResponse(f.read(), content_type="application/pdf")
        elif suffix == "py":
            response = HttpResponse(f.read(), content_type="text/plain")
        elif suffix == "zip":
            response = HttpResponse(f.read(), content_type="application/zip")

        response["Content-Disposition"] = "attachment;filename=" + name
        return response
