# -*- coding: utf-8 -*-

import os
import sys
import json

from . import setting
from .log import getLogger
from .input import ParseParams
from .output import SetOutput

log = getLogger()
parseParamsObj = ParseParams()
params = parseParamsObj.get_input()

# 执行结果
def get_status(status):
    return setting.BK_ATOM_STATUS.get(status.upper(), None)


# 输出模版类型
def get_output_template_type(type):
    return setting.BK_OUTPUT_TEMPLATE_TYPE.get(type.upper(), None)


# 输出字段类型
def get_output_field_type(type):
    return setting.BK_OUTPUT_FIELD_TYPE.get(type.upper(), None)


def get_input():
    """
    @summary: 获取原子输入参数
    @return dict
    """
    return params


def get_project_name():
    return params.get("project.name", None)


def get_project_name_cn():
    return params.get("project.name.chinese", None)


def get_pipeline_id():
    return params.get("pipeline.id", None)


def get_pipeline_name():
    return params.get("pipeline.name", None)


def get_pipeline_build_id():
    return params.get("pipeline.build.id", None)


def get_pipeline_build_num():
    return params.get("pipeline.build.num", None)


def get_pipeline_start_type():
    return params.get("pipeline.start.type", None)


def get_pipeline_start_user_id():
    return params.get("pipeline.start.user.id", None)


def get_pipeline_start_user_name():
    return params.get("pipeline.start.user.name", None)


def get_pipeline_time_start_mills():
    return params.get("pipeline.time.start", None)


def get_pipeline_version():
    return params.get("pipeline.version", None)


def get_artifact_urls(file_src, file_path, project_code, pipeline_id, build_id):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_artifacts_url(file_src, file_path, project_code, pipeline_id, build_id)


def set_output(output):
    """
    @summary: 设置输出
    """
    setOutput = SetOutput()
    setOutput.set_output(output)


if __name__ == "__main__":
    pass
