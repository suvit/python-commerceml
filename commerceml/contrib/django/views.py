
import logging
import os

from xml.etree import ElementTree

from django.conf import settings
from django.http import HttpResponse

from commerceml.conf import RESPONSE_SUCCESS, RESPONSE_ERROR

from commerceml.contrib.django.signals import (requested_catalog_file,
                                               requested_catalog_import,
                                               requested_sale_query,
                                               requested_sale_success,
                                               requested_sale_file)
from commerceml.contrib.django.cml.conf import CmlConf


logger = logging.getLogger(__name__)


def dispatcher(request):
    type = request.GET.get('type')
    mode = request.GET.get('mode')
    try:
        view = globals()['%s_%s' % (type, mode)]
    except KeyError:
        return HttpResponse(RESPONSE_ERROR)

    logger.debug('dispatch to %s' % view)
    return view(request)


def catalog_checkauth(request):
    session = request.session
    return HttpResponse('%s\n%s\n%s' % (RESPONSE_SUCCESS,
                                        settings.SESSION_COOKIE_NAME,
                                        session.session_key))


def catalog_init(request):
    result = ('zip=%s\n'
              'file_limit=%s' % ('yes' if CmlConf.USE_ZIP else 'no',
                                 CmlConf.FILE_LIMIT))
    return HttpResponse(result)


def handle_uploaded_file(f, name=None):
    with open(os.path.join(CmlConf.IMPORT_FOLDER,
                           name or f.name),
              'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return destination.name

def import_file(request, callback=None):
    if request.method != 'POST':
        return HttpResponse(RESPONSE_ERROR)

    try:
        filename = request.GET['filename']
    except KeyError:
        if settings.DEBUG:
            raise
        return HttpResponse(RESPONSE_ERROR)

    try:
        file = request.FILES[filename]
    except KeyError:
        if settings.DEBUG:
            raise

        return HttpResponse(RESPONSE_ERROR)

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
        return HttpResponse(RESPONSE_ERROR)

    data = {'request': request,
            'filename': filename}
    requsted_catalog_import.send(data)

    if 'response' in data:
        return data['response']
    else:
        return HttpResponse(RESPONSE_ERROR)

# Sale views
sale_checkauth = catalog_checkauth
sale_init = catalog_init


def sale_query(request):
    data = {'request': request}

    requested_sale_query.send(data)

    if 'response' in data:
        return data['response']
    else:
        return HttpResponse(RESPONSE_ERROR)


def sale_success(request):
    # log success
    return HttpResponse(RESPONSE_SUCCESS)


def sale_file(request):
    importer = Importer(filename, request.session)
    return import_file(request, callback=importer.import_orders)
