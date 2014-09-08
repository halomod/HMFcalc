'''
Created on May 3, 2012

@author: smurray
'''

# from django import forms
from django.utils.safestring import mark_safe
import numpy as np
# import floppyforms as forms
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div
from crispy_forms.bootstrap  import TabHolder, Tab, InlineCheckboxes, FormActions
#--------- Custom Form Field for Comma-Separated Input -----
class FloatListField(forms.CharField):
    """
    Defines a form field that accepts comma-separated real values and returns a list of floats.
    """
    def __init__(self, min_val=None, max_val=None, *args, **kwargs):
        self.min_val, self.max_val = min_val, max_val
        super(FloatListField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)

        final_list = []
        if value:
            numbers = value.split(',')
            for number in numbers:
                try:
                    final_list.append(float(number))
                except ValueError:
                    raise forms.ValidationError("%s is not a float" % number)
            for number in final_list:
                if self.min_val is not None:
                    if number < self.min_val:
                        raise forms.ValidationError("Must be greater than " + str(self.min_val) + " (" + str(number) + ")")
                if self.max_val is not None:
                    if number > self.max_val:
                        raise forms.ValidationError("Must be smaller than " + str(self.max_val) + " (" + str(number) + ")")

        return final_list

#------------ THE BIG FORM ------------------------------#
class HMFInput(forms.Form):
    """
    Input parameters to the halo mass function finder.
    """
    #------ Init Method for Dynamic Form -------------
    def __init__(self, add, minm=None, maxm=None, *args, **kwargs):
        self.add = add
        self.minm = minm
        self.maxm = maxm
#        self.hmfform = hmfform
        super (HMFInput, self).__init__(*args, **kwargs)

        if add == 'create':
            # Then we wnat to display min_M and max_M
                # Which values of the radius to use?
            self.fields['Mmin'] = forms.FloatField(label="Minimum Mass",
                                                    initial=10.0,
                                                    help_text=mark_safe("Units of log<sub>10</sub>(M<sub>&#9737</sub>)"),
                                                    min_value=3.0,
                                                    max_value=18.0)
            self.fields['Mmax'] = forms.FloatField(label="Maximum Mass",
                                                    initial=15.0,
                                                    help_text=mark_safe("Units of log<sub>10</sub>(M<sub>&#9737</sub>)"),
                                                    min_value=3.0,
                                                    max_value=18.0)
            self.fields['dlog10m'] = forms.FloatField(label="Mass Bin Width",
                                                     initial=0.05,
                                                     help_text="Logarithmic Bins",
                                                     min_value=0.00001,
                                                     max_value=15.0)
#             hmf_form_choices = [("dndlnm", "dn/dln(M)"),
#                                 ("dndlog10m", "dn/dlog10(M)"),
#                                 ("dndm", "dn/dM")]
#
#             self.fields['hmf_form'] = forms.ChoiceField(label="Form of HMF",
#                                                         initial='dndlnm',
#                                                         choices=hmf_form_choices)

        self.helper = FormHelper()
        self.helper.form_id = 'input_form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.help_text_inline = True


        if add == 'create':
            d = Div('wdm_mass', 'lnk_min', 'lnk_max', 'dlnk', 'cut_fit', 'Mmin', 'Mmax',
                    'dlog10m', css_class='span4')
            # self.helper.add_input(Submit('submit', 'Calculate!'))

        else:
            d = Div('wdm_mass', 'lnk_min', 'lnk_max', 'dlnk', 'cut_fit', css_class='span4')

        self.helper.layout = Layout(TabHolder(
                                              Tab('Run Parameters',
                                                      Div(
                                                          Div('z',
                                                              'delta_h',
                                                              'delta_wrt',
                                                              'mf_fit',
                                                              css_class='span4'
                                                              ),
                                                           d)
#                                                       Div(
#                                                           Fieldset('Optional Extra Plots',
#                                                                    InlineCheckboxes('extra_plots'),
#                                                                    ),
#                                                           css_class='span12'
#
#                                                           )
                                                      ),
                                                  Tab('Cosmological Parameters',
                                                      Div(
                                                          Div('transfer_file',
                                                              'transfer_file_upload',
                                                              'transfer_fit',
                                                              'delta_c',
                                                              'n',
                                                              css_class='span4'
                                                              ),
                                                          Div('sigma_8',
                                                              'H0',
                                                              'omegab',
                                                              'omegac',
                                                              'omegav',
                                                              css_class='span4'
                                                              )
                                                          )
                                                      )
                                                  ),
                                        FormActions(Submit('submit', 'Calculate!', css_class='btn btn-primary btn-large'))
                                        )
    ###########################################################
    # MAIN RUN PARAMETERS
    ###########################################################


    # Redshift at which to calculate the mass variance.
    z = FloatListField(label="Redshifts",
                       initial='0',
                       help_text="Comma-separated list",
                       max_length=50,
                       min_val=0,
                       max_val=1100)

    delta_h = FloatListField(label=mark_safe("&#916<sub>halo</sub>"),
                                 help_text="Comma-separated list",
                                 max_length=50,
                                 initial=200.0,
                                 min_val=10)

    delta_wrt = forms.ChoiceField(label=mark_safe("&#916<sub>halo</sub> with respect to"),
                                  choices=[("mean", "Mean Density"),
                                           ("crit", "Critical Density")],
                                  initial="mean",
                                  required=True,
                                  widget=forms.RadioSelect)

    # WDM particle masses (empty list if none)
    wdm_mass = FloatListField(label="WDM Masses",
                              required=False,
                              help_text="Comma-separated list. In keV (eg. 0.05)",
                              max_length=50,
                              min_val=0.0001)


    # Mass Function fit
    approach_choices = [("PS", "Press-Schechter (1974)"),
                        ("SMT", "Sheth-Mo-Tormen (2001)"),
                        ("Jenkins", "Jenkins (2001)"),
                        ("Reed03", "Reed (2003)"),
                        ("Warren", "Warren (2006)"),
                        ("Reed07", "Reed (2007)"),
                        ("Peacock", "Peaock (2007)"),
                        ("Tinker08", "Tinker (2008)"),
                        ("Crocce", "Crocce (2010)"),
                        ("Courtin", "Courtin (2010)"),
                        ("Tinker10", "Tinker (2010)"),
                        ("Bhattacharya", "Bhattacharya (2011)"),
                        ("Angulo", "Angulo (2012)"),
                        ("AnguloBound", "Angulo (Subhaloes) (2012)"),
                        ("Watson_FoF", "Watson (FoF Universal) (2012)"),
                        ("Watson", "Watson (Redshift Dependent) (2012)"),
                        ("Behroozi", "Behroozi (Tinker Extension to High-z) (2013)")
                        ]

    mf_fit = forms.MultipleChoiceField(label="Fitting Function",
                                       choices=approach_choices,
                                       initial=['SMT'],
                                       required=False)

#     alternate_model = forms.CharField(label=mark_safe('Custom Fitting Function'),
#                                        help_text=mark_safe('Type a fitting function form (<a href="http://docs.scipy.org/doc/numpy/reference/routines.math.html">Python syntax</a>) in terms of mass variance (denoted by x). Eg. for Jenkins: 0.315*exp(-abs(log(1.0/x)+0.61)**3.8)'),
#                                        required=False,
#                                        widget=forms.Textarea(attrs={'cols':'40', 'rows':'3'}))

#     def clean_alternate_model(self):
#         """
#         Performs some simple parsing to check that the alternate model is not rubbish
#         """
#         # TODO: actually make this (clean_alternate_model) catch all exceptions
#         numbers = "0123456789"
#         operators = ["+", "-", "*", "/", "**"]
#         functions = ['sin', 'cos', 'tan', 'abs', 'arctan', 'arccos', 'arcsin', 'exp', "log", "(", ")", "."]
#         values = 'x'
#
#         operators_compressed = "".join(operators)
#         functions_compressed = "".join(functions)
#
#         am = self.cleaned_data.get("alternate_model")
#
#         if am is not None:
#             for i, character in enumerate(am):
#                 if character not in numbers + operators_compressed + functions_compressed + values + " ":
#                     raise forms.ValidationError("The character " + character + " is not recognized")
#                 if character in "+-/" and (am[i - 1] in "+-/" or am[i + 1] in "+-/"):
#                     raise forms.ValidationError("The character " + character + " cannot be next to ", am[i - 1], " and ", am[i + 1])



    transfer_choices = [('transfers/PLANCK_transfer.dat', 'PLANCK'),
                        ('transfers/WMAP9_transfer.dat', 'WMAP9'),
                        ("transfers/WMAP7_transfer.dat", "WMAP7"),
                        ("transfers/WMAP5_transfer.dat", "WMAP5"),
                        ('transfers/WMAP3_transfer.dat', 'WMAP3'),
                        ('transfers/WMAP1_transfer.dat', 'WMAP1'),
                        ("transfers/Millennium_transfer.dat", "Millennium (and WALLABY)"),
                        ("transfers/GiggleZ_transfer.dat", "GiggleZ"),
                        ("custom", "Custom")]

    transfer_fit_choices = [('CAMB', 'CAMB'),
                            ("EH", "Eisenstein-Hu"),
                            ("BBKS", "BBKS"),
                            ("BondEfs", "Bond-Efstathiou"),
                            ("FromFile", "Upload Function")]

    transfer_fit = forms.ChoiceField(label="Transfer Calculator",
                                     choices=transfer_fit_choices,
                                     initial="CAMB")

    transfer_file = forms.ChoiceField(label="Transfer Function",
                                      choices=transfer_choices,
                                      initial="transfers/PLANCK_transfer.dat")

    transfer_file_upload = forms.FileField(label="Upload Transfer Function",
                                           required=False,
                                           help_text="File in CAMB format")

    def clean_transfer_file_upload(self):
        thefile = self.cleaned_data['transfer_file_upload']
        if thefile is not None:
            try:
                np.genfromtxt(thefile)
            except:
                raise forms.ValidationError("Uploaded transfer file is of the wrong format")
#===================================================================
#    RUN PARAMETERS
#===================================================================
    # Extrapolation parameters.
    # extrapolate = forms.BooleanField(label='Extrapolate bounds of k?', initial=True, required=False)
    cut_fit = forms.BooleanField(label="Restrict mass range to fitted range?", initial=True, required=False)
    lnk_max = FloatListField(label="Maximum ln(k)",
                             initial=15.0,
                             help_text="Highest Wavenumber Used, Comma-Separated Decimals",
                             min_val=-15)

    lnk_min = FloatListField(label="Minimum ln(k)",
                             initial=-15,
                             help_text="Lowest Wavenumber Used",
                             max_val=15,
                             min_val=-50)

    dlnk = FloatListField(label="Resolution in ln(k)",
                          initial=0.05,
                          help_text="Bin width of log wavenumber",
                          max_val=15,
                          min_val=0.00001)

#===================================================================
#    OPTIONAL PLOTS
#===================================================================
#     optional_plots = [("get_ngtm", "N(>M)"),
#                         ("get_mgtm", "M(>M)"),
#                         ("get_nltm", "N(<M)"),
#                         ("get_mltm", "M(<M)"),
#                         ("get_L", 'Box Size for One Halo'),
#                         ]
#
#     extra_plots = forms.MultipleChoiceField(label="Optional Extra Plots",
#                                             choices=optional_plots,
#                                             initial=['get_ngtm'],
#                                             required=False)

#===================================================================
#   COSMOLOGICAL PARAMETERS
#===================================================================
#     cp_label = forms.CharField(label="Unique Labels",
#                                initial='WMAP7',
#                                help_text="One unique identifier for each cosmology, separated by commas")

#     def clean_cp_label(self):
#         labels = self.cleaned_data['cp_label']
#         labels = labels.split(',')
#         for i, label in enumerate(labels):
#             lab = label.strip()
#             lab = lab.replace(" ", "_")
#             labels[i] = lab
#         return labels

    # Critical Overdensity corresponding to spherical collapse
    delta_c = FloatListField(label=mark_safe("&#948<sub>c</sub>"),
                                  initial='1.686',
                                  min_val=1,
                                  max_val=3)
    # Power spectral index
    n = FloatListField(label=mark_safe("n<sub>s</sub> "),
                          initial='0.967',
                          min_val=-4,
                          max_val=3)

    # Mass variance on a scale of 8Mpc
    sigma_8 = FloatListField(label=mark_safe("&#963<sub>8</sub>"),
                                initial='0.81',
                                min_val=0.1)

    # Hubble Constant
    H0 = FloatListField(label=mark_safe("H<sub>0</sub>"),
                               initial='70.4',
                               min_val=10,
                               max_val=500.0)

    omegab = FloatListField(label=mark_safe("&#937<sub>b</sub>"),
                                       initial='0.0455',
                                       min_val=0.005,
                                       max_val=0.65)

    omegac = FloatListField(label=mark_safe("&#937<sub>c</sub>"),
                                       initial='0.226',
                                       min_val=0.02,
                                       max_val=2.0)

    omegav = FloatListField(label=mark_safe("&#937<sub>&#923</sub>"),
                                       initial='0.728',
                                       min_val=0,
                                       max_val=1.6)

#    cp_w_lam = FloatListField(label="w",
#                                       initial='-1.0')

#    cp_omegan = FloatListField(label=mark_safe("&#937<sub>v</sub>"),
#                                       initial='0.0',
#                                       min_val=0,
#                                       max_val=0.7)

    def clean(self):
        """
        Clean the form for things that need to be cross-referenced between fields.
        
        Most of the tests are in try: except: statements because if a field's individual clean method
        finds an error, then it will be None and probably raise an exception here which is not handled.
        With this method, at least this function will finish, and the individual error will be reported
        """
        cleaned_data = super(HMFInput, self).clean()

        #========= Check At Least One Approach Is Chosen ======#
#         approach = cleaned_data.get("approach")
#         alternate_model = cleaned_data.get("alternate_model")
#
#         if not approach and not alternate_model:
#             raise forms.ValidationError("You must either choose an approach or enter a custom fitting function")

        #========= Check That There are Enough Labels =========#
#         labels = cleaned_data.get("cp_label")
#         try:
#             cosmo_quantities = []
#             for key, val in cleaned_data.iteritems():
#                 if key.startswith('cp_'):
#                     cosmo_quantities.append(key)
#
#             lengths = []
#             for quantity in cosmo_quantities:
#                 lengths = lengths + [len(cleaned_data.get(quantity))]
#
#             if len(labels) != max(lengths):
#                 raise forms.ValidationError("There must be %s labels separated by commas" % max(lengths))
#         except:
#             pass
        #========== Check That k limits are right ==============#
#         extrapolate = cleaned_data.get("extrapolate")
#         try:
#             if extrapolate:
        min_k = cleaned_data.get("lnk_min")
        max_k = cleaned_data.get("lnk_max")
        dlnk = cleaned_data.get("dlnk")

        if np.max(min_k) > np.min(max_k):
            raise forms.ValidationError("All min(k) must be less than max(k)")

        if dlnk > np.min(max_k) - np.max(min_k):
            raise forms.ValidationError("Wavenumber step-size must be less than the k-range.")
        #=========== Check that Mass limits are right ==========#
        try:
            if not self.minm:
                minm = cleaned_data.get("M_min")
                maxm = cleaned_data.get("M_max")
                mstep = cleaned_data.get("dlog10m")
                if maxm < minm:
                    raise forms.ValidationError("min(M) must be less than max(M)")
                if mstep > maxm - minm:
                    raise forms.ValidationError("Mass bin width must be less than the range of Mass")
        except:
            pass

        #=========== Here we check roughly how long we expect calculations to take and make the user adjust if too long
        #        For 50 M's:
        #----------------------------------------------------
        # setup             :  0.903198504448
        # set_transfer_cosmo:  1.05522716045
        # set_kbounds       :  0.0717063983281
        # set_WDM           :  0.071452331543
        # set_z             :  0.00227285861969
        # Get MF            :  6.63149356842e-05
        #----------------------------------------------------
#         initial_setup_time = 0.9
#         try:
#             set_transfer_time = max((len(cleaned_data.get("cp_H0")) , len(cleaned_data.get("cp_omegab")), len(cleaned_data.get("cp_omegac")),
#                                  len(cleaned_data.get("cp_omegav")))) * 1.055
#
#             set_kbounds_time = max((len(cleaned_data.get("k_ends_at")), len(cleaned_data.get("k_begins_at")))) * len(cleaned_data.get("cp_n")) * \
#                             len(cleaned_data.get("cp_sigma_8")) * 0.072
#
#             set_WDM_time = len(cleaned_data.get("WDM")) * 0.072
#
#             set_z_time = len(cleaned_data.get("z")) * 0.003
#
#             get_mf_time = len(cleaned_data.get("approach")) * len(cleaned_data.get("overdensity")) * len(cleaned_data.get("cp_delta_c")) * 6.64 * 10 ** -5
#
#             total_time = initial_setup_time + set_transfer_time + set_kbounds_time + set_WDM_time + set_z_time + get_mf_time
#
#             if total_time > 10.0:
#                 raise forms.ValidationError("Your choice of data will take too long to calculate, please reduce the amounts of combinations")
#
#         except:
#             pass
        return cleaned_data



class PlotChoice(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super (PlotChoice, self).__init__(*args, **kwargs)
        # Add in extra plot choices if they are required by the form in the session.
        # There have been a lot of errors coming through here -- not really sure why,
        # probably something to do with a session dying or something. I'm just wrapping
        # it in a try-except block for now so that people don't get errors at least.

        objects = request.session["objects"]

        plot_choices = [("dndm", "dn/dm"),
                        ("dndlnm", "dn/dln(m)"),
                        ("dndlog10m", "dn/dlog10(m)"),
                        ("fsigma", "f(sigma)"),
                        ("sigma", "Mass Variance"),
                        ("lnsigma", "ln(1/sigma)"),
                        ("n_eff", "Effective Spectral Index"),
                        ("ngtm", "n(>m)"),
                        ("nltm", "n(<m)"),
                        ("mltm", "m(<m)"),
                        ("mgtm", "m(>m)"),
                        ("transfer", "Transfer Function"),
                        ("power", "Power Spectrum"),
                        ("delta_k", "Dimensionless Power Spectrum") ]

        if len(objects) > 1:
            plot_choices += [("comparison_dndm", "Comparison of Mass Functions"),
                            ("comparison_fsigma", "Comparison of Fitting Functions")]

        self.fields["plot_choice"] = forms.ChoiceField(label="View plot of",
                                                       choices=plot_choices,
                                                       initial='dndm')

        self.helper = FormHelper()
        self.helper.form_id = 'plotchoiceform'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.help_text_inline = True

        self.helper.layout = Layout(Div('plot_choice', 'download_choice', css_class="span3"))

    download_choices = [("pdf-current", "PDF of Current Plot"),
                        # ("pdf-all", "PDF's of All Plots"),
                        ("ASCII", "All ASCII data"),
                        ("parameters", "List of parameter values")]

    download_choice = forms.ChoiceField(label=mark_safe('<a href="../dndm.pdf" id="plot_download">Download </a>'),
                                choices=download_choices,
                                initial='pdf-current')




class ContactForm(forms.Form):

    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        super(ContactForm, self).__init__(*args, **kwargs)
