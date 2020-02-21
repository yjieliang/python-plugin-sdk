# -*- coding: utf-8 -*-

from .bklog import logger, getLogger
from .input import ParseParams
from .output import SetOutput
from .const import Status, OutputTemplateType, OutputFieldType, OutputReportType

log = logger()
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


def get_pipeline_creator():
    return params.get("BK_CI_PIPELINE_CREATE_USER", None)


def get_pipeline_modifier():
    return params.get("BK_CI_PIPELINE_UPDATE_USER", None)


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


def get_artifact_urls(file_src, file_path, projectId=None, pipelineId=None, buildNo=None):
    if projectId and not pipelineId:
        return False, "pipelineId is null"
    if pipelineId and not projectId:
        return False, "projectId is null"
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_artifacts_url(file_src, file_path, projectId=projectId, pipelineId=pipelineId, buildNo=buildNo)


def get_artifacts_properties(file_src, file_path, projectId=None, pipelineId=None, buildNo=None):
    if projectId and not pipelineId:
        return False, "pipelineId is null"
    if pipelineId and not projectId:
        return False, "projectId is null"
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_artifacts_properties(file_src, file_path, projectId=projectId, pipelineId=pipelineId,
                                           buildNo=buildNo)


def set_output(output):
    """
    @summary: 设置输出
    """
    setOutput = SetOutput()
    setOutput.set_output(output)


def upload_file(file_src, file_path, upload_url, params={}, headers={}, file_field="file", timeout=300):
    """
    @summary: 上传构件到第三方平台
    """
    from .openapi import OpenApi
    client = OpenApi()

    result, download_url_list = get_artifact_urls(file_src, file_path)
    if not result:
        return False, download_url_list

    if len(download_url_list) > 1:
        log.error("found multiple files, confused")
        return False, "found multiple files, confused"

    if len(download_url_list) == 0:
        log.error("can not find file, please check file_src & file_path")
        return False, "can not find file, please check file_src & file_path"

    return client.upload_file(download_url_list[0], upload_url, params=params, headers=headers, file_field=file_field,
                              timeout=timeout)


def download_file(file_src, file_path, file_name=None, projectId=None, pipelineId=None, buildNo=None):
    """
    @summary: 从仓库下载构件到本地
    """
    from .openapi import OpenApi
    client = OpenApi()

    result, download_url_list = get_artifact_urls(file_src, file_path, projectId=projectId, pipelineId=pipelineId,
                                                  buildNo=buildNo)
    if not result:
        return False, download_url_list

    if len(download_url_list) > 1:
        log.error("found multiple files, confused")
        return False, "found multiple files, confused"
    elif len(download_url_list) == 0:
        log.error("can not find file: {}, {}".format(file_src, file_path))
        return False, "can not find file: {}, {}".format(file_src, file_path)

    return client.download_file(download_url_list[0], file_name)


def get_credential(credential_id):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_credential(credential_id)


def get_commits():
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_commits()


def docker_push(userId, srcImageName, srcImageTag, repoAddress, namespace, targetImageName, targetImageTag,
                ticketId=None):
    projectId = get_project_name()
    buildId = get_pipeline_build_id()
    pipelineId = get_pipeline_id()

    from .openapi import OpenApi
    client = OpenApi()
    return client.docker_push(userId, srcImageName, srcImageTag, repoAddress, namespace, targetImageName,
                              targetImageTag, projectId, buildId, pipelineId, ticketId=ticketId)


def get_docker_push_status(userId, taskId):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_docker_push_status(userId, taskId)


def get_repo_info(identity, identity_type):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_repo_info(identity, identity_type)


def get_git_oauth(userId):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_git_oauth(userId)


def send_rtx_notify(receivers, title, body):
    from .openapi import OpenApi
    client = OpenApi()
    return client.send_rtx_notify(receivers, title, body)


def send_wechat_notify(receivers, body):
    from .openapi import OpenApi
    client = OpenApi()
    return client.send_wechat_notify(receivers, body)


def send_email_notify(receivers, title, body, cc=[], content_format="TEXT"):
    from .openapi import OpenApi
    client = OpenApi()
    return client.send_email_notify(receivers, title, body, cc, content_format)


# ipt专用
def get_commit_build_artifactory_info(pipeline_id, user_id, commit_id, file_path):
    from .openapi import OpenApi
    client = OpenApi()
    return client.get_commit_build_artifactory_info(pipeline_id, user_id, commit_id, file_path)


def set_properties(file_src, file_path, properties):
    from .openapi import OpenApi
    client = OpenApi()
    if str(file_src) == "PIPELINE":
        file_path = "/"+get_pipeline_id()+"/"+get_pipeline_build_id()+"/"+str(file_path).replace("/", "", 1)
    elif str(file_src) == "CUSTOM_DIR":
        file_path = "/"+str(file_path).replace("/", "", 1)
    return client.set_properties(file_src, file_path, properties)


if __name__ == "__main__":
    pass
