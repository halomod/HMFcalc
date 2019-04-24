from collections import OrderedDict

from crispy_forms.bootstrap import Tab
from crispy_forms.layout import Div, Field
from django import forms
from django.utils.safestring import mark_safe
import re


class RangeSlider(forms.TextInput):
    def __init__(self, minimum, maximum, step, elem_name, initial=None, *args,**kwargs):
        widget = super(RangeSlider,self).__init__(*args,**kwargs)
        self.minimum = str(minimum)
        self.maximum = str(maximum)
        self.step = str(step)
        self.elem_name = str(elem_name)

        self.initial = initial

    @property
    def initial_min(self):
        if self.initial is None:
            return self.minimum
        else:
            if type(self.initial) is str:
                return self.initial.split(" - ")[0]
            else:
                return self.initial[0]

    @property
    def initial_max(self):
        if self.initial is None:
            return self.maximum
        else:
            if type(self.initial) is str:
                return self.initial.split(" - ")[1]
            else:
                return self.initial[1]

    def render(self, name, value, attrs=None, renderer=None):
        s = super(RangeSlider, self).render(name, value, attrs)
        self.elem_id = re.findall(r'id_([A-Za-z0-9_\./\\-]*)"', s)[0]
        html = """<div id="slider-range-""" + self.elem_id + """"></div>
        <script>
        $('#id_""" + self.elem_id + """').attr("readonly", true)
        $( "#slider-range-""" + self.elem_id + """" ).slider({
        range: true,
        min: """ + self.minimum + """,
        max: """ + self.maximum + """,
        step: """ + self.step + """,
        values: [ """ + self.initial_min + """,""" + self.initial_max + """ ],
        slide: function( event, ui ) {
          $( "#id_""" + self.elem_id + """" ).val(" """ + self.elem_name + """ "+ ui.values[ 0 ] + " - " + ui.values[ 1 ] );
        }
        });
        $( "#id_""" + self.elem_id + """" ).val(" """ + self.elem_name + """ "+ $( "#slider-range-""" + self.elem_id + """" ).slider( "values", 0 ) +
        " - " + $( "#slider-range-""" + self.elem_id + """" ).slider( "values", 1 ) );
        </script>
        """

        return mark_safe(s + html)

# --------- Custom Form Field for Comma-Separated Input -----
class FloatListField(forms.CharField):
    """
    Defines a form field that accepts comma-separated real values and returns a list of floats.
    """

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_val, self.max_val = min_value, max_value
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
                        raise forms.ValidationError(
                            "Must be greater than " + str(self.min_val) + " (" + str(number) + ")")
                if self.max_val is not None:
                    if number > self.max_val:
                        raise forms.ValidationError(
                            "Must be smaller than " + str(self.max_val) + " (" + str(number) + ")")

        return final_list


class RangeSliderField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', '')
        self.minimum = kwargs.pop('minimum', 0)
        self.maximum = kwargs.pop('maximum', 100)
        self.step = kwargs.pop('step', 1)
        self.initial = kwargs.pop("initial", None)

        kwargs['widget'] = RangeSlider(self.minimum, self.maximum, self.step, self.name, initial=self.initial)

        if 'label' not in kwargs.keys():
            kwargs['label'] = False

        super(RangeSliderField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super().clean(value)

        items = value.split(" - ")
        return [float(i) for i in items]


class CompositeForm(forms.Form):
    """
    Helper class to handle form composition.
    Usage::
      class ProfileForm(CompositeForm):
          form_list = [ProfileAddressForm, ProfileBirthDayForm]

    Ripped from https://github.com/t0ster/django-composite-form
    """
    form_list = None  # Form classes

    def __init__(self, data=None, files=None, field_order=None, *args, **kwargs):
        super().__init__(data, files, field_order=None, *args, **kwargs)

        self._form_instances = OrderedDict()  # Form instances
        for form in self.form_list:
            kw = kwargs.copy()
            self._form_instances[form] = form(data, files, *args, **kw)

        for form in self.forms:
            self.fields.update({f"{name}": val for name, val in form.fields.items()})

        self.order_fields(self.field_order if field_order is None else field_order)

        for form in self.forms:
            self.initial.update(form.initial)

    @property
    def forms(self):
        """
        Returns list of form instances
        """
        # Preserving forms ordering
        return [self._form_instances[form_class] for form_class in self.form_list]

    def get_form(self, form_class):
        """
        Returns form instance by its class
        ``form_class``: form class from ``forms_list``
        """
        return self._form_instances[form_class]

    # def non_field_errors(self):
    #     _errors = forms.utils.ErrorList()
    #     for form in self.forms:
    #         _errors.extend(form.non_field_errors())
    #     return _errors

    def full_clean(self):
        super().full_clean()

        if not self.is_bound:
            return

        for form in self.forms:
            form.full_clean()
            self.cleaned_data.update(form.cleaned_data)
            self._errors.update(form._errors)


class HMFModelForm(forms.Form):
    label = None
    kind = None
    choices = None
    _initial = None
    multi = False

    module = None

    ignore_fields = []
    add_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.label is None:
            self.label = self.__class__.__name__.split("Form")[0] + " Model"

        if self.kind is None:
            self.kind = self.__class__.__name__.split("Form")[0].lower()

        # Fill the fields
        if not self.multi:
            self.fields[f'{self.kind}_model'] = forms.ChoiceField(
                label=self.label,
                choices=self.choices,
                initial=self._initial,
                required=True,
            )
        else:
            self.fields[f'{self.kind}_model'] = forms.MultipleChoiceField(
                label=self.label,
                choices=self.choices,
                initial=[self._initial],
                required=True,
            )

        # Add all the possible parameters for this model
        for choice in self.choices:
            # Allow a "None" class
            if choice[0] == "None":
                continue

            cls = getattr(self.module, choice[0])

            if hasattr(cls, "_defaults"):
                for key, val in cls._defaults.items():
                    name = f"{self.kind}_{key}"

                    if name not in self.fields and key not in self.ignore_fields:
                        self.fields[name] = forms.FloatField(
                            label=key,
                            initial=str(val),
                            required=False
                        )
                        self.fields[name].belongs_to = self.kind
                        self.fields[name].show_for = [choice[0]]

                    elif name in self.fields and key not in self.ignore_fields:
                        self.fields[name].show_for.append(choice[0])

        for fieldname, field in self.add_fields.items():
            name = f"{self.kind}_{fieldname}"
            self.fields[name] = field
            self.fields[name].belongs_to = self.kind

        param_div = Div()
        for name, field in self.fields.items():
            if name == f"{self.kind}_model":
                continue

            if hasattr(field, "show_for"):
                param_div.append(
                    Div(
                        name,
                        css_class="col hmf_param" if hasattr(field, "show_for") else "col",
                        data_name=self.kind if hasattr(field, "show_for") else None,
                        data_models=" ".join(field.show_for) if hasattr(field, "show_for") else None)
                )
            else:
                param_div.append(
                    Div(name, css_class='col')
                )

        # Make layout a simple Tab with a model chooser and model parameters.
        self._layout = Tab(
            self.label,
            Div(
                Div(
                    Field(
                        f"{self.kind}_model",
                        css_class="hmf_model",
                        data_name=self.kind
                    ),
                    css_class='col',
                ),
                param_div,
                css_class='mt-4 row',
            )
        )


class HMFFramework(forms.Form):
    label = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.label is None:
            self.label = self.__class__.__name__

        self._layout = Tab(
            self.label,
            Div(
                *self.fields.keys(),
                css_class="mt-4 col"
            )
        )
