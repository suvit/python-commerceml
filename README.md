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

Настройки django
-----------------

`CML_FILE_LIMIT`
`CML_USE_ZIP`




TODO
-----------------

* Написать документация
* Написать тесты
* django. создание папки в MEDIA_ROOT по умолчанию
* django. USE_ZIP == True
* django. FILE_LIMIT > 0
* django. импорт и экспорт заказов
* django. экспорт каталога
* django. basic auth
* django. lfs. api
