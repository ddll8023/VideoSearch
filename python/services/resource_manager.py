"""
资源站管理器

负责管理多个视频资源站的配置信息，提供统一的站点管理接口。
主要功能包括：站点信息获取、状态切换、连接测试、站点验证等。
"""

import httpx
import asyncio
import random
from config.resource_config import ResourceConfig, ResourceSiteConfig
import logging
from utils.http_client import HttpClient, TEST_HEADERS
from settings import Config


class ResourceManager:
    """
    资源站配置管理器

    统一管理视频资源站点的配置信息和状态，为视频搜索系统提供
    站点管理功能。支持站点启用/禁用、连接测试、配置验证等操作。

    使用场景：
    - API接口中的站点信息查询
    - 视频搜索前的站点验证
    - 系统设置中的站点管理
    """

    def __init__(self, config_file: str | None = None):
        """
        初始化资源站管理器

        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        # 初始化配置管理器，负责从文件加载站点配置
        self.resource_config = ResourceConfig(config_file)
        # 初始化HTTP客户端，用于站点连接测试
        self.http_client = HttpClient()
        # 创建专用日志记录器
        self.logger = logging.getLogger("video_search.resource_manager")

    def get_sites_info(self) -> list[dict]:
        """
        获取所有资源站信息

        将ResourceSiteConfig对象转换为字典格式，便于API响应和前端展示。
        返回所有站点信息（包括禁用的），前端根据enabled字段判断状态。

        Returns:
            资源站信息列表，每个元素包含：site_id, name, base_url, enabled, timeout
        """
        return [
            {
                "site_id": site.site_id,  # 站点唯一标识
                "name": site.name,  # 站点显示名称
                "base_url": site.base_url,  # 站点API地址
                "enabled": site.enabled,  # 启用状态
                "timeout": site.timeout,  # 请求超时时间
            }
            for site in self.resource_config.sites.values()
        ]

    def get_stats(self) -> dict[str, int]:
        """
        获取资源站统计信息

        计算并返回站点的基础统计数据，用于系统监控和前端展示。

        Returns:
            统计信息字典，包含：total_sites（总数）, enabled_sites（已启用数量）
        """
        # 统计已启用的站点数量
        enabled_count = sum(
            1 for site in self.resource_config.sites.values() if site.enabled
        )
        return {
            "total_sites": len(self.resource_config.sites),  # 站点总数
            "enabled_sites": enabled_count,  # 已启用站点数
        }

    def validate_site(
        self, site_id: str
    ) -> tuple[bool, str, ResourceSiteConfig | None]:
        """
        验证站点是否存在且可用

        在执行视频搜索前验证目标站点的有效性，确保只对可用的站点发起请求。
        验证规则：站点ID非空 -> 站点存在 -> 站点已启用

        Args:
            site_id: 资源站ID

        Returns:
            三元组：(是否有效, 错误消息, 站点配置对象)
            - 如果验证通过，返回 (True, "", site_config)
            - 如果验证失败，返回 (False, error_message, None)
        """
        # 第一层验证：检查站点ID是否有效
        if not site_id:
            return False, "资源站ID不能为空", None

        # 第二层验证：检查站点是否存在
        site = self.resource_config.get_site(site_id)
        if not site:
            return False, f"资源站 {site_id} 不存在", None

        # 第三层验证：检查站点是否已启用
        if not site.enabled:
            return False, f"资源站 {site.name} 已禁用", None

        # 所有验证通过
        return True, "", site

    def toggle_site_status(self, site_id: str) -> bool:
        """
        切换资源站启用状态

        用于系统设置页面的站点启用/禁用功能。状态切换后会立即保存到配置文件，
        确保重启后配置不丢失。

        Args:
            site_id: 资源站ID

        Returns:
            新的启用状态 (True: 已启用, False: 已禁用)

        Raises:
            ValueError: 当站点不存在时抛出异常
        """
        # 验证站点是否存在（不检查启用状态，因为要切换状态）
        if site_id not in self.resource_config.sites:
            raise ValueError(f"资源站 {site_id} 不存在")

        # 获取站点配置并切换状态
        site = self.resource_config.sites[site_id]
        site.enabled = not site.enabled

        # 立即保存配置到文件，确保状态持久化
        self.resource_config.save_config()

        return site.enabled

    def test_site_connection(self, site_id: str) -> dict:
        """
        测试资源站连接

        向指定站点发送测试请求，检查网络连通性和响应性能。
        使用标准的搜索接口进行测试，模拟真实的搜索请求。

        Args:
            site_id: 资源站ID

        Returns:
            测试结果字典，包含：
            - success: 是否连接成功
            - status_code: HTTP状态码（成功时）
            - elapsed_ms: 请求耗时（毫秒）
            - message: 结果描述信息
            - error: 错误信息（失败时）

        Raises:
            ValueError: 当站点不存在时抛出异常
        """
        # 验证站点是否存在
        if site_id not in self.resource_config.sites:
            raise ValueError(f"资源站 {site_id} 不存在")

        site = self.resource_config.sites[site_id]

        async def test_connection():
            """内部异步函数，执行实际的连接测试"""
            # 从配置中随机选择测试关键词，避免固定关键词被识别
            test_keywords = Config.CONNECTION_TEST_CONFIG["test_keywords"]
            test_keyword = random.choice(test_keywords)

            # 构建测试请求参数（使用真实搜索接口进行测试）
            params = self.http_client.build_params(
                {
                    "ac": "detail",  # 请求详情数据
                    site.search_endpoint: test_keyword,  # 使用随机常见关键词
                }
            )

            async with httpx.AsyncClient() as client:
                # 使用统一的HTTP客户端发送测试请求
                # 包含完整的日志记录和性能监控
                result = await self.http_client.request_with_logging(
                    client=client,
                    site_id=site.site_id,
                    site_name=site.name,
                    url=site.base_url,
                    params=params,
                    headers=TEST_HEADERS,  # 使用测试专用请求头
                    timeout=site.timeout,  # 使用站点配置的超时时间
                )

                # 检查HTTP请求是否成功
                if result.get("success"):
                    # 进行响应内容验证
                    validation_result = self._validate_response_content(result)

                    if validation_result["is_valid"]:
                        # 响应内容有效，返回成功结果
                        return {
                            "success": True,
                            "status_code": result.get("status_code"),
                            "elapsed_ms": result.get("elapsed_ms"),
                            "response_size": result.get("response_size", 0),
                            "message": "连接成功，API响应正常",
                            "test_keyword": test_keyword,
                        }
                    else:
                        # 响应内容无效（可能是验证码页面等）
                        return {
                            "success": False,
                            "elapsed_ms": result.get("elapsed_ms", 0),
                            "error": validation_result["error"],
                            "message": f"连接失败: {validation_result['error']}",
                            "test_keyword": test_keyword,
                        }
                else:
                    # HTTP请求失败，返回错误信息
                    error_msg = result.get("error", "未知错误")
                    return {
                        "success": False,
                        "elapsed_ms": result.get("elapsed_ms", 0),
                        "error": error_msg,
                        "message": f"连接失败: {error_msg}",
                        "test_keyword": test_keyword,
                    }

        # 将异步函数转换为同步执行，适配外部同步接口
        return asyncio.run(test_connection())

    def _validate_response_content(self, result: dict) -> dict:
        """
        验证响应内容是否为有效的API响应

        Args:
            result: HTTP请求结果字典

        Returns:
            dict: 验证结果 {"is_valid": bool, "error": str}
        """
        try:
            # 获取响应数据
            data = result.get("data")
            if not data:
                return {"is_valid": False, "error": "响应数据为空"}

            # 检查响应大小
            response_size = result.get("response_size", 0)
            min_size = Config.CONNECTION_TEST_CONFIG["response_validation"][
                "min_response_size"
            ]
            if response_size < min_size:
                return {
                    "is_valid": False,
                    "error": f"响应内容过短({response_size}字节)",
                }

            # 将响应转换为字符串进行检查
            response_text = str(data).lower()

            # 检查是否包含反爬机制的关键词
            invalid_indicators = Config.CONNECTION_TEST_CONFIG["response_validation"][
                "invalid_indicators"
            ]
            for indicator in invalid_indicators:
                if indicator.lower() in response_text:
                    return {"is_valid": False, "error": f"检测到反爬机制: {indicator}"}

            # 如果是字典类型，检查必要字段
            if isinstance(data, dict):
                # 检查API响应码
                if "code" in data:
                    valid_codes = Config.CONNECTION_TEST_CONFIG["response_validation"][
                        "valid_response_codes"
                    ]
                    if data.get("code") not in valid_codes:
                        return {
                            "is_valid": False,
                            "error": f"API返回错误码: {data.get('code')}",
                        }

                # 检查是否包含数据字段
                if "data" in data or "list" in data:
                    return {"is_valid": True, "error": ""}
                else:
                    return {"is_valid": False, "error": "响应缺少数据字段"}

            # 非字典类型响应，只要不包含反爬关键词就认为有效
            return {"is_valid": True, "error": ""}

        except Exception as e:
            return {"is_valid": False, "error": f"响应验证异常: {str(e)}"}
