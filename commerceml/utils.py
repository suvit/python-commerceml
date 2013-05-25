# -*- coding: utf-8 -
from datetime import datetime
from decimal import Decimal
from xml.etree.ElementTree import ElementTree, Element, SubElement

from commerceml.object import Order, OrderItem

def import_catalog(filename):
    pass  # TODO


def import_orders(filename):
    tree = ElementTree.parse(filename)

    for doc in tree.getroot().findall(u'Документ'):
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
            orderitem_ids.append(shop_orderitem.id)

        for shop_orderitem in order.items().exclude(id__in=orderitem_ids):
            shop_orderitem.delete()


def export_orders(last_update=None):
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
        SubElement(contact, u'Тип').text = u'Телефон'
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
