# -*- coding: utf-8 -*-
from django.dispatch import Signal

requested_catalog_file = Signal(providing_args=["file"])

requested_catalog_import = Signal(providing_args=["data"])

requested_sale_query = Signal(providing_args=["data"])

requested_sale_file = Signal(providing_args=["file"])

requested_sale_success = Signal()
