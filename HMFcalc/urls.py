from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path(
        r'favicon\.ico',
        RedirectView.as_view(url='http://hmfstatic.appspot.com/img/favicon.ico')
    ),
    path(
        '',
        views.home.as_view(),
        name='home'
    ),
    path(
        'hmfcalc/create/',
        views.HMFInputCreate.as_view(),
        name='calculate'
    ),
    path(
        'hmfcalc/create/<label>/',
        views.HMFInputCreate.as_view(),
        name='calculate'
    ),
    path(
        'hmfcalc/edit/<label>/',
        views.HMFInputEdit.as_view(),
        name='calculate'
    ),
    path(
        'hmfcalc/delete/<label>/',
        views.delete_plot,
        name='delete'
    ),
    path(
        'hmfcalc/restart/',
        views.complete_reset,
        name='restart'
    ),
    path(
        'help/',
        views.help.as_view(),
        name='help'
    ),
    # path(
    #     'hmf_resources/',
    #     views.resources.as_view(),
    #     name='resources'
    # ),
    # path(
    #     'hmf_acknowledgments/',
    #     views.acknowledgments.as_view(),
    #     name='acknowledgments'
    # ),
    path(
        'hmfcalc/',
        views.ViewPlots.as_view(),
        name='image-page'
    ),
    path(
        'hmfcalc/<plottype>.<filetype>',
        views.plots,
        name='images'
    ),
    path(
        'hmfcalc/download/allData.zip',
        views.data_output,
        name='data-output'
    ),
    path(
        'hmfcalc/download/parameters.txt',
        views.header_txt,
        name='header-txt'
    ),
    path(
        'emailme/',
        views.ContactFormView.as_view(),
        name='contact-email'
    ),
    path(
        'email-sent/',
        views.EmailSuccess.as_view(),
        name='email-success'
    ),
    path(
        'hmfcalc/download/halogen.zip',
        views.halogen,
        name='halogen-output'
    ),
]