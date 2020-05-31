from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's2(pm&w%$lg5vn3%oyig&md0gsx!lq1b))x(ug%_(8=fzz%oci'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EN_HOST = 'decruck.en:8000'
FR_HOST = 'decruck.fr:8000'

PAYPAL_TEST = True
PAYPAL_ACCT_EMAIL = 'info-facilitator@example.org'
ORDER_EMAIL_ADDR = 'order-test@example.org'

try:
    from .local import *
except ImportError:
    pass
