
from django.conf import settings
from django.http import HttpResponse

from commerceml.contrib.django.conf import CmlConf

def dispatcher(request):
    type = request.GET.get('type')
    mode = request.GET.get('mode')
    try:
        view = globals()['%s_%s' % (type, mode)]
    except KeyError:
        return HttpResponse('error')

    return view(request)


def catalog_checkout(request):
    session = request.session
    return HttpResponse('success\n%s\n%s' % (settings.SESSION_COOKIE_NAME,
                                             session.session_key))


def catalog_init(request):
    result = 'zip=%s\n'
             'file_limit=%s' % ('yes' if CmlConf.USE_ZIP else 'no',
                                CmlConf.FILE_LIMIT)
    return HttpResponse(result)


def catalog_file(request):
    if request.method != 'POST':
        return HttpResponse('error')

    try:
        filename = request.GET['filename']
    except KeyError:
        return HttpResponse('error')

    try:
        file = request.FILES[filename]
    except KeyError:
        return HttpResponse('error')

    file.save()

    return HttpResponse('success')


def catalog_import(request, filename):
    if request.method != 'POST':
        return HttpResponse('error')

    raise NotImplementedError


# Sale views
sale_checkout = catalog_checkout
sale_init = catalog_init


def sale_query(request):
    orders = get_orders()
    return HttpResponse(orders.as_xml())


def sale_success(request):
    # log success
    return HttpResponse('success')

def update_orders(file):
    pass

sale_file = catalog_file
