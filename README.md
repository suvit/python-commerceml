python-commerceml
=================

Обмен между 1с и сайтом

Установка
-------------

``pip install python-commerceml``

* django

    добавить приложение ``commerceml.contrib.django.cml`` в INSTALLED_APPS

    добавить пути в общий urls

        (r'^1c/', include('commerceml.contrib.django.urls')),


TODO
-----------------

* Написать документация
* Написать тесты
* django. создание папки в MEDIA_ROOT по умолчанию
* django. USE_ZIP == True
* django. импорт каталога
* django. basic auth
