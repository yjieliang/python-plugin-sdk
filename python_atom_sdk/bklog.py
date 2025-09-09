# -*- coding: utf-8 -*-

import sys
import logging

# Python 2/3 兼容性处理
if sys.version_info[0] == 2:
    string_types = (str, unicode)
    text_type = unicode
    binary_type = str
else:
    string_types = (str,)
    text_type = str
    binary_type = bytes

LOG_NAME = "ATOM_LOG"
LOG_FORMAT = "%(bk_ci_placeholder)s%(message)s"
LOG_LEVEL = logging.DEBUG
BK_CI_PLACEHOLDER = "BK_CI_PLACEHOLDER"


def get_logger():
    """
    兼容老版本的方法
    """
    return BkLogger().logger


class MyLoggerAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs["extra"] = self.extra
        return msg, kwargs


class ContextFilter(logging.Filter):

    def filter(self, record):
        bk_ci_placeholder = ""
        if hasattr(record, "bk_ci_placeholder") and record.bk_ci_placeholder != BK_CI_PLACEHOLDER:
            bk_ci_placeholder = record.bk_ci_placeholder
        else:
            bk_ci_placeholder = record.levelname.lower()
        record.bk_ci_placeholder = "##[{}]".format(bk_ci_placeholder)
        return True


class BkLogger():

    def __init__(self):
        init_logger = logging.getLogger(LOG_NAME)
        if init_logger.handlers:
            self.logger = init_logger
        else:
            init_logger.setLevel(LOG_LEVEL)
            formatter = logging.Formatter(LOG_FORMAT)
            filter = ContextFilter()

            console = logging.StreamHandler(sys.stdout)
            console.setFormatter(formatter)
            console.addFilter(filter)

            init_logger.addHandler(console)

            extra_dict = {"bk_ci_placeholder": BK_CI_PLACEHOLDER}
            self.logger = MyLoggerAdapter(init_logger, extra_dict)

    def _safe_log(self, log_func, msg, *args, **kwargs):
        """
        安全的日志记录方法，乐观模式：先尝试正常记录，出错时进行安全处理
        """
        try:
            # 乐观模式：先尝试格式化测试，如果成功则正常记录
            if args:
                # 预先测试格式化是否会出错
                try:
                    test_msg = msg % args
                    # 格式化成功，正常记录
                    log_func(msg, *args, **kwargs)
                except:
                    # 格式化失败，抛出异常让下面的except处理
                    raise ValueError("Message formatting failed")
            else:
                log_func(msg, **kwargs)
        except Exception as e:
            # 出现异常时，使用安全方式记录
            self._handle_safe_logging_exception(log_func, msg, args, kwargs, e)
    
    def _handle_safe_logging_exception(self, log_func, msg, args, kwargs, error):
        """
        处理日志记录异常的安全方法
        """
        try:
            # 安全地转换消息和参数
            safe_msg = self._make_safe_string(msg)
            safe_args = [self._make_safe_string(arg) for arg in args] if args else []
            
            # 记录错误信息
            error_msg = "[日志异常] {0}".format(str(error))
            log_func(error_msg, **kwargs)
            
            # 记录原始消息的安全版本
            if safe_args:
                processed_msg = "[已处理] {0} | 参数: {1}".format(safe_msg, ', '.join(map(str, safe_args)))
            else:
                processed_msg = "[已处理] {0}".format(safe_msg)
            log_func(processed_msg, **kwargs)
            
        except Exception:
            # 最后的保险措施
            try:
                # 直接使用底层logger记录
                level_name = log_func.__name__.upper()
                print("##[{0}][严重日志异常] 无法记录消息: {1}".format(level_name.lower(), str(error)))
            except:
                pass
    
    def _make_safe_string(self, obj):
        """
        将对象转换为安全的字符串格式
        """
        if obj is None:
            return "None"
        
        try:
            # Python 2/3 兼容的字符串类型检查
            if isinstance(obj, string_types):
                # 在Python 2中，如果是str类型，尝试解码为unicode
                if sys.version_info[0] == 2 and isinstance(obj, str):
                    try:
                        return obj.decode('utf-8')
                    except UnicodeDecodeError:
                        return obj.decode('utf-8', errors='replace')
                return obj
            elif isinstance(obj, binary_type):
                # 尝试多种编码方式解码
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                    try:
                        return obj.decode(encoding)
                    except (UnicodeDecodeError, LookupError):
                        continue
                # 如果所有编码都失败，使用错误处理方式
                return obj.decode('utf-8', errors='replace')
            else:
                # 对于其他类型，转换为字符串
                return text_type(obj)
        except Exception:
            # 如果转换失败，返回类型信息和repr
            try:
                return "<{0}: {1}>".format(type(obj).__name__, repr(obj))
            except:
                return "<{0}: 无法显示内容>".format(type(obj).__name__)





    def debug(self, msg, *args, **kwargs):
        self._safe_log(self.logger.debug, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._safe_log(self.logger.info, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._safe_log(self.logger.warning, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._safe_log(self.logger.error, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._safe_log(self.logger.critical, msg, *args, **kwargs)

    def command(self, command):
        self._safe_log(self.logger.info, command, extra={"bk_ci_placeholder": "command"})

    def group_start(self, msg):
        self._safe_log(self.logger.info, msg, extra={"bk_ci_placeholder": "group"})

    def group_end(self):
        self.logger.info("", extra={"bk_ci_placeholder": "endgroup"})


if __name__ == '__main__':

    obj = BkLogger()
    obj.group_start("group1 start")
    obj.info("info is info")
    obj.debug("debug is debug")
    obj.warning("warning is warning")
    obj.error("error is error")
    obj.command("this is a command")
    obj.group_end()
