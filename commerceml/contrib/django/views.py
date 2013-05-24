
from django.http import HttpResponse

COOKIE_NAME = 'python-cml'
COOKIE_VALUE = 'python-cml'
USE_ZIP = True
FILE_LIMIT = 100000


def dispatcher(request):
    type = request.GET.get('type')
    mode = request.GET.get('mode')
    try:
        view = globals()['%s_%s' % (type, mode)]
    except KeyError:
        return HttpResponse('error')

    return view(request)


def catalog_checkout(request):
    return HttpResponse('success\n%s\n%s' % (COOKIE_NAME,
                                             COOKIE_VALUE))


def catalog_init(request):
    return HttpResponse('zip=%s\nfile_limit=%s' % ('yes' if USE_ZIP else 'no',
                                                   FILE_LIMIT))


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


sale_file = catalog_file
