#Analytics settings
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-41647354-1'

#My email
ADMINS = (
     ('Steven', 'steven.jeanette.m@gmail.com'),
)

#===============================================================================
# EMAIL SETUP
#===============================================================================
EMAIL_USE_TLS = True  #Whether to use a TLS (secure) connection when talking to the SMTP server.
EMAIL_HOST = 'smtp.ivec.com'
#EMAIL_HOST_USER = 'hmf@hmf-test.icrar.org'
#EMAIL_HOST_PASSWORD = 'Password1'
EMAIL_PORT = 25  #Port to use for the SMTP server defined in EMAIL_HOST.

SERVER_EMAIL = 'hmf@django.com'  #The email address that error messages come from, such as those sent to ADMINS and MANAGERS.
DEFAULT_FROM_EMAIL = SERVER_EMAIL

MANAGERS = ADMINS

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')#4yu%#tt5@cp4ot0!fntm!1fcapxe8pnb%9v9p7%w8c5=+aa1'
