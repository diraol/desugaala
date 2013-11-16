""" Helper Functions. """

import json
from functools import wraps

from django.http import HttpResponse
from django.core.cache import cache
from django.http import HttpResponseForbidden


def json_rest(func):
    """
    Do a wrap on the body of the request page, treating it as a json.

    Parses its content and sends the arguments
    to the specified function.

    Returns:
        httpResponse object

    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponse('bad request', status=400)

        result = json.dumps(func(request, data, *args, **kwargs))
        return HttpResponse(result, content_type='application/json')

    return inner


# http://djangosnippets.org/snippets/2017/
def throttle_post(func, duration=5):
    """Use memcached to throttle POSTs.

    Returns:
        the function passed as argument cached or not

    """
    def inner(request, *args, **kwargs):
        if request.method == 'POST':
            remote_addr = request.META.get('HTTP_X_FORWARDED_FOR') or \
                request.META.get('REMOTE_ADDR')
            key = '%s.%s' % (remote_addr, request.get_full_path())
            if cache.get(key):
                return HttpResponseForbidden('Try slowing down a little.')
            else:
                cache.set(key, 1, duration)
        return func(request, *args, **kwargs)
    return inner
