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
from crispy_forms.layout import Layout, Submit, Div, HTML
from crispy_forms.bootstrap  import TabHolder, Tab, FormActions
import os
from django.conf import settings
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
    def __init__(self, labels=None, add=True, *args, **kwargs):
        self.old_labels = labels
        self.add = add
        super (HMFInput, self).__init__(*args, **kwargs)

        self.fields['label'] = forms.CharField(label="Label",
                                initial="PLANCK-SMT",
                                help_text="A base label for this calculation",
                                max_length=25)

#         if add == 'create':
#             # Then we wnat to display min_M and max_M
#             self.fields['Mmin'] = forms.FloatField(label="",
#                                                     initial=10.0,
#                                                     help_text=mark_safe("Units of log<sub>10</sub>(M<sub>&#9737</sub>)"),
#                                                     min_value=3.0,
#                                                     max_value=18.0)
#             self.fields['Mmax'] = forms.FloatField(label="",
#                                                     initial=15.0,
#                                                     help_text="",
#                                                     min_value=3.0,
#                                                     max_value=18.0)
#             self.fields['dlog10m'] = forms.FloatField(label="",
#                                                      initial=0.05,
#                                                      help_text="",
#                                                      min_value=0.00001,
#                                                      max_value=15.0)

        self.helper = FormHelper()
        # self.helper.form_id = 'input_form'
        self.helper.form_class = 'form-horizontal'

        self.helper.form_tag = False  # don't render form DOM element
#         self.helper.render_unmentioned_fields = True  # render all fields
        self.helper.help_text_inline = True
        self.helper.label_class = "col-md-3 control-label"
        self.helper.field_class = "col-md-8"

        k_html = HTML(mark_safe("""
<div class="form-group">
    <label for="id_lnk_min" class="col-md-3 control-label">Min|Max|&#916 (lnk)</label>
    <div class="col-md-9">
        <div class="form-group row">
            <div class="col-md-4">
                <input class="form-control" id="id_lnk_min" name="lnk_min" type="text" value="-15" />
                
            </div>
            <div class="col-md-4">
                <input class="form-control" id="id_lnk_max" name="lnk_max" type="text" value="15" />
            </div>
            <div class="col-md-4">
                <input class="form-control" id="id_dlnk" name="dlnk" type="text" value="0.05" />
            </div>
        </div>
    </div>    
</div>
"""))
        m_html = HTML(mark_safe("""
<div class="form-group">
    <label for="id_lnk_min" class="col-md-3 control-label">Min|Max|&#916 (log<sub>10</sub>M<sub>&#9737</sub>)</label>
    <div class="col-md-9">
        <div class="form-group row">
            <div class="col-md-4">
                <input class="form-control" id="id_Mmin" name="Mmin" type="text" value="10" />
            </div>
            <div class="col-md-4">
                <input class="form-control" id="id_Mmax" name="Mmax" type="text" value="15" />
            </div>
            <div class="col-md-4">
                <input class="form-control" id="id_dlog10m" name="dlog10m" type="text" value="0.05" />
            </div>
        </div>
    </div>    
</div>
"""))
#         if add == 'create':
#             d = Div('wdm_mass', k_html, m_html, 'cut_fit', css_class='col-md-6')
#         else:
        d = Div('wdm_mass', k_html, 'cut_fit', css_class='col-md-6')

        self.helper.layout = Layout("label",
                                    TabHolder(
                                              Tab('Run Parameters',
                                                      Div(
                                                          Div('z',
                                                              'delta_h',
                                                              'delta_wrt',
                                                              'mf_fit',
                                                              css_class='col-md-6'
                                                              ),
                                                           d)
                                                      ),
                                              Tab('Cosmological Parameters',
                                                      Div(
                                                          Div('transfer_file',
                                                              'transfer_file_upload',
                                                              'transfer_fit',
                                                              'delta_c',
                                                              'n',
                                                              css_class='col-md-6'
                                                              ),
                                                          Div('sigma_8',
                                                              'H0',
                                                              'omegab',
                                                              'omegac',
                                                              'omegav',
                                                              css_class='col-md-6'
                                                              )
                                                          )
                                                      )
                                                  ),
                                        FormActions(Submit('submit', 'Calculate!', css_class='btn-large'))
                                        )
#         self.helper.form_action = ''
    ###########################################################
    # MAIN RUN PARAMETERS
    ###########################################################
    def clean_label(self):
        label = self.cleaned_data['label']
        label = label.replace("_", "-")
        if self.add:
            if self.old_labels:
                if label in self.old_labels:
                    raise forms.ValidationError("Label must be unique")
        return label

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
                                       required=True)


    transfer_choices = [(os.path.join(settings.ROOT_DIR, 'HMFcalc/transfers/PLANCK_transfer.dat'), 'PLANCK'),
                        (os.path.join(settings.ROOT_DIR, 'HMFcalc/transfers/WMAP9_transfer.dat'), 'WMAP9'),
                        (os.path.join(settings.ROOT_DIR, "HMFcalc/transfers/WMAP7_transfer.dat"), "WMAP7"),
                        (os.path.join(settings.ROOT_DIR, "HMFcalc/transfers/WMAP5_transfer.dat"), "WMAP5"),
                        (os.path.join(settings.ROOT_DIR, 'HMFcalc/transfers/WMAP3_transfer.dat'), 'WMAP3'),
                        (os.path.join(settings.ROOT_DIR, 'HMFcalc/transfers/WMAP1_transfer.dat'), 'WMAP1'),
                        (os.path.join(settings.ROOT_DIR, "HMFcalc/transfers/Millennium_transfer.dat"), "Millennium (and WALLABY)"),
                        (os.path.join(settings.ROOT_DIR, "HMFcalc/transfers/GiggleZ_transfer.dat"), "GiggleZ"),
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
        min_k = cleaned_data.get("lnk_min")
        max_k = cleaned_data.get("lnk_max")
        dlnk = cleaned_data.get("dlnk")

        if np.max(min_k) > np.min(max_k):
            raise forms.ValidationError("All min(k) must be less than max(k)")

        if dlnk > np.min(max_k) - np.max(min_k):
            raise forms.ValidationError("Wavenumber step-size must be less than the k-range.")
        #=========== Check that Mass limits are right ==========#
#         try:
#             if not self.minm:
#                 minm = cleaned_data.get("M_min")
#                 maxm = cleaned_data.get("M_max")
#                 mstep = cleaned_data.get("dlog10m")
#                 if maxm < minm:
#                     raise forms.ValidationError("min(M) must be less than max(M)")
#                 if mstep > maxm - minm:
#                     raise forms.ValidationError("Mass bin width must be less than the range of Mass")
#         except:
#             pass

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


class Axes(forms.Form):

    m_choices = [("M", "log(M)"),
                 ("sigma", mark_safe("&#963 (mass variance)")),
                 ("_dlnsdlnm", mark_safe("dln(&#963)/dln(M)")),
                 ("nu", mark_safe("Peak height, &#957")),
                 ("lnsigma", mark_safe("ln(1/&#963)")),
                 ("n_eff", "Effective Spectral Index"),
                 ("fsigma", mark_safe("f(&#963)")),
                 ("dndm", "dn/dm"),
                 ("dndlnm", "dn/dln(m)"),
                 ("dndlog10m", "dn/dlog10(m)"),
                 ("ngtm", "n(>m)"),
                 ("rho_ltm", mark_safe("&#961(&#60m)")),
                 ("rho_gtm", mark_safe("&#961(>m)")),
                 ("how_big", "L(n=1)")]

    k_choices = [("lnk", "ln(k)"),
                 ("transfer", "T(k)"),
                 ("power", "P(k)"),
                 ("delta_k", mark_safe("&#916(k)"))]

    choices = m_choices + k_choices

    def __init__(self, *args, **kwargs):
        super(Axes, self).__init__(*args, **kwargs)
        self.fields["x"] = forms.ChoiceField(label="x axis",
                                             choices=self.choices,
                                             initial="M")

        self.fields["y"] = forms.ChoiceField(label="y axis",
                                             choices=self.choices,
                                             initial="dndm")

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.help_text_inline = True
        helper.label_class = "col-md-3 control-label"
        helper.field_class = "col-md-8"
        helper.layout = Layout('x', 'y',
                               FormActions(Submit('submit', 'Submit', css_class='btn-large')))
        return helper


class Download(forms.Form):

    def __init__(self, *args, **kwargs):
        super(Download, self).__init__(*args, **kwargs)

        self.fields['m'] = forms.MultipleChoiceField(label="mass vector quantities",
                                                     choices=Axes.m_choices,
                                                     widget=forms.CheckboxSelectMultiple,
                                                     initial=["M", "dndm"])

        self.fields['k'] = forms.MultipleChoiceField(label="k vector quantities",
                                                     choices=Axes.k_choices,
                                                     widget=forms.CheckboxSelectMultiple,
                                                     initial=["lnk", "power"])

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.help_text_inline = True
        helper.label_class = "col-md-3 control-label"
        helper.field_class = "col-md-8"
        helper.layout = Layout(Div('m', css_class="col-md-6"), Div('k', css_class="col-md-6"),
                               FormActions(Submit('submit', 'Download', css_class='btn-large')))
        return helper

class ContactForm(forms.Form):

    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        super(ContactForm, self).__init__(*args, **kwargs)
