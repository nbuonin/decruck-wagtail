from django.conf import settings


def language_host_names(request):
    return {
        'EN_HOST': '{}://{}'.format(request.scheme, settings.EN_HOST),
        'FR_HOST': '{}://{}'.format(request.scheme, settings.FR_HOST),
    }


def ga_tracking_id(request):
    return {'GA_TRACKING_ID': getattr(settings, 'GA_TRACKING_ID', None)}


def captcha_site_key(request):
    return {'CAPTCHA_SITE_KEY': getattr(settings, 'CAPTCHA_SITE_KEY', None)}
