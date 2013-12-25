# -*- coding: utf-8 -*-
import dbsettings
from dbsettings import values


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
