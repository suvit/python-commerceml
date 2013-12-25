# -*- coding: utf-8 -*-
from django.http import HttpResponse

from commerceml.conf import RESPONSE_SUCCESS, RESPONSE_ERROR
from commerceml.contrib.django.signals import (requested_catalog_file,
                                               requested_catalog_import,
                                               requested_sale_query,
                                               requested_sale_success,
                                               requested_sale_file)
from commerceml.utils import Importer, export_orders


def import_catalog_file(sender, **kwargs):
    request = sender['request']

    sender['response'] = HttpResponse(RESPONSE_SUCCESS)
requested_catalog_file.connect(import_catalog_file)

def import_catalog(sender, **kwargs):
    filename = sender['filename']
    request = sender['request']

    response =  Importer(filename, request.session).import_catalog()
    sender['response'] = response

requsted_catalog_import.connect(import_catalog)

def export_sale(sender, **kwargs):
    request = sender['request']

    response = HttpResponse(export_orders(request),
                            content_type='text/xml; charset=utf-8')
    sender['response'] = response
requested_sale_query.connect(export_sale)

def import_sale(sender, **kwargs):
    filename = sender['filename']
    request = sender['request']

    response = Importer(filename, request.session).import_orders()
    sender['response'] = response
requested_sale_file.connect(import_sale)
