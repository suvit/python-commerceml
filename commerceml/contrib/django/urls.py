# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns("commerceml.contrib.django.views",
    url(r'^1c_exchange.php$', 'dispatcher', name='cml-dispatcher')
)
