# -*- coding: utf-8 -
from datetime import datetime
from decimal import Decimal
from xml.etree.ElementTree import ElementTree, Element, SubElement

from commerceml.conf import MAX_EXEC_TIME, RESPONSE_SUCCESS, RESPONSE_PROGRESS
from commerceml.object import Order, OrderItem


class Importer(object):
    def __init__(self, filename, state=None):
        self.filename = filename
        self.state = state or {}
        self.start_time = state.get('start_time', datetime.now())
        self.max_time = state.get('max_time', MAX_EXEC_TIME)

    def import_catalog(self):
        tree = ElementTree.parse(self.filename)

        if self.filename == 'import.xml':

            last_product = self.state.get('last_product', 0)

            if last_product == 0:  # first import
                xml_catalog = tree.findall(u'Классификатор')
                self.import_categories(xml_catalog)
                self.import_props(xml_catalog)

            xml_products = tree.findall(u'Товар')[last_product:]
            for i, xml_product in enumerate(xml_products):
                self.import_product(xml_product)

                exec_time = (datetime.now() - self.start_time).seconds
                if exec_time + 1 >= self.max_exec_time:
                    self.state['last_product'] = last_product + i + 1
                    return (u'%s\n'
                            u'Выгружено товаров: %s\n' % (RESPONSE_PROGRESS,
                                                          i + 1))

            del self.state['last_product']
            return SUCCESS

        elif self.filename == 'offers.xml':

            last_offer = self.state.get('last_offer', 0)

            xml_offers = tree.findall(u'Предложение')[last_offer:]
            for i, xml_offer in enumarate(xml_offers):
                self.import_offer(xml_offer)

                exec_time = (datetime.now() - self.start_time).seconds
                if exec_time + 1 >= self.max_exec_time:
                    self.state['last_offer'] = last_offer + i + 1
                    return (u'%s\n'
                            u'Выгружено товарных предложений:'
                            u' %s\n' % (RESPONSE_PROGRESS,
                                        i + 1))

            del self.state['last_offer']
            return SUCCESS

    def import_categories(self, xml_catalog, parent=0):
        for xml_cat in xml_catalog.findall(u'Группы/Группа'):
            external_id = xml_cat.find(u'Ид').text
            if not shop_category:
                name = xml_cat.find(u'Наименование').text
                shop_category = Category.objects.create(external_id=external_id,
                                        parent=parent or None,
                                        name=name,
                                        slug=Slugify(name))

            cat_id = shop_category.id
            self.state.setdefault('cat_map', {})[external_id] = cat_id
            self.import_categories(xml_cat, parent=cat_id)

    def import_props(self, xml_catalog):
        properties = []

        xml_properties = xml_catalog.findall(u'Свойства/СвойствоНоменклатуры')
        if not xml_properties:
            xml_properties = xml_catalog.findall(u'Свойства/Свойство')

        for xml_prop in xml_properties:
            prop_id = xml_prop.find('Ид').text
            prop_name = xml_prop.find('Наименование').text

            if prop_name == u'Производитель':
                self.state['mnf_external_id'] = prop_id
                continue

            shop_property = Property.objects.get(external_id=prop_id)
            if not shop_property:
                shop_property = Property.objects.create(external_id=prop_id,
                                                        name=prop_name)

    def import_product(self, xml_product):
        external_id = xml_product.find(u'Ид').text
        product_name = xml_product.find(u'Наименование').text
        product_description = xml_product.find(u'Описание').text
        product_status = xml_product.find(u'Статус').text

        shop_product = Product.objects.get(external_id=external_id)
        if not shop_product:
            shop_product = Product.objects.create(external_id=external_id,
                                                  name=product_name,
                                                  slug=Slugify(product_name),
                                                  description=product_description)

        else:  # elif full_update:
            shop_product.name = product_name
            shop_product.slug = Slugify(product_name)
            shop_product.description = description

            shop_product.categories.remove()
            shop_product.images.remove()
            shop_product.save()

        if product_status == u'Удален':
            shop_product.delete()
            return

        # TODO if several groups
        external_cat_id = xml_product.find(u'Группы/Ид').text
        category = Category.objects.get(external_id=external_cat_id)
        shop_product.categories.add(category)

        for xml_image in xml_product.findall(u'Картинка'):
            image = Image.objects.create(file=xml_image.text)
            shop_product.images.add(image)

        for xml_prop in xml_product.findall(u'ЗначенияСвойств/ЗначенияСвойства'):
            prop_id = xml_prop.find(u'Ид').text
            # TODO several values
            prop_value = xml_prop.find(u'Значение').text

            if prop_id == self.state['mnf_external_id']:
                mnf = Manufacturer.objects.get_or_create(name=prop_value)
                shop_product.manufacturer = mnf
            else:
                shop_prop = Property.objects.get(external_id=prop_id)
                shop_product.add_property(shop_prop, prop_value)
                shop_product.category.add_property(shop_prop)

    def import_offer(self, xml_offer):
        external_id = xml_offer.find(u'Ид').text
        shop_product = Product.objects.get(external_id=external_id)

        shop_product.price = xml_offer.find(u'Цены/Цена/ЦенаЗаЕдиницу').text

        # TODO convert shop currency to 1c currency
        #currency = xml_offer.find(u'Цены/Цена/Валюта').text
        #shop_product.price = convert(shop_product.price, currency)

        shop_product.stock_amount = xml_offer.find(u'Количество').text
        shop_product.save()

    def import_orders(self):
        tree = ElementTree.parse(self.filename)

        for doc in tree.getroot().findall(u'Документ'):
            self.import_order(doc)

    def import_order(self, doc):
        order = Order()
        order.id = doc.find(u'Номер').text().strip()

        shop_order = Order.objects.get(pk=order.id)

        order.created = '%s %s' % (doc.find(u'Дата').text(),
                                   doc.find(u'Время').text())

        order.customer = doc.find(u'Контрагенты/Контрагент/Наименование').text()
        order.price = Decimal(doc.find(u'Сумма').text())

        proveden = udalen = False
        for prop in doc.findall(u'ЗначенияРеквизитов/ЗначениеРеквизита'):
            prop_title = prop.find(u'Наименование').text()
            if prop_title == u'Проведен':
                proveden = prop.find(u'Значение').text() == 'true'
            elif prop_title == u'ПометкаУдаления':
                udalen = prop.find(u'Значение').text() == 'true'

        if udalen:
            order.status = state.DELETED
        elif proveden:
            order.status = state.ACEPTED
        elif not proveden:
            order.status = state.NEW

        if shop_order.id:
            order.update(shop_order)
        else:
            order.id = shop_order.save()

        orderitems_ids = []
        for xml_product in doc.findall(u'Товары/Товар'):
            orderitems_ids.append(self.import_orderitem(xml_product, order))

        for shop_orderitem in order.items().exclude(id__in=orderitem_ids):
            shop_orderitem.delete()

    def import_orderitem(self, xml_product, order):

        orderitem = OrderItem()

        product_1c_id = xml_product.find(u'Ид').text()

        product = Product.objects.get(external_id=product_1c_id)

        orderitem.order = order
        orderitem.product = product

        orderitem.sku = xml_product.find(u'Артикул').text()
        orderitem.product_name = xml_product.find(u'Наименование').text()
        orderitem.amount = xml_product.find(u'Количество').text()
        orderitem.price = Decimal(xml_product.find(u'ЦенаЗаЕдиницу').text())

        # orderitem discounts
        for xml_discount in doc.findall(u'Скидки/Скидка'):
            discount = xml_discount.find(u'Процент').text()
            orderitem.price = orderitem.price * (100 - int(discount))/100

        shop_orderitem = OrderItem.objects.get(order=order,
                                               product=product)

        if shop_orderitem.id:
            orderitem.update(shop_orderitem)
        else:
            shop_orderitem.save()

        return shop_orderitem.id


class Exporter(object):
    pass


def export_orders(request, last_update=None):
    root = Element(u'КоммерческаяИнформация')
    root.set(u'ВерсияСхемы', '2.05')
    root.set(u'ДатаФормирования', datetime.now())

    orders = Order.object.filter(state_changed__gt=last_update)

    for order in orders:
        xml_order = SubElement(root, u'Документ')

        SubElement(xml_order, u'Ид').text = str(order.id)
        SubElement(xml_order, u'Номер').text = str(order.number)

        SubElement(xml_order, u'Дата').text = str(order.created.date())
        SubElement(xml_order, u'Время').text = str(order.created.time())

        SubElement(xml_order, u'ХозОперация').text = u'Заказ товара'
        SubElement(xml_order, u'Роль').text = u'Продавец'

        SubElement(xml_order, u'Курс').text = '1'
        SubElement(xml_order, u'Сумма').text = order.price

        SubElement(xml_order, u'Комментарий').text = order.comment

        contragents = SubElement(xml_order, u'Контрагенты')
        customer = SubElement(contragents, u'Контрагент')
        SubElement(customer, u'Ид').text = order.get_customer().id
        SubElement(customer, u'Наименование').text = order.name
        SubElement(customer, u'ПолноеНаименование').text = order.fullname
        SubElement(customer, u'Роль').text = u'Покупатель'

        addr = SubElement(customer, u'АдресРегистрации')
        SubElement(addr, u'Представление').text = order.shipping_address()
        addr_field = SubElement(addr, u'АдресноеПоле')
        SubElement(addr_field, u'Тип').text = u'Страна'
        SubElement(addr_field, u'Значение').text = shop.country
        addr_field = SubElement(addr, u'АдресноеПоле')
        SubElement(addr_field, u'Тип').text = u'Регион'
        SubElement(addr_field, u'Значение').text = order.shipping_address()

        contacts = SubElement(customer, u'Контакты')
        contact = SubElement(contacts, u'Контакт')
        SubElement(contact, u'Тип').text = u'Телефон'
        SubElement(contact, u'Значение').text = order.shipping_phone
        contact = SubElement(contacts, u'Контакт')
        SubElement(contact, u'Тип').text = u'Почта'
        SubElement(contact, u'Значение').text = order.shipping_email

        xml_orderitems = SubElement(xml_order, u'Товары')
        for orderitem in order.items():
            product = orderitem.product
            try:
                external_id = product.external_id
            except AttributeError:
                external_id = orderitem.product_id

            xml_product = SubElement(xml_orderitems, u'Товар')
            SubElement(xml_product, u'Ид').text = external_id
            SubElement(xml_product, u'Артикул').text = product.sku
            SubElement(xml_product, u'Наименование').text = orderitem.product_name
            price = orderitem.get_price_with_discount()
            SubElement(xml_product, u'ЦенаЗаЕдиницу').text = price
            SubElement(xml_product, u'Количество').text = orderitem.product_amount
            SubElement(xml_product, u'Cумма').text = price * orderitem.product_amount

            xml_discounts = SubElement(xml_product, u'Скидки')
            xml_discount = SubElement(xml_discounts, u'Скидка')

            SubElement(xml_discount, u'Cумма').text = order.discount_price
            SubElement(xml_discount, u'УчтеноВСумме').text = "true"

            xml_props = SubElement(xml_product, u'ЗначенияРеквизитов')
            xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
            SubElement(xml_prop, u'Наименование').text = u'ВидНоменклатуры'
            SubElement(xml_prop, u'Значение').text = u'Товар'
            xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
            SubElement(xml_prop, u'Наименование').text = u'ТипНоменклатуры'
            SubElement(xml_prop, u'Значение').text = u'Товар'

        if order.shipping_price > 0:
            xml_product = SubElement(xml_orderitems, u'Товар')
            SubElement(xml_product, u'Ид').text = order.shipping_method_id
            SubElement(xml_product, u'Артикул').text = order.shipping_method.sku
            SubElement(xml_product, u'Наименование').text = order.shipping_method.sku
            price = order.shipping_price
            SubElement(xml_product, u'ЦенаЗаЕдиницу').text = price
            SubElement(xml_product, u'Количество').text = 1
            SubElement(xml_product, u'Cумма').text = price

            xml_props = SubElement(xml_product, u'ЗначенияРеквизитов')
            xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
            SubElement(xml_prop, u'Наименование').text = u'ВидНоменклатуры'
            SubElement(xml_prop, u'Значение').text = u'Услуга'
            xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
            SubElement(xml_prop, u'Наименование').text = u'ТипНоменклатуры'
            SubElement(xml_prop, u'Значение').text = u'Услуга'

        if order.payment_price > 0:
            xml_product = SubElement(xml_orderitems, u'Товар')
            SubElement(xml_product, u'Ид').text = order.payment_method_id
            SubElement(xml_product, u'Артикул').text = order.payment_method.sku
            SubElement(xml_product, u'Наименование').text = order.payment_method.sku
            price = order.payment_price
            SubElement(xml_product, u'ЦенаЗаЕдиницу').text = price
            SubElement(xml_product, u'Количество').text = 1
            SubElement(xml_product, u'Cумма').text = price

            xml_props = SubElement(xml_product, u'ЗначенияРеквизитов')
            xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
            SubElement(xml_prop, u'Наименование').text = u'ВидНоменклатуры'
            SubElement(xml_prop, u'Значение').text = u'Услуга'
            xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
            SubElement(xml_prop, u'Наименование').text = u'ТипНоменклатуры'
            SubElement(xml_prop, u'Значение').text = u'Услуга'

        xml_props = SubElement(xml_order, u'ЗначенияРеквизитов')
        xml_prop = SubElement(xml_props, u'ЗначениеРеквизита')
        if order.state == 1:
            SubElement(xml_prop, u'Наименование').text = u'Статус заказа'
            SubElement(xml_prop, u'Значение').text = u'[N] Принят'
        elif order.state == 2:
            SubElement(xml_prop, u'Наименование').text = u'Статус заказа'
            SubElement(xml_prop, u'Значение').text = u'[F] Доставлен'
        elif order.state == 3:
            SubElement(xml_prop, u'Наименование').text = u'Отменен'
            SubElement(xml_prop, u'Значение').text = u'true'

    # Needed BOM ?
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '%s' % ElementTree.tostring(root, encoding='utf8'))
