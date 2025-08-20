"""
日志工具模块

提供统一的日志配置和工具函数，支持简洁的日志记录
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class SimpleFormatter(logging.Formatter):
    """简洁格式化器，用于控制台输出"""

    def format(self, record):
        # 简洁的时间格式
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # 基础消息
        message = f"{timestamp} [{record.levelname}] {record.getMessage()}"

        # 添加关键信息
        if hasattr(record, "elapsed_ms"):
            message += f" ({record.elapsed_ms}ms)"
        if hasattr(record, "status_code"):
            message += f" [{record.status_code}]"
        if hasattr(record, "error"):
            message += f" - {record.error}"

        # 添加URL信息（仅在请求开始时显示）
        if hasattr(record, "url") and "请求" in record.getMessage():
            message += f"\n    URL: {record.url}"

        return message


class JSONFormatter(logging.Formatter):
    """简化的JSON格式化器，用于文件输出"""

    def format(self, record):
        log_entry = {
            "time": datetime.fromtimestamp(record.created).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # 重命名部分字段以符合JSON输出规范
        if hasattr(record, "site_name"):
            log_entry["site"] = record.site_name
        if hasattr(record, "status_code"):
            log_entry["status"] = record.status_code

        # 直接添加其他字段
        for key in ["request_id", "elapsed_ms", "error", "url"]:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class RequestLogger:
    """HTTP请求日志记录器"""

    def __init__(
        self,
        site_name: str = "",
        logger_name: str = "video_search.requests",
    ):
        self.logger = logging.getLogger(logger_name)
        self.site_name = site_name

    def log_request_start(
        self,
        url: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> str:
        """记录请求开始，包含完整URL信息"""
        if not request_id:
            request_id = str(uuid.uuid4())[:8]

        # 构建完整的请求URL（内联原_build_full_url逻辑）
        full_url = url
        if params:
            # 构建查询字符串
            query_parts = []
            for key, value in params.items():
                if value is not None:
                    query_parts.append(f"{key}={value}")
            if query_parts:
                full_url = f"{url}?{'&'.join(query_parts)}"

        self.logger.info(
            f"请求 {self.site_name}",
            extra={
                "request_id": request_id,
                "site_name": self.site_name,
                "url": full_url,
            },
        )
        return request_id

    def log_request_success(
        self,
        request_id: str,
        status_code: int,
        elapsed_ms: int,
        data_count: int = 0,
    ):
        """记录请求成功"""
        # 简化消息格式
        message = f"{self.site_name} 请求成功"
        if data_count > 0:
            message += f" (获取{data_count}条数据)"

        self.logger.info(
            message,
            extra={
                "request_id": request_id,
                "site_name": self.site_name,
                "status_code": status_code,
                "elapsed_ms": elapsed_ms,
            },
        )

    def log_request_error(
        self,
        request_id: str,
        error: str,
        elapsed_ms: int,
        status_code: Optional[int] = None,
    ):
        """记录请求错误"""
        self.logger.error(
            f"{self.site_name} 请求失败",
            extra={
                "request_id": request_id,
                "site_name": self.site_name,
                "error": error,
                "elapsed_ms": elapsed_ms,
                "status_code": status_code,
            },
        )

    def log_request_timeout(
        self,
        request_id: str,
        timeout: int,
        elapsed_ms: int,
    ):
        """记录请求超时"""
        self.logger.warning(
            f"{self.site_name} 请求超时",
            extra={
                "request_id": request_id,
                "site_name": self.site_name,
                "error": f"timeout({timeout}s)",
                "elapsed_ms": elapsed_ms,
            },
        )


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    json_format: bool = True,
    third_party_log_levels: Optional[Dict[str, str]] = None,
) -> None:
    """
    配置应用日志系统

    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        max_file_size: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
        enable_console: 是否启用控制台输出（使用简洁格式）
        json_format: 是否使用JSON格式（仅影响文件输出）
        third_party_log_levels: 第三方库日志级别配置，格式为 {"库名": "级别"}
    """
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 控制台处理器 - 始终使用简洁格式
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(SimpleFormatter())
        root_logger.addHandler(console_handler)

    # 文件处理器 - 根据配置选择格式
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count, encoding="utf-8"
        )

        # 文件使用JSON格式或简洁格式
        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(SimpleFormatter())

        root_logger.addHandler(file_handler)

    # 设置第三方库日志级别，减少噪音
    default_third_party_levels = {
        "werkzeug": "WARNING",
        "httpx": "WARNING",
        "urllib3": "WARNING",
    }

    # 合并用户配置的第三方库日志级别
    if third_party_log_levels:
        default_third_party_levels.update(third_party_log_levels)

    for library, level in default_third_party_levels.items():
        logging.getLogger(library).setLevel(getattr(logging, level.upper()))
