# -*- coding: utf-8 -*-

import os
import json
import traceback
import requests
import requests_toolbelt as rt

from . import setting
from .bklog import getLogger


class OpenApi():

    _log = getLogger()

    def __init__(self):
        sdk_json = self.get_sdk_json()

        self.gateway = sdk_json.get("gateway", None)
        self.header_auth = {
            setting.AUTH_HEADER_DEVOPS_BUILD_TYPE: sdk_json.get("buildType", None),
            setting.AUTH_HEADER_DEVOPS_PROJECT_ID: sdk_json.get("projectId", None),
            setting.AUTH_HEADER_DEVOPS_AGENT_ID: sdk_json.get("agentId", None),
            setting.AUTH_HEADER_DEVOPS_AGENT_SECRET_KEY: sdk_json.get("secretKey", None),
            setting.AUTH_HEADER_DEVOPS_BUILD_ID: sdk_json.get("buildId", None),
            setting.AUTH_HEADER_DEVOPS_VM_SEQ_ID: sdk_json.get("vmSeqId", None)
        }

        # 保存session增加3次重试
        self.session = requests.Session()
        self.session.trust_env = False
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)

    def get_sdk_json(self):
        """
        @summary：获取sdk配置
        """
        if not os.path.exists(setting.BK_SDK_JSON):
            self._log.error("[openapi]init error: sdk json do not exist")
            exit(-1)

        with open(setting.BK_SDK_JSON, 'r') as f:
            content = f.read()
        if not content:
            self._log.error("[openapi]init error: sdk json is null")
            exit(-1)

        try:
            sdk_json = json.loads(content)

            check_result, field = self.check_sdk_json(sdk_json)
            if not check_result:
                self._log.error("[openapi]check sdk json field error: {}".format(field))
                exit(-1)

            return sdk_json
        except:
            traceback.print_exc()
            self._log.error("[openapi]parse sdk json error")
            exit(-1)

    def check_sdk_json(self, src_json):
        """
        @summary：检查sdk配置
        """
        for field in setting.BK_SDK_JSON_FIELDS:
            if not src_json.get(field, None):
                return False, field

        return True, ""

    def generate_url(self, path):
        """
        @summary：组装访问openapi的url
        """
        return "http://{}/{}".format(self.gateway, path.lstrip("/"))

    def do_get(self, url, params=None):
        if params:
            r = self.session.get(url, headers=self.header_auth, params=params)
        else:
            r = self.session.get(url, headers=self.header_auth)

        if r.status_code == 200:
            try:
                ret = r.json()
                if ret["status"] != 0:
                    self._log.error("unexpected status: {}".format(r.text))
                    return False, {}

                return True, ret["data"]
            except:
                self._log.error("abnormal: {}".format(r.text))
                return False, {}
        else:
            self._log.error("unexpected status_code: {}" .format(r.text))
            return False, {}

    def get_artifacts_url(self, file_src, file_path):
        """
        @summary: 获取已归档构件的下载链接
        @param file_src：构件源 PIPELINE 从本次已归档构件中获取, CUSTOM_DIR 从自定义版本仓库中获取
        @param file_path: 构件的相对路径
        """
        path = "/artifactory/api/build/artifactories/thirdPartyDownloadUrl"
        params = {
            "artifactoryType": file_src,
            "path": file_path,
            "ttl": 3600*24
        }
        url = self.generate_url(path)
        return self.do_get(url, params=params)

    def get_artifacts_properties(self, file_src, file_path):
        """
        @summary: 获取已归档构件的元数据
        @param file_src：构件源 PIPELINE 从本次已归档构件中获取, CUSTOM_DIR 从自定义版本仓库中获取
        @param file_path: 构件的相对路径
        """
        path = "/artifactory/api/build/artifactories/getPropertiesByRegex"
        params = {
            "artifactoryType": file_src,
            "path": file_path
        }
        url = self.generate_url(path)
        return self.do_get(url, params=params)

    def download_file(self, file_url, file_name=None):
        """
        @summary: 下载文件到本地
        @param file_url: 下载链接
        @param file_name: 本地储存的文件名，选填
        @ret file_path_local: 下载后存储的本地路径
        """
        r = self.session.get(file_url, headers=self.header_auth)

        if r.status_code != 200:
            self._log.error("download file failed, status_code is {}".format(r.status_code))
            return False, r.status_code

        if not file_name:
            file_url_list = file_url.split("?", 1)
            file_name = os.path.basename(file_url_list[0])

        file_path_local = os.path.join(os.getenv(setting.BK_DATA_DIR, '.'), file_name)
        file_path_dir = os.path.dirname(file_path_local)
        if not os.path.exists(file_path_dir):
            os.makedirs(file_path_dir)

        with open(file_path_local, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)

        return True, file_path_local

    def upload_file(self, download_url, upload_url, params={}, headers={}, file_field="file"):
        """
        @summary: 从仓库获取构件，并推送到第三方系统
        """
        # self._log.info("upload_url: {}, params: {}, headers={}".format(upload_url, params, headers))

        result, filepath = self.download_file(download_url)
        if not result:
            return result

        fields = {
            file_field: (filepath, open(filepath, "rb").read())
        }
        fields.update(params)
        m = rt.MultipartEncoder(fields=fields)

        _headers = {
            "Content-Type": m.content_type,
            "accept": "application/json"
        }
        _headers.update(headers)

        response = requests.post(upload_url, data=m, headers=_headers)
        return response.json()

    def get_credential(self, credential_id):
        """
        @summary：根据凭据ID，获取凭据内容
        """

        path = "/ticket/api/build/credentials/{}/detail".format(credential_id)
        url = self.generate_url(path)
        return self.do_get(url)

    def get_commits(self):
        """
        @summary：获取当前构建下的代码变更记录
        """

        path = "/repository/api/build/commit/getCommitsByBuildId"
        url = self.generate_url(path)
        return self.do_get(url)

    def docker_push(self, userId, srcImageName, srcImageTag, repoAddress, namespace, targetImageName, targetImageTag, projectId, buildId, pipelineId, ticketId=None):
        """
        @summary: 从蓝盾仓库推送镜像到目标仓库
        @param userId：用户ID 必填
        @param srcImageName：源镜像名称 必填
        @param srcImageTag：源镜像tag 必填
        @param repoAddress：目标镜像仓库地址 必填
        @param namespace：目标命名空间 必填
        @param targetImageName：目的镜像名称 必填
        @param targetImageTag：目的镜像tag 必填
        @param projectId：项目ID 必填
        @param buildId：构建ID 必填
        @param pipelineId：流水线ID 必填

        @param ticketId：凭证ID 非必填
        """
        path = "/image/api/build/image/common/push"
        url = self.generate_url(path)

        params = {
            "userId": userId,
            "srcImageName": srcImageName,
            "srcImageTag": srcImageTag,
            "repoAddress": repoAddress,
            "namespace": namespace,
            "targetImageName": targetImageName,
            "targetImageTag": targetImageTag,
            "projectId": projectId,
            "buildId": buildId,
            "pipelineId": pipelineId
        }
        if ticketId:
            params["ticketId"] = ticketId

        headers = self.header_auth
        headers["Content-type"] = "application/json"

        r = self.session.post(url, headers=headers, data=json.dumps(params))

        if r.status_code == 200:
            try:
                ret = r.json()
                if ret["status"] != 0:
                    self._log.error("unexpected status: {}".format(r.text))
                    return False, {}

                return True, ret["data"]
            except:
                self._log.error("abnormal: {}".format(r.text))
                return False, {}
        else:
            self._log.error("unexpected status_code: {}" .format(r.text))
            return False, {}

    def get_docker_push_status(self, userId, taskId):
        """
        @summary 根据任务ID获取推送镜像进度
        """
        path = "/image/api/build/image/common/query?userId={}&taskId={}".format(userId, taskId)
        url = self.generate_url(path)
        return self.do_get(url)
