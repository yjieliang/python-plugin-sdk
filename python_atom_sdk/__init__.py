# -*- coding: utf-8 -*-

import os
import sys
import json

from .bklog import getLogger
from .input import ParseParams
from .output import SetOutput
from .const import Status, OutputTemplateType, OutputFieldType, OutputReportType

log = getLogger()
parseParamsObj = ParseParams()
params = parseParamsObj.get_input()
status = Status()
output_template_type = OutputTemplateType()
output_field_type = OutputFieldType()
output_report_type = OutputReportType()


def get_input():
    """
    @summary: 获取 插件输入参数
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


def get_workspace():
    return params.get("bkWorkspace", None)


def get_test_version_flag():
    """
    @summary: 当前插件是否是测试版本标识
    """
    return params.get("testVersionFlag", None)


def get_sensitive_conf(key):
    confJson = params.get("bkSensitiveConfInfo", None)
    if confJson:
        return confJson.get(key, None)
    else:
        return None


def get_artifact_urls(file_src, file_path):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_artifacts_url(file_src, file_path)


def get_artifacts_properties(file_src, file_path):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_artifacts_properties(file_src, file_path)


def set_output(output):
    """
    @summary: 设置输出
    """
    setOutput = SetOutput()
    setOutput.set_output(output)


def upload_file(file_src, file_path, upload_url, params={}, headers={}, file_field="file"):
    """
    @summary: 上传构件到第三方平台
    """
    from .openapi import OpenApi
    client = OpenApi()

    result, download_url_list = get_artifact_urls(file_src, file_path)
    if not result:
        return False

    if len(download_url_list) > 1:
        log.error("found multiple files, confused")
        return False

    if len(download_url_list) == 0:
        log.error("can not find file, please check file_src & file_path")
        return False

    return client.upload_file(download_url_list[0], upload_url, params=params, headers=headers, file_field=file_field)


def download_file(file_src, file_path, file_name=None):
    """
    @summary: 从仓库下载构件到本地
    """
    from .openapi import OpenApi
    client = OpenApi()

    result, download_url_list = get_artifact_urls(file_src, file_path)
    if not result:
        return False

    if len(download_url_list) > 1:
        log.error("found multiple files, confused")
        return False

    return client.download_file(download_url_list[0], file_name)


if __name__ == "__main__":
    pass
