# -*- coding: utf-8 -*-
import os
import traceback
import json
import requests
import requests_toolbelt as rt

from . import setting
from .bklog import BkLogger


class OpenApi():
    _log = BkLogger()

    def __init__(self):
        sdk_json = self.get_sdk_json()
        # self._log.info(sdk_json)

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
        sdk_path = os.path.join(os.environ.get(setting.BK_DATA_DIR, None), setting.BK_SDK_JSON)
        if not os.path.exists(sdk_path):
            self._log.error("[openapi]init error: sdk json do not exist")
            exit(-1)

        with open(sdk_path, 'r') as f_sdk:
            content = f_sdk.read()
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
        except TypeError as _e:
            self._log.error("[openapi]parse sdk json error: type error, sdk.json is {}" .format(content))
            exit(-1)
        else:
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
        if self.gateway.startswith("http://") or self.gateway.startswith("https://"):
            return "{}/{}".format(self.gateway, path.lstrip("/"))
        else:
            return "http://{}/{}".format(self.gateway, path.lstrip("/"))

    def do_get(self, url, params=None, timeout=60):
        # self._log.debug(url)
        if params:
            res = self.session.get(url, headers=self.header_auth, params=params, timeout=timeout)
        else:
            res = self.session.get(url, headers=self.header_auth, timeout=timeout)

        try:
            content = res.text.encode("utf-8")
        except AttributeError as _e:
            content = res.text
        else:
            content = res.text

        # self._log.debug(r.status_code)
        # self._log.debug(content)
        if res.status_code == 200:
            try:
                ret = res.json()
                if ret["status"] != 0:
                    self._log.error("unexpected status: {}".format(content))
                    return False, {}

                return True, ret["data"]
            except TimeoutError as _e:
                self._log.error("timeout error")
                return False, {}
            else:
                self._log.error("abnormal: {}".format(content))
                return False, {}
        else:
            self._log.error("unexpected status_code: {}".format(content))
            return False, {}

    def do_post(self, url, header=None, message=None, timeout=120):
        for key, val in header.items():
            self.header_auth[key] = val

        with self.session as session:
            if message:
                res = session.post(url, headers=self.header_auth, data=json.dumps(message), timeout=timeout)
            else:
                res = session.post(url, headers=self.header_auth, timeout=timeout)

            try:
                content = res.text.encode("utf-8")
            except AttributeError as _e:
                content = res.text
            else:
                content = res.text

            if res.status_code == 200:
                try:
                    ret = res.json()
                    if ret["status"] != 0:
                        self._log.error("unexpected status: {}".format(ret["message"]))
                        return False, {}

                    return True, ret["data"]
                except TimeoutError as _e:
                    self._log.error("timeout error")
                    return False, {}
                else:
                    self._log.error("abnormal: {}".format(content))
                    return False, {}
            else:
                self._log.error(res.status_code)
                self._log.error("unexpected message: {}".format(res.json()["message"]))
                return False, {}

    def get_artifacts_url(self, file_src, file_path, project_id=None, pipeline_id=None, build_no=None):
        """
        @summary: 获取已归档构件的下载链接
        @param file_src：构件源 PIPELINE 从本次已归档构件中获取, CUSTOM_DIR 从自定义版本仓库中获取
        @param file_path: 构件的相对路径
        """
        path = "/artifactory/api/build/artifactories/thirdPartyDownloadUrl"
        params = {
            "artifactoryType": file_src,
            "path": file_path,
            "ttl": 3600 * 24
        }
        if project_id:
            params["projectId"] = project_id
        if pipeline_id:
            params["pipelineId"] = pipeline_id
        if project_id and pipeline_id:
            if build_no:
                params["buildNo"] = build_no
            else:
                params["buildNo"] = "-1"  # 最近一次构建
        url = self.generate_url(path)
        # self._log.debug(url)
        # self._log.debug(params)
        return self.do_get(url, params=params)

    def get_artifacts_properties(self, file_src, file_path, project_id=None, pipeline_id=None, build_no=None):
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
        if project_id:
            params["projectId"] = project_id
        if pipeline_id:
            params["pipelineId"] = pipeline_id
        if project_id and pipeline_id:
            if build_no:
                params["buildNo"] = build_no
            else:
                params["buildNo"] = "-1"
        url = self.generate_url(path)
        # self._log.debug(url)
        # self._log.debug(params)
        return self.do_get(url, params=params)

    def download_file(self, file_url, file_name=None):
        """
        @summary: 下载文件到本地
        @param file_url: 下载链接
        @param file_name: 本地储存的文件名，选填
        @ret file_path_local: 下载后存储的本地路径
        """
        res = self.session.get(file_url, headers=self.header_auth, stream=True)

        if res.status_code != 200:
            self._log.error("download file failed, status_code is {}".format(r.status_code))
            return False, res.status_code

        if not file_name:
            file_url_list = file_url.split("?", 1)
            file_name = os.path.basename(file_url_list[0])

        file_path_local = os.path.join(os.getenv(setting.BK_DATA_DIR, '.'), file_name)
        file_path_dir = os.path.dirname(file_path_local)
        if not os.path.exists(file_path_dir):
            os.makedirs(file_path_dir)

        with open(file_path_local, 'wb') as f_file:
            for chunk in res.iter_content(chunk_size=512):
                if chunk:
                    f_file.write(chunk)

        return True, file_path_local

    def upload_file(self, download_url, upload_url, params=None, headers=None, file_field="file", timeout=300):
        """
        @summary: 从仓库获取构件，并推送到第三方系统
        """
        # self._log.info("upload_url: {}, params: {}, headers={}".format(upload_url, params, headers))

        result, filepath = self.download_file(download_url)
        if not result:
            return result

        fields = {
            file_field: (filepath, open(filepath, "rb"), "text/plain")
        }
        fields.update(params)
        multipart_encoder = rt.MultipartEncoder(fields=fields)

        _headers = {
            "Content-Type": multipart_encoder.content_type,
            "accept": "application/json"
        }
        _headers.update(headers)

        response = requests.post(upload_url, data=multipart_encoder, headers=_headers, timeout=timeout)
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

    def docker_push(self, user_id, src_image_name, src_image_tag, repo_address, namespace, target_image_name, 
                    target_image_tag, project_id, build_id, pipeline_id, ticket_id=None):
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
            "userId": user_id,
            "srcImageName": src_image_name,
            "srcImageTag": src_image_tag,
            "repoAddress": repo_address,
            "namespace": namespace,
            "targetImageName": target_image_name,
            "targetImageTag": target_image_tag,
            "projectId": project_id,
            "buildId": build_id,
            "pipelineId": pipeline_id
        }
        if ticket_id:
            params["ticketId"] = ticket_id

        headers = self.header_auth
        headers["Content-type"] = "application/json"

        res = self.session.post(url, headers=headers, data=json.dumps(params))

        try:
            content = res.text.encode("utf-8")
        except AttributeError as _e:
            content = res.text
        else:
            content = res.text

        if res.status_code == 200:
            try:
                ret = res.json()
                if ret["status"] != 0:
                    self._log.error("unexpected status: {}".format(content))
                    return False, {}

                return True, ret["data"]
            except TypeError as _e:
                self._log.error("abnormal: {}".format(content))
                return False, {}
            else:
                self._log.error("abnormal: {}".format(content))
                return False, {}
        else:
            self._log.error("unexpected status_code: {}".format(content))
            return False, {}

    def get_docker_push_status(self, user_id, task_id):
        """
        @summary：根据任务ID获取推送镜像进度
        """
        path = "/image/api/build/image/common/query?userId={}&taskId={}".format(user_id, task_id)
        url = self.generate_url(path)
        return self.do_get(url)

    def get_repo_info(self, identity, identity_type):
        """
        @summary：根据代码库别名，获取代码库详细地址
        """
        path = "/repository/api/build/repositories/"
        params = {
            "repositoryId": identity,
            "repositoryType": identity_type
        }
        url = self.generate_url(path)

        return self.do_get(url, params=params)

    def get_git_oauth(self, user_id):
        """
        @summary：获取工蜂OAUTH信息
        """
        path = "/repository/api/build/oauth/git/{}".format(user_id)

        url = self.generate_url(path)

        return self.do_get(url)

    def send_rtx_notify(self, receivers, title, body):
        """
        @summary：发送企业微信通知
        :param receivers: 接收人集合
        :param body: 通知内容
        :param title: 通知标题
        :return:
        """
        path = "/notify/api/build/notifies/rtx"

        header = {
            "Content-type": "application/json"
        }

        message = {
            "receivers": receivers, "body": body, "sender": "", "title": title, "priority": "-1",
            "source": 0
        }
        url = self.generate_url(path)
        ret, _msg = self.do_post(url, header, message)

        return ret

    def send_wechat_notify(self, receivers, body):
        """
        @summary：发送微信通知
        :param receivers: 接收人集合
        :param body: 通知内容
        :return:
        """
        path = "/notify/api/build/notifies/wechat"

        header = {
            "Content-type": "application/json"
        }

        message = {
            "receivers": receivers, "body": body
        }
        url = self.generate_url(path)
        ret, _msg = self.do_post(url, header, message)

        return ret

    def send_email_notify(self, receivers, title, body, ccs=None, content_format="TEXT"):
        """
        @summary：发送邮件通知
        :param receivers: 接收人集合
        :param cc: 抄送人集合
        :param body: 通知内容
        :param title: 通知标题
        :param content_format: TEXT普通文本  HTML html
        :return:
        """
        path = "/notify/api/build/notifies/email"

        header = {
            "Content-type": "application/json"
        }

        _format = {
            "TEXT": 0,
            "HTML": 1
        }
        if not ccs:
            ccs = []

        message = {
            "receivers": receivers, "cc": ccs, "title": title, "body": body, "format": _format[content_format]
        }
        url = self.generate_url(path)
        ret, _msg = self.do_post(url, header, message)

        return ret

    def get_commit_build_artifactory_info(self, pipeline_id, user_id, commit_id, file_path):
        path = "/process/api/build/ipt/repo/pipeline/{}/commit/{}/artifactorytInfo?userId={}"\
            .format(pipeline_id, commit_id, user_id)
        if file_path:
            path = path + "&filePath=" + file_path
        url = self.generate_url(path)
        return self.do_get(url)

    def set_properties(self, file_src, file_path, properties):
        """
        @summary: 设置归档文件元数据
        :param file_src：构件源 PIPELINE 从本次已归档构件中获取, CUSTOM_DIR 从自定义版本仓库中获取
        :param file_path: 构件的相对路径
        :param properties: 新设置的元数据，map类型
        """
        path = "artifactory/api/build/artifactories/properties?artifactoryType={}&path={}"\
            .format(file_src, file_path)
        url = self.generate_url(path)

        header = {
            "Content-type": "application/json"
        }

        ret, _msg = self.do_post(url, header, properties)
        return ret
