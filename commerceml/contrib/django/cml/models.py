# -*- coding: utf-8 -*-
from django.db.models import signals

import dbsettings
from dbsettings import values


def create_perm(app, created_models, verbosity, db, **kwargs):
    """
    Creates a fake content type and permission
    to be able to check for permissions
    """
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    if ContentType._meta.installed and Permission._meta.installed:
        content_type, created = ContentType.objects.get_or_create(
            name='exchange_1c',
            app_label='cml',
            model='cml')

        permission, created = Permission.objects.get_or_create(
            name='Can exchange with 1c',
            content_type=content_type,
            codename='exchange_1c')


signals.post_syncdb.connect(create_perm, dispatch_uid="cml.create_perm")


class Exchange1c(dbsettings.Group):
    export_index = values.IntegerValue(u'1c Экспорт: Номер последнего документа', default=0)
    exported = values.DateTimeValue(u'1с Экспорт: Дата последнего экспорта',
                                    required=False, default='')
    exported_new = values.DateTimeValue(u'1с Экспорт: Дата последнего экспорта. новое значение',
                                        required=False, default='')

    import_index = values.IntegerValue(u'1c Импорт: Номер последнего документа', default=0)
    imported = values.DateTimeValue(u'1с Импорт: Дата последнего импорта',
                                    required=False, default='')

exchange_1c = Exchange1c(u'Обмен с 1с')
