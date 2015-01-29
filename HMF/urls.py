from django.conf.urls import patterns, include, url
from HMFcalc import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from active_menu import menu_item

# Tab heirarchy
home = menu_item('home')
acknowledgments = menu_item('acknowledgments')  # if has a parent, use parent=
resources = menu_item('resources')
contact = menu_item('contact-info')
calculator = menu_item("hmf-calculator")
help = menu_item("help")
email = menu_item("contact-email", parent=contact)

# Patterns
urlpatterns = patterns('',
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='http://hmfstatic.appspot.com/img/favicon.ico')),
    url(r'^$', \
        views.Home.as_view(),
        name='home'),
    url(r'^hmf-calculator/$',
        views.Calculator.as_view(),
        name="hmf-calculator"),
    url(r'^hmf-calculator/reload/$',
        "HMFcalc.views.redraw_plot",
        name="reload"),
    url(r'^hmf-calculator/(?P<mode>add|edit)/(?P<label>[^/]+)/$',
        views.Input.as_view(),
        name="input"),
    url(r'^hmf-calculator/axes/$',
        views.Axes.as_view(),
        name="axes"),
    url(r'^hmf-calculator/axes/y-selector/$',
        'HMFcalc.views.y_selector',
        name='y-selector'),
    url(r'^hmf-calculator/clear/$',
        'HMFcalc.views.clear_all',
        name="clear-all"),
    url(r'^hmf-calculator/del/$',
        'HMFcalc.views.remove_single_entry',
        name="del"),
    url(r'^hmf-calculator/download/$',
        views.Download.as_view(),
        name="download"),
    url(r'^hmf-calculator/data/$',
        'HMFcalc.views.downloader',
        name="downloader"),
    url(r'^hmf-calculator/switch_compare/$',
        'HMFcalc.views.switch_compare',
        name="switch-compare"),
    # ---- INFO PAGES --------
    url(r'^help/$',
        views.Help.as_view(),
        name='help'),
#    url(r'^hmf_parameter_discussion/',
#        views.param_discuss.as_view(),
#        name='param-discuss'),
    url(r'^resources/',
        views.Resources.as_view(),
        name='resources'),
    url(r'^acknowledgments/',
        views.Acknowledgments.as_view(),
        name='acknowledgments'),
    url(r'^hmf-calculator/compare_to/$',
        'HMFcalc.views.set_compare_model',
        name="compare_to"),
#     url(r'^hmf_finder/hmf_image_page/$',
#         views.ViewPlots.as_view(),
#         name='image-page'),
#-------- UTILITIES
#     url(r'^hmf_finder/(?P<plottype>\w+).(?P<filetype>\w{3})$',
#         'HMFcalc.views.plots',
#         name='images'),
#     url(r'^hmf_finder/hmf_image_page/plots.zip$',
#         'HMFcalc.views.hmf_all_plots',
#         name='all-plots'),
#     url(r'^hmf_finder/hmf_image_page/allData.zip$',
#         'HMFcalc.views.data_output',
#         name='data-output'),
#     url(r'^hmf_finder/hmf_image_page/parameters.txt$',
#         'HMFcalc.views.header_txt',
#         name='header-txt'),

    url(r'^contact_info/$',
        views.Contact.as_view(),
        name='contact-info'),
    url(r'^contact_info/emailme/$',
        views.ContactFormView.as_view(),
        name='contact-email'),
    url(r'^email-sent/$',
        views.EmailSuccess.as_view(),
        name='email-success'),
    url(r'^downloads/(?P<name>\w+).(?P<type>\w+)$',
        'HMFcalc.views.get_code',
        name='get-code')
    )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()


