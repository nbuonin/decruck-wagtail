import re
from urllib.parse import unquote

from django import template
from django.utils.translation import activate, get_language
from six import iteritems


try:
    from django.urls import resolve
except ImportError:
    from django.core.urlresolvers import resolve


try:
    from wagtail.core.models import Page
    from wagtail.core.templatetags.wagtailcore_tags import pageurl
except ImportError:
    from wagtail.wagtailcore.models import Page
    from wagtail.wagtailcore.templatetags.wagtailcore_tags import pageurl


register = template.Library()


# This is an override of Wagtail Model translate's change_lang tag. It
# addresses the pages that use the routable page mixin
@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, page=None, *args, **kwargs):
    current_language = get_language()

    if 'request' in context and lang and current_language:
        request = context['request']
        match = resolve(unquote(request.path, errors='strict'))
        non_prefixed_path = re.sub(current_language + '/', '', request.path, count=1)

        # means that is an wagtail page object
        if match.url_name == 'wagtail_serve':
            activate(lang)
            try:
                translated_url = page.url
            except AttributeError:
                activate(current_language)
                return ''

            req_url = request.path.split('/')
            p_url = translated_url.split('/')
            if len(req_url) > len(p_url):
                for idx, val in enumerate(p_url[:-1]):
                    req_url[idx] = val

                translated_url = '/'.join(req_url)

            activate(current_language)

            return translated_url
        elif match.url_name == 'wagtailsearch_search':
            path_components = [component for component in non_prefixed_path.split('/') if component]

            translated_url = '/' + lang + '/' + path_components[0] + '/'
            if request.GET:
                translated_url += '?'
                for count, (key, value) in enumerate(iteritems(request.GET)):
                    if count != 0:
                        translated_url += "&"
                    translated_url += key + '=' + value
            return translated_url

    return ''

