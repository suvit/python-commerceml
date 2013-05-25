
import logging
import os

from xml.etree import ElementTree

from django.conf import settings
from django.http import HttpResponse

from commerceml.utils import (import_orders, export_orders,
                              import_catalog)
from commerceml.contrib.django.cml.conf import CmlConf

logger = logging.getLogger(__name__)

SUCCESS = 'success'
ERROR = 'failure'


def dispatcher(request):
    type = request.GET.get('type')
    mode = request.GET.get('mode')
    try:
        view = globals()['%s_%s' % (type, mode)]
    except KeyError:
        return HttpResponse(ERROR)

    logger.debug('dispatch to %s' % view)
    return view(request)


def catalog_checkout(request):
    session = request.session
    return HttpResponse('%s\n%s\n%s' % (SUCCESS,
                                        settings.SESSION_COOKIE_NAME,
                                        session.session_key))


def catalog_init(request):
    result = ('zip=%s\n'
              'file_limit=%s' % ('yes' if CmlConf.USE_ZIP else 'no',
                                 CmlConf.FILE_LIMIT))
    return HttpResponse(result)


def handle_uploaded_file(f, name=None):
    with open(os.path.join(settings.MEDIA_ROOT,
                           CmlConf.FILE_ROOT,
                           name or f.name),
              'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return destination

def import_file(request, callback=None):
    if request.method != 'POST':
        return HttpResponse(ERROR)

    try:
        filename = request.GET['filename']
    except KeyError:
        if settings.DEBUG:
            raise
        return HttpResponse(ERROR)

    try:
        file = request.FILES[filename]
    except KeyError:
        if settings.DEBUG:
            raise

        return HttpResponse(ERROR)

    dest = handle_uploaded_file(file, filename)

    res = SUCCESS
    if callback:
         res = callback(dest)

    return HttpResponse(res)


def catalog_file(request):
    return import_file(request)


def catalog_import(request):
    try:
        filename = request.GET['filename']
    except KeyError:
        if settings.DEBUG:
            raise
        return HttpResponse(ERROR)

    return import_catalog(filename)

# Sale views
sale_checkout = catalog_checkout
sale_init = catalog_init


def sale_query(request):
    return HttpResponse(export_orders(),
                        content_type='text/xml; charset=utf-8')


def sale_success(request):
    # log success
    return HttpResponse(SUCCESS)


def sale_file(request):
    return import_file(request, callback=import_orders)
