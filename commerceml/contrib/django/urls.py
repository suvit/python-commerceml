# -*- coding: utf-8 -*-
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('commerceml.contrib.django.views',
    url(r'^1c_exchange.php$', 'dispatcher', name='cml-dispatcher')
)
