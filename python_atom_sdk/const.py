# -*- coding: utf-8 -*-

from . import setting


class Status:
    """
    @summary: 原子执行结果定义
    """
    ERROR = setting.BK_ATOM_STATUS.get("ERROR", None)
    FAILURE = setting.BK_ATOM_STATUS.get("FAILURE", None)
    SUCCESS = setting.BK_ATOM_STATUS.get("SUCCESS", None)


class OutputTemplateType:
    """
    @summary: 原子输出模版类型
    """
    DEFAULT = setting.BK_OUTPUT_TEMPLATE_TYPE.get("DEFAULT", None)


class OutputFieldType:
    """
    @summary: 原子输出字段类型
    """
    STRING = setting.BK_OUTPUT_FIELD_TYPE.get("STRING", None)
    ARTIFACT = setting.BK_OUTPUT_FIELD_TYPE.get("ARTIFACT", None)
    REPORT = setting.BK_OUTPUT_FIELD_TYPE.get("REPORT", None)
