# -*- coding: utf-8 -
import os
from django.conf import settings

RESPONSE_SUCCESS = 'success'
RESPONSE_PROGRESS = 'progress'
RESPONSE_ERROR = 'failure'

Shop = 'path.to.shop.api'
Order = 'path.to.order'
OrderItem = 'path.to.orderitem'
Product = 'path.to.product'
Category = 'path.to.category'
Manufacturer = 'path.to.manufacturer'
Image = 'path.to.image'
Property = 'path.to.property'

MAX_EXEC_TIME = 60
USE_ZIP = False
FILE_LIMIT = 0
FILE_ROOT = os.path.join(settings.MEDIA_ROOT, 'cml')