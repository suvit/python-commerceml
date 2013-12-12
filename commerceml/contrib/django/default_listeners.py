
from django.http import HttpResponse

from commerceml.utils import Importer, export_orders

from commerceml.contrib.django.signals import (requested_catalog_file,
                                               requested_catalog_import,
                                               requested_sale_query,
                                               requested_sale_success,
                                               requested_sale_file)


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
