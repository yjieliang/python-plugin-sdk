# -*- coding: utf-8 -*-

import os
import sys
import json

from . import setting
from .log import getLogger
from .input import ParseParams
from .output import SetOutput

log = getLogger()

# 执行结果
status = {
    "success": setting.BK_ATOM_STATUS.get("SUCCESS", ""),
    "failure": setting.BK_ATOM_STATUS.get("FAILURE", ""),
    "error": setting.BK_ATOM_STATUS.get("ERROR", "")
}

# 输出模版类型
output_template_type = {
    "default": setting.BK_OUTPUT_TEMPLATE_TYPE.get("DEFAULT", "")
}

# 输出字段类型
output_field_type = {
    "string": setting.BK_OUTPUT_FIELD_TYPE.get("STRING", ""),
    "artifact": setting.BK_OUTPUT_FIELD_TYPE.get("ARTIFACT", ""),
    "report": setting.BK_OUTPUT_FIELD_TYPE.get("REPORT", "")
}


def get_input():
    """
    @summary: 获取原子输入参数
    @return dict
    """
    parseParams = ParseParams()

    return parseParams.get_input()


def set_output(output):
    """
    @summary: 设置输出
    """
    setOutput = SetOutput()
    setOutput.set_output(output)


if __name__ == "__main__":
    pass
