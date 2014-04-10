# -*- coding: utf-8 -*-
import logging
import os
import datetime

from xml.etree import ElementTree

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt

from commerceml.conf import RESPONSE_SUCCESS, RESPONSE_ERROR

from commerceml.contrib.django.cml.conf import CmlConf
from commerceml.contrib.django.cml.models import exchange_1c
from commerceml.contrib.django.http_auth import http_auth
from commerceml.contrib.django.signals import (requested_catalog_file,
                                               requested_catalog_import,
                                               requested_sale_query,
                                               requested_sale_success,
                                               requested_sale_file)

logger = logging.getLogger(__name__)


@csrf_exempt
@http_auth
@permission_required('cml.exchange_1c')
def dispatcher(request):
    type = request.GET.get('type')
    mode = request.GET.get('mode')
    try:
        view = globals()['%s_%s' % (type, mode)]
    except KeyError:
        output = u'\n'.join([RESPONSE_ERROR, 'Unknown command type.'])
        return HttpResponse(output)

    logger.debug('dispatch to %s' % view)
    return view(request)


def catalog_checkauth(request):
    session = request.session
    return HttpResponse('%s\n%s\n%s\n' % (RESPONSE_SUCCESS,
                                          settings.SESSION_COOKIE_NAME,
                                          session.session_key))


def catalog_init(request):
    result = ('zip=%s\n'
              'file_limit=%s\n' % ('yes' if CmlConf.USE_ZIP else 'no',
                                   CmlConf.FILE_LIMIT))

    # increase index to add this index to new files
    exchange_1c.import_index += 1

    return HttpResponse(result)


def handle_uploaded_file(f, name=None):
    with open(os.path.join(CmlConf.IMPORT_FOLDER,
                           name or f.name),
              'ab') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return destination.name


def import_file(request, signal):
    if request.method != 'POST':
        return HttpResponse(RESPONSE_ERROR)

    try:
        filename = request.GET['filename']
    except KeyError:
        if settings.DEBUG:
            raise
        return HttpResponse(RESPONSE_ERROR)

    filename = os.path.basename(filename)
    old_name, ext = os.path.splitext(filename)
    new_filename = '%s_%s%s' % (old_name, exchange_1c.import_index, ext)

    file = SimpleUploadedFile(new_filename, request.read(),
                              content_type='text/xml')

    filepath = handle_uploaded_file(file, new_filename)

    data = {'request': request,
            'filename': filename,
            'new_filename': new_filename,
            'file': file,
            'filepath': filepath}

    signal.send(data)

    if 'response' in data:
        return data['response']
    else:
        return HttpResponse(RESPONSE_SUCCESS)


def catalog_file(request):
    return import_file(request, requested_catalog_file)


def catalog_import(request):
    try:
        filename = request.GET['filename']
    except KeyError:
        if settings.DEBUG:
            raise
        return HttpResponse(RESPONSE_ERROR)

    filename = os.path.basename(filename)
    old_name, ext = os.path.splitext(filename)
    new_filename = '%s_%s%s' % (old_name, exchange_1c.import_index, ext)

    data = {'request': request,
            'filename': filename,
            'new_filename': new_filename,
            'filepath': os.path.join(CmlConf.IMPORT_FOLDER, new_filename)}

    requested_catalog_import.send(data)
    if 'response' in data:
        return data['response']
    else:
        exchange_1c.imported = datetime.datetime.now()
        return HttpResponse(RESPONSE_SUCCESS)

# Sale views
sale_checkauth = catalog_checkauth
sale_init = catalog_init


def sale_query(request):
    exported_new = datetime.datetime.now()
    data = {'request': request,
            'exported_new': exported_new}

    requested_sale_query.send(data)

    if 'response' in data:
        return data['response']
    else:
        return HttpResponse(RESPONSE_SUCCESS)


def sale_success(request):

    # fixed exported(commited) to db settings
    exchange_1c.exported = exchange_1c.exported_new

    data = {'request': request,
            'exported': exchange_1c.exported}
    requested_sale_success.send(data)

    if 'response' in data:
        return data['response']
    else:
        return HttpResponse(RESPONSE_SUCCESS)


def sale_file(request):
    return import_file(request, requested_sale_file)
