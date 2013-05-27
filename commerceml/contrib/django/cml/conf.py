import os
from appconf import AppConf

from commerceml import conf as default


class CmlConf(AppConf):
    USE_ZIP = default.USE_ZIP
    FILE_LIMIT = default.FILE_LIMIT
    FILE_ROOT = default.FILE_ROOT
    MAX_EXEC_TIME = default.MAX_EXEC_TIME

