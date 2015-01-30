'''
Created on Jun 15, 2012

@author: Steven
'''
from hmf.functional import get_hmf
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
import numpy as np
import logging
# import cosmolopy.distance as cd
# import pandas
import os
# import matplotlib.ticker as tick
import StringIO
import copy
import json
from scipy.interpolate import InterpolatedUnivariateSpline as spline
from django.forms import MultipleChoiceField
# TODO: cosmography doesn't do all redshifts if added at once on an add??

# labels = {"M":'Mass \((M_{\odot}h^{-1})/)',
#           "dndm":r'Mass Function \(\left( \frac{dn}{dM} \right) h^4 Mpc^{-3}\)',
#           "dndlnm":r'Mass Function \(\left( \frac{dn}{d\ln M} \right) h^3 Mpc^{-3}\)',
#           "dndlog10m":r'Mass Function \(\left( \frac{dn}{d\log_{10}M} \right) h^3 Mpc^{-3}\)',
#           "fsigma":r'\(f(\sigma) = \nu f(\nu)\)',
#           "ngtm":r'\(n(>M) h^3 Mpc^{-3}\)',
#           "rho_gtm":r'\(\rho(>M)$, $M_{\odot}h^{2}Mpc^{-3}\)',
#           "rho_ltm":r'\(\rho(<M)$, $M_{\odot}h^{2}Mpc^{-3}\)',
#           "how_big":r'Box Size, \(L\) Mpc\(h^{-1}\)',
#           "sigma":'Mass Variance, \(\sigma\)',
#           "lnsigma":r'\(\ln(\sigma^{-1})\)',
#           "n_eff":r'Effective Spectral Index, \(n_{eff}\)',
#           "power":r'\(\ln(P(k))\), [Mpc\(^3 h^{-3}\)]',
#           "lnk":r"Wavenumber, \(k\) [\(h\)/Mpc]",
#           "transfer":r'\(\ln(T(k))\), [Mpc\(^3 h^{-3}\)]',
#           "delta_k":r'\(\ln(\Delta(k))\)'}
#
# log_labels = {"M":'Mass \((\log_{10}M_{\odot}h^{-1})\)',
#           "dndm":r'Mass Function \(\left( \log_{10}\frac{dn}{dM} \right) h^4 Mpc^{-3}\)',
#           "dndlnm":r'Mass Function \(\left( \log_{10}\frac{dn}{d\ln M} \right) h^3 Mpc^{-3}\)',
#           "dndlog10m":r'Mass Function \(\left( \log_{10}\frac{dn}{d\log_{10}M} \right) h^3 Mpc^{-3}\)',
#           "fsigma":r'\(\log_{10}f(\sigma) = \log_{10}(\nu f(\nu))\)',
#           "ngtm":r'\(\log_{10}n(>M) h^3 Mpc^{-3}\)',
#           "rho_gtm":r'\(\log_{10}\rho(>M)\), \(M_{\odot}h^{2}Mpc^{-3}\)',
#           "rho_ltm":r'\(\log_{10}\rho(<M)\), \(M_{\odot}h^{2}Mpc^{-3}\)',
#           "how_big":r'Box Size, \(\log_{10}L\) Mpc\(h^{-1}\)',
#           "sigma":'Mass Variance, \(\log_{10}\sigma\)',
#           "lnsigma":r'\(\ln(\sigma^{-1})\)',
#           "n_eff":r'Effective Spectral Index, \(\log_{10}n_{eff}\)',
#           "power":r'\(\ln(P(k))\), [Mpc\(^3 h^{-3}\)]',
#           "lnk":r"Wavenumber, \(\log_{10}k\) [\(h\)/Mpc]",
#           "transfer":r'\(\ln(T(k))$, [Mpc$^3 h^{-3}\)]',
#           "delta_k":r'\(\ln(\Delta(k))\)'}

# For now at least, the axis labels must be in non-latex format.
labels_txt = {"M":'Mass [log10 M_sun/h])',
              "dndm":r'Mass Function, dn/dm [h^4 Mpc^-3]',
              "dndlnm":r'Mass Function, dn/dln(m) [h^3 Mpc^-3]',
              "dndlog10m":r'Mass Function, dn/dlog10(m) [h^3 Mpc^-3]',
              "fsigma":r'Fitting Function, f(sigma)',
              "ngtm":r'Cumulative Mass Function, n(>m) [h^3 Mpc^-3]',
              "rho_gtm":r'Cumulative Density, rho(>m) [h^2 Mpc^-3]',
              "rho_ltm":r'Cumulative Density, rho(<m) [h^2 Mpc^-3]',
              "how_big":r'Box Size, [Mpc h^-1]',
              "sigma":'Mass Variance, sigma',
              "nu": "Peak height, nu = (d_c/sigma)^2",
              "lnsigma":r'ln(1/sigma)',
              "n_eff":r'Effective Spectral Index, n_eff',
              "_dlnsdlnm":r"dln(sigma)/dln(m)",
              "power":r'Power Spectrum, ln(P(k)) [Mpc^3 h^-3]',
              "lnk":r"Wavenumber, ln(k) [h/Mpc]",
              "transfer":r'Transfer Function, ln(T(k)) [Mpc^3 h^-3]',
              "delta_k":r'Dimensionless Power, ln(Delta(k))'}

labels = {"M":'Mass [log<sub>10</sub>M<sub>&#x2299</sub>/h])',
          "dndm":r'Mass Function, dn/dm [h<sup>4</sup>Mpc<sup>-3</sup>]',
          "dndlnm":r'Mass Function, dn/dln(m) [h<sup>3</sup>Mpc<sup>-3</sup>]',
          "dndlog10m":r'Mass Function, dn/dlog<sub>10</sub>(m) [h<sup>3</sup>Mpc<sup>-3</sup>]',
          "fsigma":r'Fitting Function, f(&#963)',
          "ngtm":r'Cumulative Mass Function, n(>m) [h<sup>3</sup>Mpc<sup>-3</sup>]',
          "rho_gtm":r'Cumulative Density, &#961(>m) [h<sup>2</sup>Mpc<sup>-3</sup>]',
          "rho_ltm":r'Cumulative Density, &#961(<m) [h<sup>2</sup>Mpc<sup>-3</sup>]',
          "how_big":r'Box Size, [Mpc h<sup>-1</sup>]',
          "sigma":'Mass Variance, &#963',
          "nu":"Peak height, &#957 = (&#948<sub>c</sub>/&#963)<sup>2</sup>",
          "lnsigma":r'ln(1/&#963)',
          "n_eff":r'Effective Spectral Index, n<sub>eff</sub>',
          "_dlnsdlnm":r"dln(&#963)/dln(m)",
          "power":r'Power Spectrum, ln(P(k)) [Mpc<sup>3</sup>h<sup>-3</sup>]',
          "lnk":r"Wavenumber, ln(k) [h/Mpc]",
          "transfer":r'Transfer Function, ln(T(k)) [Mpc<sup>3</sup>h<sup>-3</sup>]',
          "delta_k":r'Dimensionless Power, ln(&#916(k))'}

log_labels = {"M":'Mass [log<sub>10</sub>M<sub>&#x2299</sub>/h]',
          "dndm":r'Mass Function, log<sub>10</sub>(dn/dm) [h<sup>4</sup>Mpc<sup>-3</sup>]',
          "dndlnm":r'Mass Function, log<sub>10</sub>(dn/dln(m)) [h<sup>3</sup>Mpc<sup>-3</sup>]',
          "dndlog10m":r'Mass Function, log<sub>10</sub>(dn/dlog<sub>10</sub>(m)) [h<sup>3</sup>Mpc<sup>-3</sup>]',
          "fsigma":r'Fitting Function, log<sub>10</sub>(f(&#963))',
          "ngtm":r'Cumulative Mass Function, log<sub>10</sub>(n(>m)) [h<sup>3</sup>Mpc<sup>-3</sup>]',
          "rho_gtm":r'Cumulative Density, log<sub>10</sub>(&#961(>m)) [h<sup>2</sup>Mpc<sup>-3</sup>]',
          "rho_ltm":r'Cumulative Density, log<sub>10</sub>(&#961(<m)) [h<sup>2</sup>Mpc<sup>-3</sup>]',
          "how_big":r'Box Size, log<sub>10</sub>(L) [Mpc h<sup>-1</sup>]',
          "sigma":'Mass Variance, log<sub>10</sub>(&#963)',
          "nu":"Peak height, log<sub>10</sub>&#957 = log<sub>10</sub>(&#948<sub>c</sub>/&#963)<sup>2</sup>",
          "lnsigma":r'ln(1/&#963)',
          "n_eff":r'Effective Spectral Index, log<sub>10</sub>(n<sub>eff</sub>)',
          "_dlnsdlnm":r"log<sub>10</sub>(dln(&#963)/dln(m))",
          "power":r'Power Spectrum, ln(P(k)) [Mpc<sup>3</sup>h<sup>-3</sup>]',
          "lnk":r"Wavenumber, ln(k) [h/Mpc]",
          "transfer":r'Transfer Function, ln(T(k)) [Mpc<sup>3</sup>h<sup>-3</sup>]',
          "delta_k":r'Dimensionless Power, ln(&#916(k))'}

#           "comparison_dndm":r'Ratio of Mass Functions $ \left(\frac{dn}{dM}\right) / \left( \frac{dn}{dM} \right)_{%s} $' % labels[0],
#                       "yscale":'log',
#                       "basey":2},
#               "comparison_fsigma":{"xlab":r'Mass $(M_{\odot}h^{-1})$',
#                       "ylab":r'Ratio of Fitting Functions $f(\sigma)/ f(\sigma)_{%s}$' % labels[0],
#                       "yscale":'log',
#                       "basey":2}
#               }

def hmf_driver(label, transfer_fit,
               transfer_options,
               **kwargs):  # A dictionary of bools for optional extra plots.

    # Change directory to this file (for picking up transfer files if pre-made)
    os.chdir(os.path.dirname(__file__))

    # Set up a logger
    hmflog = logging.getLogger("hmf")
    stream = StringIO.StringIO()
    ch = logging.StreamHandler(stream)
    hmflog.addHandler(ch)

    # Appropriately handle WDM
    if len(kwargs["wdm_mass"]) == 0:
        kwargs["wdm_mass"] = [None]
    objects = []
    labels = []
    for res in get_hmf('dndm', get_label=True, transfer_fit=transfer_fit,
                       transfer_options=transfer_options, **kwargs):
        objects += [copy.deepcopy(res[1])]
        l = (label + " " + res[2])

        labels += [sanitise_label(l)]

    warnings = stream.buflist
    warnings = list(set(warnings))
    return objects, labels, warnings

def sanitise_label(l):
        # Sanitise label, which needs to be used as html id, html text, and url,
        # as well as plot annotations.
        # Because of this, use only alphnumeric characters (no underscore), with
        # hyphens for spaces and : for associations, plus . for decimals
        l = l.strip().replace(": ", ":").replace(" ", "-")
        return l

def make_json_data(x, y, models, compare, new_models=[]):
    """
    Creates a JSON object containing javascript Arrays for the data and labels
    
    All quantities are interpolated onto the same grid, so that they may be
    simply compared. 
    """
    # Make the new labels into appropriate HTML
    extra_labels = ""
    if isinstance(new_models, basestring):
        extra_labels = new_models
    else:
        for lab in new_models:
            primary_lab = "-empty" if (len(models) > 1 and lab != compare) else " "

            extra_labels += """
    <div class="col-md-12 modelbar" id="%s">
        <div class="col-md-6 model-label">%s</div> 
        <div class="btn-group">
            <button type="button" class="btn btn-default edit">
                <span class="glyphicon glyphicon-pencil"></span>
            </button>
            <button type="button" class="btn btn-default add">
                <span class="glyphicon glyphicon-plus"></span>
            </button>
            <button type="button" class="btn btn-default delete">
                <span class="glyphicon glyphicon-remove"></span>
            </button>
            <button type="button" class="btn btn-default primary">
                <span class="glyphicon glyphicon-star%s"></span>
            </button>
        </div>
    </div>""" % (lab, lab, primary_lab)
    # TODO: do visibility buttons properly
#             <button type="button" class="btn btn-default visibility">
#                 <span class="glyphicon glyphicon-eye-open"></span>
#             </button>
    objects = [models[l]['data'] for l in models.keys()]
    alabels = models.keys()

    # First determine xmin and xmax
    xmins = np.array([getattr(o, x)[np.logical_and(np.logical_not(np.isnan(getattr(o, x))), np.logical_not(np.isnan(getattr(o, y))))].min() for o in objects])
    xmaxs = np.array([getattr(o, x)[np.logical_and(np.logical_not(np.isnan(getattr(o, x))), np.logical_not(np.isnan(getattr(o, y))))].max() for o in objects])


    xmin = np.min(xmins)
    xmax = np.max(xmaxs)

    print "xmin, xmax: ", xmins, xmaxs
    # Deduce whether to log by dynamic range??
    # (ONLY SINCE THERE'S NO LOG-X FUNCTIONALITY IN DYGRAPHS)
    outarray = np.empty((len(objects) + 1, 500), dtype="object")
    outarray[:, :] = np.nan

    if xmax / xmin > 1e4:
        xvec = np.exp(np.linspace(np.log(xmin), np.log(xmax), 500))
        outarray[0] = np.log10(xvec)
        xlabel = log_labels[x]
    else:
        xvec = np.linspace(xmin, xmax, 500)
        outarray[0] = xvec
        xlabel = labels[x]

    ylabel = labels[y]
    # Get yvec for each model
    for i, o in enumerate(objects):
        inds = np.logical_and(xvec >= xmins[i], xvec <= xmaxs[i])
        xvals = getattr(o, x)
        sort = np.argsort(xvals)
        xvals = xvals[sort]
        yvals = getattr(o, y)[sort]

        # weed out nan values
        nan_inds = np.logical_and(np.logical_not(np.isnan(xvals)), np.logical_not(np.isnan(yvals)))
#         inds = np.logical_and(inds, nan_inds)
        xvals = xvals[nan_inds]
        yvals = yvals[nan_inds]

        print xvals.min(), xvals.max(), yvals.min(), yvals.max()
#         if yvals.max() / yvals.min() > 1e4:
#             s = spline(xvals, np.log(yvals))
#             outarray[i + 1][inds] = np.exp(s(xvec))[inds]
#         else:
        s = spline(xvals, yvals)
        outarray[i + 1][inds] = s(xvec)[inds]

    if compare is not None:
        ref = outarray[alabels.index(compare) + 1].copy()
        for i in range(len(objects)):
            outarray[i + 1] /= ref

    # Set nan's to None
    data = [[None if np.isnan(xx) else xx for xx in a] for a in outarray.T.tolist()]

    outdict = {'csv': data, "labels":[x] + alabels, "xlabel":xlabel,
                      "ylabel":ylabel, "new_labels":extra_labels}

    return outdict

def save_form_object(objects, labels, form, **weird_ones):
    form_params = []
    for i, o in enumerate(objects):
        form_params.append({})
        for field in form.fields:
            try:
                form_params[i][field] = str(getattr(o, field))

                # Some special cases
                if form_params[i][field] == "None":
                    form_params[i][field] = ""
                if type(form.fields[field]) == MultipleChoiceField:
                    form_params[i][field] = [form_params[i][field]]

            except AttributeError:
                if field == "label":
                    form_params[i][field] = labels[i]



        form_params[i].update(weird_ones)
    return form_params

tablabels = {"growth":"Growth Rate",
             "age":"Age at z",
             "cdist":"Comoving Dist. [Mpc/h]"}

def create_table(quantities, models):
    """Similar to make_json_data, except it does the table information"""

    objects = [models[l]['data'] for l in models.keys()]
    alabels = models.keys()

    print "Here are the labels: ", alabels

    # Write table heading
    tabstring = "<thead><tr><th>Model</th>"
    for q in quantities:
        tabstring += "<th>%s</th>" % tablabels[q]
    tabstring += "</tr></thead>"

    # Write each entry
    for i, o in enumerate(objects):
        tabstring += "<tr><th>%s</th>" % alabels[i]
        for q in quantities:
            try:
                val = getattr(o, q)
            except AttributeError:
                if q == "age":
                    # FIXME
                    val = 1
                elif q == "cdist":
                    val = 2

            tabstring += "<td>%s</td>" % val
            print alabels[i], q, val
        tabstring += "</tr>"

    return {"table":tabstring}

#
# def cosmography(objects, labels):
#
#     ######################################################
#     # COSMOGRAPHY
#     ######################################################
#     distances = []
#
#
#     for i, cosmology in enumerate(cosmology_list):
#         # Set a cosmology for cosmolopy
#         cosmo = {'omega_M_0':cosmology['omegab'] + cosmology['omegac'],
#                  'omega_lambda_0':cosmology['omegav'],
#                  'h':cosmology['H0'] / 100.0,
#                  'omega_b_0':cosmology['omegab'],
#                  'omega_n_0':0,  # cosmology['omegan'],
#                  'N_nu':0,
#                  'n':cosmology['n'],
#                  'sigma_8':cosmology['sigma_8']}
#
#         cd.set_omega_k_0(cosmo)
#
#         # Age of the Universe
#         for j, z in enumerate(redshifts):
#             distances = distances + [[cosmo_labels[i],
#                                       z,
#                                       cd.age(z, use_flat=False, **cosmo) / (3600 * 24 * 365.25 * 10 ** 9),
#                                       cd.comoving_distance(z, **cosmo) / 1000,
#                                       cd.comoving_volume(z, **cosmo) / 10 ** 9,
#                                       cd.angular_diameter_distance(z, **cosmo) / 1000,
#                                       cd.luminosity_distance(z, **cosmo) / 1000,
#                                       growth[i][j]],
#                                      ]
#
#
#
#     return distances
#
# def create_canvas(objects, labels, q, d):
#     # TODO: make log scaling automatic
#     fig = Figure(figsize=(11, 6), edgecolor='white', facecolor='white', dpi=100)
#     ax = fig.add_subplot(111)
# #     ax.set_title(title)
#     ax.grid(True)
#     ax.set_xlabel(d["xlab"])
#     ax.set_ylabel(d["ylab"])
#
#     linecolours = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
#     lines = ["-", "--", "-.", ":"]
#
#     if q.startswith("comparison"):
#         compare = True
#         q = q[11:]
#     else:
#         compare = False
#
#     if len(objects[0].M) == len(getattr(objects[0], q)):
#         x = "M"
#     else:
#         x = "lnk"
#
#     if not compare:
#         for i, o in enumerate(objects):
#             y = getattr(o, q)
#             ax.plot(getattr(o, x), y,
#                     color=linecolours[(i / 4) % 7],
#                     linestyle=lines[i % 4],
#                     label=labels[i]
#                     )
#     else:
#         for i, o in enumerate(objects[1:]):
#             y = getattr(o, q) / getattr(objects[0], q)
#             ax.plot(getattr(o, x) , y,
#                     color=linecolours[((i + 1) / 4) % 7],
#                     linestyle=lines[(i + 1) % 4],
#                     label=labels[i + 1]
#                     )
#
#     # Shrink current axis by 30%
#     if x != 'lnk':
#         ax.set_xscale('log')
#
#     ax.set_yscale(d["yscale"], basey=d.get("basey", 10))
#     if d['yscale'] == 'log':
#         if d.get("basey", 10) == 2:
#             ax.yaxis.set_major_formatter(tick.ScalarFormatter())
#
#     box = ax.get_position()
#     ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])
#
#     # Put a legend to the right of the current axis
#     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#     # fig.tight_layout()
#
#     canvas = FigureCanvas(fig)
#     return canvas

