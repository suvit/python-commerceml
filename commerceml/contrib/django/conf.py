
from appconf import conf


class CmlConf(Conf):
    USE_ZIP = True
    FILE_LIMIT = 1000000
    FILE_ROOT = '/files/cml/'
