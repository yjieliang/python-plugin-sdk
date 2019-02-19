# -*- coding: utf-8 -*-

import os
import json

from . import setting
from . import log


class ParseParams():
    """
    @summary: 获取原子入参
    """

    _log = log.getLogger()

    def __init__(self):
        self.data_path = os.getenv(setting.BK_DATA_DIR, '.')
        self.input_file_name = os.getenv(setting.BK_DATA_INPUT, 'input.json')

    def get_input(self):
        """
        @summary: 获取原子输入参数
        @return dict
        """
        input_file_path = os.path.join(self.data_path, self.input_file_name)
        self._log.info("input_file_path: {}".format(input_file_path))
        if os.path.exists(input_file_path):
            with open(input_file_path, "r") as f:
                content = f.read()
                return json.loads(content)

        return {}
