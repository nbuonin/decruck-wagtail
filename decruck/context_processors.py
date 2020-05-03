from django.conf import settings


def language_host_names(request):
    return {
        'EN_HOST': '{}://{}'.format(request.scheme, settings.EN_HOST),
        'FR_HOST': '{}://{}'.format(request.scheme, settings.FR_HOST),
    }
