# -*- coding: utf-8 -*-

import os
import sys
import json

from .bklog import getLogger
from .input import ParseParams
from .output import SetOutput
from .const import Status, OutputTemplateType, OutputFieldType

log = getLogger()
parseParamsObj = ParseParams()
params = parseParamsObj.get_input()
status = Status()
output_template_type = OutputTemplateType()
output_field_type = OutputFieldType()


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


def get_artifact_urls(file_src, file_path):
    from .openapi import OpenApi
    client = OpenApi()
    project_code = get_project_name()
    pipeline_id = get_pipeline_id()
    build_id = get_pipeline_build_id()
    return client.get_artifacts_url(file_src, file_path, project_code, pipeline_id, build_id)


def set_output(output):
    """
    @summary: 设置输出
    """
    setOutput = SetOutput()
    setOutput.set_output(output)


def upload_file(file_src, file_path, upload_url, params={}, headers={}):
    """
    @summary: 上传构件到第三方平台
    """
    from .openapi import OpenApi
    client = OpenApi()

    result, download_url_list = get_artifact_urls(file_src, file_path)
    if not result:
        return result

    return client._upload_file(download_url_list[0], upload_url, params=params, headers=headers)


if __name__ == "__main__":
    pass
