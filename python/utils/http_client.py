"""
通用HTTP请求处理模块

为视频搜索系统提供统一的HTTP请求服务，包括：
- 异步HTTP请求处理（基于httpx）
- 完整的请求日志记录（开始/成功/超时/错误）
- 统一的异常处理和响应格式
- 请求参数构建工具
- 预配置的HTTP请求头

主要类：
- RequestContext: 请求上下文，封装日志记录功能
- HttpClient: HTTP客户端，提供统一的请求接口

"""

import time
import httpx
import json
from typing import Dict, Any, Optional

from utils.logger import RequestLogger, setup_logging
from settings import Config


class RequestContext:
    """
    HTTP请求上下文管理器

    封装单个HTTP请求的生命周期管理，包括：
    - 请求开始时间记录
    - 请求ID生成和管理
    - 日志记录的统一接口
    - 请求耗时计算

    用于在HttpClient中简化日志记录代码，提供一致的请求追踪体验
    """

    def __init__(self, request_logger: RequestLogger, site_name: str):
        """
        初始化请求上下文

        Args:
            request_logger: 请求日志记录器实例，已配置好site_name
            site_name: 资源站点名称
        """
        self.request_logger = request_logger
        self.site_name = site_name
        self.start_time = time.perf_counter()
        self.request_id = None

    def log_start(self, url: str, params: Dict[str, Any], headers: Dict[str, str]):
        """
        记录HTTP请求开始

        Args:
            url: 请求URL
            params: HTTP请求参数字典
            headers: HTTP请求头字典

        Note:
            会生成唯一的request_id用于后续日志关联
        """
        self.request_id = self.request_logger.log_request_start(
            url=url,
            params=params,
        )

    def log_success(self, status_code: int, response_size: int, data_count: int):
        """
        记录HTTP请求成功

        Args:
            status_code: HTTP响应状态码
            response_size: 响应内容大小（字节）
            data_count: 返回的数据项数量（用于统计）

        Returns:
            int: 请求耗时（毫秒）
        """
        elapsed_ms = self._calculate_elapsed_ms()
        self.request_logger.log_request_success(
            request_id=self.request_id,
            status_code=status_code,
            elapsed_ms=elapsed_ms,
            data_count=data_count,
        )
        return elapsed_ms

    def log_timeout(self, timeout: int):
        """
        记录HTTP请求超时

        Args:
            timeout: 超时时间设置（秒）

        Returns:
            int: 请求耗时（毫秒）
        """
        elapsed_ms = self._calculate_elapsed_ms()
        self.request_logger.log_request_timeout(
            request_id=self.request_id,
            timeout=timeout,
            elapsed_ms=elapsed_ms,
        )
        return elapsed_ms

    def log_error(self, error: str, status_code: Optional[int] = None):
        """
        记录HTTP请求错误

        Args:
            error: 错误信息描述
            status_code: HTTP状态码（如果有的话）

        Returns:
            int: 请求耗时（毫秒）
        """
        elapsed_ms = self._calculate_elapsed_ms()
        self.request_logger.log_request_error(
            request_id=self.request_id,
            error=error,
            elapsed_ms=elapsed_ms,
            status_code=status_code,
        )
        return elapsed_ms

    def _calculate_elapsed_ms(self) -> int:
        """
        计算从请求开始到现在的耗时

        Returns:
            int: 耗时（毫秒）
        """
        return int((time.perf_counter() - self.start_time) * 1000)


class HttpClient:
    """
    简化的HTTP客户端类，专门用于视频搜索API

    提供统一的HTTP请求接口和日志记录功能，支持：
    - 异步HTTP请求（使用httpx）
    - 统一的请求/响应日志记录
    - 异常处理和错误日志
    - 超时处理

    使用场景：
    - 视频搜索服务中的资源站点请求
    - 资源管理器中的连接测试
    """

    def __init__(self):
        """
        初始化HTTP客户端

        创建请求日志记录器实例，用于记录所有HTTP请求的详细信息
        """
        # 使用通用的日志记录器，在具体请求时会创建带site信息的记录器
        self.request_logger = setup_logging()

    async def request_with_logging(
        self,
        client: httpx.AsyncClient,
        site_id: str,
        site_name: str,
        url: str,
        params: Dict[str, Any],
        headers: Dict[str, str],
        timeout: int = 15,
    ) -> Dict[str, Any]:
        """
        发送HTTP请求并记录详细日志

        Args:
            client: httpx异步客户端实例
            site_id: 资源站点ID，用于日志标识和错误追踪
            site_name: 资源站点名称，用于日志显示
            url: 请求的目标URL
            params: HTTP请求参数字典
            headers: HTTP请求头字典
            timeout: 请求超时时间（秒）

        Returns:
            Dict[str, Any]: 包含响应数据和元信息的字典，格式：
                {
                    "success": bool,
                    "data": Any,  # 响应数据，success=True时有效
                    "error": str,  # 错误信息，success=False时有效
                    "status_code": int,  # HTTP状态码
                    "elapsed_ms": int,  # 请求耗时（毫秒）
                    "response_size": int  # 响应大小（字节）
                }

        Raises:
            无直接异常抛出，所有异常都被捕获并在返回值中体现
        """
        # 创建带有site信息的请求日志记录器
        site_logger = RequestLogger(site_name=site_name)

        # 使用RequestContext记录请求上下文
        context = RequestContext(site_logger, site_name)
        context.log_start(url, params, headers)

        try:
            # 发送HTTP请求
            response = await client.get(
                url, params=params, headers=headers, timeout=timeout
            )
            response_text = response.text
            response_size = len(response_text.encode("utf-8"))

            # 解析JSON响应
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # JSON解析失败，记录错误并返回失败结果
                elapsed_ms = context.log_error(f"JSON解析失败: {str(e)}")
                return {
                    "success": False,
                    "error": f"JSON解析失败: {str(e)}",
                    "status_code": response.status_code,
                    "elapsed_ms": elapsed_ms,
                    "response_size": response_size,
                }

            # 记录成功日志
            elapsed_ms = context.log_success(response.status_code, response_size, 0)

            return {
                "success": True,
                "data": response_data,  # 返回解析后的JSON对象而不是字符串
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
                "response_size": response_size,
            }

        except httpx.TimeoutException:
            # 处理超时异常
            elapsed_ms = context.log_timeout(timeout)
            return {
                "success": False,
                "error": f"请求超时 ({timeout}s)",
                "status_code": None,
                "elapsed_ms": elapsed_ms,
                "response_size": 0,
            }

        except httpx.HTTPStatusError as e:
            # 处理HTTP状态错误
            elapsed_ms = context.log_error(
                f"HTTP错误: {e.response.status_code}", e.response.status_code
            )
            return {
                "success": False,
                "error": f"HTTP错误: {e.response.status_code}",
                "status_code": e.response.status_code,
                "elapsed_ms": elapsed_ms,
                "response_size": 0,
            }

        except Exception as e:
            # 处理其他异常
            elapsed_ms = context.log_error(f"网络错误: {str(e)}")
            return {
                "success": False,
                "error": f"网络错误: {str(e)}",
                "status_code": None,
                "elapsed_ms": elapsed_ms,
                "response_size": 0,
            }

    def build_params(
        self,
        param_mapping: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        构建HTTP请求参数字典

        将参数映射转换为有效的请求参数，自动过滤掉None值，
        避免向API发送无效参数。

        Args:
            param_mapping: 参数映射字典 {参数名: 参数值}
                          例如: {"wd": "喜羊羊", "pg": 1, "ac": "detail"}

        Returns:
            dict: 过滤后的请求参数字典，不包含None值

        Example:
            >>> client = HttpClient()
            >>> params = client.build_params({
            ...     "wd": "电影",
            ...     "pg": 1,
            ...     "unused": None
            ... })
            >>> print(params)
            {"wd": "电影", "pg": 1}
        """
        return {k: v for k, v in param_mapping.items() if v is not None}


# ==================== HTTP请求头配置 ====================

# 搜索请求头：用于视频搜索API请求
# 模拟浏览器请求，提高API兼容性和成功率
SEARCH_HEADERS = {
    "Accept": "application/json",  # 明确请求JSON格式响应
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",  # 模拟Edge浏览器
}

# 测试请求头：用于资源站连接测试
# 使用真实浏览器User-Agent，避免被识别为爬虫
TEST_HEADERS = Config.RESOURCE_AUTH_CONFIG["test_headers"]
