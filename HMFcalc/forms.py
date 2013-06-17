'''
Created on May 3, 2012

@author: smurray
'''

#from django import forms
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
                        raise forms.ValidationError("z must be greater than " + str(self.min_val) + " (" + str(number) + ")")
                if self.max_val is not None:
                    if number > self.max_val:
                        raise forms.ValidationError("z must be smaller than " + str(self.max_val) + " (" + str(number) + ")")

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
        super (HMFInput, self).__init__(*args, **kwargs)

        if add == 'create':
            # Then we wnat to display min_M and max_M
                # Which values of the radius to use?
            self.fields['min_M'] = forms.FloatField(label="Minimum Mass",
                                                    initial=8.0,
                                                    help_text=mark_safe("Units of log<sub>10</sub>(M<sub>&#9737</sub>)"),
                                                    min_value=3.0,
                                                    max_value=18.0)
            self.fields['max_M'] = forms.FloatField(label="Maximum Mass",
                                                    initial=15.0,
                                                    help_text=mark_safe("Units of log<sub>10</sub>(M<sub>&#9737</sub>)"),
                                                    min_value=3.0,
                                                    max_value=18.0)
            self.fields['M_step'] = forms.FloatField(label="Mass Bin Width",
                                                     initial=0.05,
                                                     help_text="Logarithmic Bins",
                                                     min_value=0.00001,
                                                     max_value=15.0)

        self.helper = FormHelper()
        self.helper.form_id = 'input_form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.help_text_inline = True

        if add == 'create':
            # self.helper.add_input(Submit('submit', 'Calculate!'))
            self.helper.layout = Layout(
                                        TabHolder(
                                                  Tab('Run Parameters',
                                                      Div(
                                                          Div('z',
                                                              'overdensity',
                                                              'WDM',
                                                              'approach',
                                                              'alternate_model',
                                                              css_class='span4'
                                                              ),
                                                           Div('extrapolate',
                                                               'k_begins_at',
                                                               'k_ends_at',
                                                               'min_M',
                                                               'max_M',
                                                               'M_step',
                                                               css_class='span4'
                                                               )),
                                                      Div(
                                                          Fieldset('Optional Extra Plots',
                                                                   InlineCheckboxes('extra_plots'),
                                                                   ),
                                                          css_class='span12'

                                                          )
                                                      ),
                                                  Tab('Cosmological Parameters',
                                                      Div(
                                                          Div('co_transfer_file',
                                                              'co_transfer_file_upload',
                                                              'cp_label',
                                                              'cp_delta_c',
                                                              'cp_n',

                                                              css_class='span4'
                                                              ),
                                                          Div('cp_sigma_8',
                                                              'cp_H0',
                                                              'cp_omegab',
                                                              'cp_omegac',
                                                              'cp_omegav',
#                                                              'cp_w_lam',
#                                                              'cp_omegan',

                                                              css_class='span4'
                                                              )
                                                          )
                                                      )
                                                  ),
                                        FormActions(Submit('submit', 'Calculate!', css_class='btn btn-primary btn-large'))
                                        )
        else:
            self.helper.layout = Layout(
                                        TabHolder(
                                                  Tab('Run Parameters',
                                                      Div(
                                                          Div('z',
                                                              'overdensity',
                                                              'WDM',
                                                              'approach',
                                                              css_class='span4'
                                                              ),
                                                          Div('extrapolate',
                                                              'k_begins_at',
                                                              'k_ends_at',
                                                              'alternate_model',
                                                              css_class='span4'
                                                              )),
                                                      Div(
                                                          Fieldset('Optional Extra Plots',
                                                                   InlineCheckboxes('extra_plots'),
                                                                   ),
                                                          css_class='span12'

                                                          )
                                                      ),
                                                  Tab('Cosmological Parameters',
                                                      Div(
                                                          Div('co_transfer_file',
                                                              'co_transfer_file_upload',
                                                              'cp_label',
                                                              'cp_delta_c',
                                                              'cp_n',

                                                              css_class='span4'
                                                              ),
                                                          Div('cp_sigma_8',
                                                              'cp_H0',
                                                              'cp_omegab',
                                                              'cp_omegac',
                                                              'cp_omegav',
#                                                              'cp_w_lam',
#                                                              'cp_omegan',

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


    overdensity = FloatListField(label="Virial Overdensity",
                                 help_text="Comma-separated list",
                                 max_length=50,
                                 initial=178,
                                 min_val=10)

    # WDM particle masses (empty list if none)
    WDM = FloatListField(label="WDM Masses",
                         required=False,
                         help_text="Comma-separated list. In keV (eg. 0.05)",
                         max_length=50,
                         min_val=0.0001)


    # Mass Function fit
    approach_choices = [("PS", "Press-Schechter (1974)"),
                        ("ST", "Sheth-Tormen (2001)"),
                        ("Jenkins", "Jenkins (2001)"),
                        ("Reed03", "Reed (2003)"),
                        ("Warren", "Warren (2006)"),
                        ("Reed07", "Reed (2007)"),
                        ("Tinker", "Tinker (2008)"),
                        ("Crocce", "Crocce (2010)"),
                        ("Courtin", "Courtin (2010)"),
                        ("Bhattacharya", "Bhattacharya (2011)"),
                        ("Angulo", "Angulo (2012)"),
                        ("Angulo_Bound", "Angulo (Subhaloes) (2012)"),
                        ("Watson_FoF", "Watson (FoF Universal) (2012)"),
                        ("Watson", "Watson (Redshift Dependent) (2012)"),
                        ]

    approach = forms.MultipleChoiceField(label="Fitting Function",
                                         choices=approach_choices,
                                         initial=['ST'],
                                         required=False)

    alternate_model = forms.CharField(label=mark_safe('Custom Fitting Function'),
                                       help_text=mark_safe('Type a fitting function form (<a href="http://docs.scipy.org/doc/numpy/reference/routines.math.html">Python syntax</a>) in terms of mass variance (denoted by x). Eg. for Jenkins: 0.315*exp(-abs(log(1.0/x)+0.61)**3.8)'),
                                       required=False,
                                       widget=forms.Textarea(attrs={'cols':'40', 'rows':'3'}))

    transfer_choices = [('transfers/PLANCK_transfer.dat', 'PLANCK'),
                        ('transfers/WMAP9_transfer.dat', 'WMAP9'),
                        ("transfers/WMAP7_transfer.dat", "WMAP7"),
                        ("transfers/WMAP5_transfer.dat", "WMAP5"),
                        ('transfers/WMAP3_transfer.dat', 'WMAP3'),
                        ('transfers/WMAP1_transfer.dat', 'WMAP1'),
                        ("transfers/Millennium_transfer.dat", "Millennium (and WALLABY)"),
                        ("transfers/GiggleZ_transfer.dat", "GiggleZ"),
                        ("custom", "Custom")]

    co_transfer_file = forms.ChoiceField(label="Transfer Function",
                                choices=transfer_choices,
                                initial="transfers/WMAP7_transfer.dat")

    co_transfer_file_upload = forms.FileField(label="Upload Transfer Function",
                                              required=False,
                                              help_text="Custom file only used if Transfer Functions is 'Custom'")

    def clean_co_transfer_file_upload(self):
        thefile = self.cleaned_data['co_transfer_file_upload']
        if thefile is not None:
            try:
                np.genfromtxt(thefile)
            except:
                raise forms.ValidationError("Uploaded transfer file is of the wrong format")
#===================================================================
#    RUN PARAMETERS
#===================================================================
    # Extrapolation parameters.
    extrapolate = forms.BooleanField(label='Extrapolate bounds of k?', initial=True, required=False)
    k_ends_at = FloatListField(label="Maximum k",
                               initial=2000.0,
                               help_text="Highest Wavenumber Used, Comma-Separated Decimals",
                               min_val=0.1)

    k_begins_at = FloatListField(label="Minimum k",
                                 initial=0.00000001,
                                 help_text="Lowest Wavenumber Used",
                                 max_val=10,
                                 min_val=0.0)

#===================================================================
#    OPTIONAL PLOTS
#===================================================================
    optional_plots = [("get_ngtm", "N(>M)"),
                        ("get_mgtm", "M(>M)"),
                        ("get_nltm", "N(<M)"),
                        ("get_mltm", "M(<M)"),
                        ("get_L", 'Box Size for One Halo'),
                        ]

    extra_plots = forms.MultipleChoiceField(label="Optional Extra Plots",
                                            choices=optional_plots,
                                            initial=['get_ngtm'],
                                            required=False)

#===================================================================
#   COSMOLOGICAL PARAMETERS
#===================================================================
    cp_label = forms.CharField(label="Unique Labels",
                               initial='WMAP7',
                               help_text="One unique identifier for each cosmology, separated by commas")

    def clean_cp_label(self):
        labels = self.cleaned_data['cp_label']
        labels = labels.split(',')
        for i, label in enumerate(labels):
            lab = label.strip()
            lab = lab.replace(" ", "_")
            labels[i] = lab
        return labels

    # Critical Overdensity corresponding to spherical collapse
    cp_delta_c = FloatListField(label=mark_safe("&#948<sub>c</sub>"),
                                  initial='1.686',
                                  min_val=1,
                                  max_val=3)
    # Power spectral index
    cp_n = FloatListField(label=mark_safe("n<sub>s</sub> "),
                          initial='0.967',
                          min_val= -4,
                          max_val=3)

    # Mass variance on a scale of 8Mpc
    cp_sigma_8 = FloatListField(label=mark_safe("&#963<sub>8</sub>"),
                                initial='0.81',
                                min_val=0.1)

    # Hubble Constant
    cp_H0 = FloatListField(label=mark_safe("H<sub>0</sub>"),
                               initial='70.4',
                               min_val=10,
                               max_val=500.0)

    cp_omegab = FloatListField(label=mark_safe("&#937<sub>b</sub>"),
                                       initial='0.0455',
                                       min_val=0.005,
                                       max_val=0.65)

    cp_omegac = FloatListField(label=mark_safe("&#937<sub>c</sub>"),
                                       initial='0.226',
                                       min_val=0.02,
                                       max_val=2.0)

    cp_omegav = FloatListField(label=mark_safe("&#937<sub>&#923</sub>"),
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
        cleaned_data = super(HMFInput, self).clean()

        #========= Check At Least One Approach Is Chosen ======#
        approach = cleaned_data.get("approach")
        alternate_model = cleaned_data.get("alternate_model")

        if not approach and not alternate_model:
            raise forms.ValidationError("You must either choose an approach or enter a custom fitting function")

        #========= Check That There are Enough Labels =========#
        labels = cleaned_data.get("cp_label")
        cosmo_quantities = []
        for key, val in cleaned_data.iteritems():
            if key.startswith('cp_'):
                cosmo_quantities.append(key)

        lengths = []
        for quantity in cosmo_quantities:
            lengths = lengths + [len(cleaned_data.get(quantity))]

        if len(labels) != max(lengths):
            raise forms.ValidationError("There must be %s labels separated by commas" % max(lengths))

        #========== Check That k limits are right ==============#
        extrapolate = cleaned_data.get("extrapolate")
        if extrapolate:
            min_k = cleaned_data.get("k_begins_at")
            max_k = cleaned_data.get("k_ends_at")
            num_k_bounds = np.max([len(min_k), len(max_k)])
            for i in range(num_k_bounds - 1):
                mink = min_k[np.min([len(min_k) - 1, i])]
                maxk = max_k[np.min([len(max_k) - 1, i])]
                if maxk < mink:
                    raise forms.ValidationError("All min(k) must be less than max(k)")

        #=========== Check that Mass limits are right ==========#
        if not self.minm:
            minm = cleaned_data.get("min_M")
            maxm = cleaned_data.get("max_M")
            mstep = cleaned_data.get("M_step")
            if maxm < minm:
                raise forms.ValidationError("min(M) must be less than max(M)")
            if mstep > maxm - minm:
                raise forms.ValidationError("Mass bin width must be less than the range of Mass")

        #=========== Here we check roughly how long we expect calculations to take and make the user adjust if too long
        #        For 50 M's:
        #----------------------------------------------------
        #setup             :  0.903198504448
        #set_transfer_cosmo:  1.05522716045
        #set_kbounds       :  0.0717063983281
        #set_WDM           :  0.071452331543
        #set_z             :  0.00227285861969
        #Get MF            :  6.63149356842e-05
        #----------------------------------------------------
        initial_setup_time = 0.9
        set_transfer_time = max((len(cleaned_data.get("cp_H0")) , len(cleaned_data.get("cp_omegab")), len(cleaned_data.get("cp_omegac")),
                                 len(cleaned_data.get("cp_omegav")))) * 1.055

        set_kbounds_time = max((len(cleaned_data.get("k_ends_at")), len(cleaned_data.get("k_begins_at")))) * len(cleaned_data.get("cp_n")) * \
                            len(cleaned_data.get("cp_sigma_8")) * 0.072

        set_WDM_time = len(cleaned_data.get("WDM")) * 0.072

        set_z_time = len(cleaned_data.get("z")) * 0.003

        get_mf_time = len(cleaned_data.get("approach")) * len(cleaned_data.get("overdensity")) * len(cleaned_data.get("cp_delta_c")) * 6.64 * 10 ** -5

        total_time = initial_setup_time + set_transfer_time + set_kbounds_time + set_WDM_time + set_z_time + get_mf_time

        if total_time > 10.0:
            raise forms.ValidationError("Your choice of data will take too long to calculate, please reduce the amounts of combinations")
        return cleaned_data



class PlotChoice(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super (PlotChoice, self).__init__(*args, **kwargs)
        # Add in extra plot choices if they are required by the form in the session.
        session_plots = request.session['extra_plots']
        extra_plots = []
        if 'get_ngtm' in session_plots:
            extra_plots.append(("ngtm", "N(>M)"))
        if 'get_nltm' in session_plots:
            extra_plots.append(("nltm", "N(<M)"))
        if "get_mgtm" in session_plots:
            extra_plots.append(("Mgtm", "Mass(>M)"))
        if "get_mltm" in session_plots:
            extra_plots.append(("Mltm", "Mass(<M)"))
        if "get_L" in session_plots:
            extra_plots.append(("L", "Box Size for One Halo"))

        plot_choices = [("hmf", "Mass Function"),
                        ("f", "f(sigma)"),
                        ("sigma", "Mass Variance"),
                        ("lnsigma", "ln(1/sigma)"),
                        ("n_eff", "Effective Spectral Index"),
                        ("comparison_hmf", "Comparison of Mass Functions"),
                        ("comparison_f", "Comparison of Fitting Functions"),
                        ("mhmf", "Mass by Mass Function"),
                        ("power_spec", "Power Spectrum")] + extra_plots

        self.fields["plot_choice"] = forms.ChoiceField(label="View plot of",
                                        choices=plot_choices,
                                        initial='hmf')

        self.helper = FormHelper()
        self.helper.form_id = 'plotchoiceform'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.help_text_inline = True

        self.helper.layout = Layout(Div('plot_choice', 'download_choice', css_class="span3"))

    download_choices = [("pdf-current", "PDF of Current Plot"),
                    ("pdf-all", "PDF's of All Plots"),
                    ("ASCII-mass", "ASCII table of all functions of mass"),
                    ("ASCII-k", "ASCII table of all functions of wavenumber"),
                    ("parameters", "List of parameter values")]

    download_choice = forms.ChoiceField(label=mark_safe('<a href="../hmf.pdf" id="plot_download">Download </a>'),
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
