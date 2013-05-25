import os
from appconf import AppConf


class CmlConf(AppConf):
    USE_ZIP = False
    FILE_LIMIT = 1000000
    FILE_ROOT = os.path.join('files', 'cml')
