from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    path("", include("HMFcalc.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
