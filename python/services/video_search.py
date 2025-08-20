from __future__ import annotations

# 异步IO库，用于将异步函数转换为同步调用
import asyncio

# HTTP异步客户端库，用于发送异步HTTP请求
import httpx

# 导入资源站点配置类
from config import ResourceSiteConfig

# 导入资源管理器，用于验证和管理视频资源站点
from services.resource_manager import ResourceManager

# 导入统一的视频数据模型
from models.video import Video

# 导入日志工具
import logging

# 导入分页计算工具
from utils.response import calculate_pagination

# 导入HTTP客户端工具
from utils.http_client import HttpClient, SEARCH_HEADERS

# 导入数据提取和映射工具
from utils.data_mapper import extract_video_items, map_video_fields


class VideoSearchService:
    """
    视频搜索服务类

    提供单个视频资源站点的搜索功能，支持异步请求指定的视频资源站点，
    统一数据格式并提供标准化的搜索结果。前端通过并发调用实现多站点搜索。

    主要功能：
    - 异步搜索指定的单个视频资源站点
    - 统一不同站点的数据格式为标准Video模型
    - 分页处理和错误处理
    - 请求性能监控和日志记录
    """

    def __init__(self) -> None:
        """
        初始化视频搜索服务

        创建资源管理器实例，用于获取已启用的视频资源站点配置信息。
        """
        # 创建资源管理器实例，负责站点配置的验证和管理
        self.resource_manager = ResourceManager()
        # 创建HTTP客户端实例，负责发送HTTP请求
        self.http_client = HttpClient()
        # 创建专用的日志记录器，用于记录搜索服务的操作日志
        self.logger = logging.getLogger("video_search.service")

    async def _fetch_site_raw(
        self,
        client: httpx.AsyncClient,
        site: ResourceSiteConfig,
        wd: str,
        pg: int,
    ) -> dict:
        """
        异步获取单个资源站点的原始搜索结果

        Args:
            client: httpx异步HTTP客户端实例
            site: 资源站点配置对象，包含站点URL和参数信息
            wd: 搜索关键词
            pg: 页码，从1开始

        Returns:
            dict: 包含请求结果的字典
                - ok (bool): 请求是否成功
                - elapsed_ms (int): 请求耗时（毫秒）
                - data (dict): 成功时返回的数据，可选
                - error (str): 失败时的错误信息，可选
        """
        # 根据站点配置构建标准化的搜索请求参数
        params = self.http_client.build_params(
            {
                site.action_param: "detail",
                site.search_endpoint: wd,
                site.page_param: pg,
            }
        )

        # 使用HttpClient发送请求，自动处理日志记录和性能监控
        # 超时时间从站点配置获取，默认15秒
        return await self.http_client.request_with_logging(
            client=client,
            site_id=site.site_id,
            site_name=site.name,
            url=site.base_url,
            params=params,
            headers=SEARCH_HEADERS,
            timeout=getattr(site, "timeout", 15),  # 获取站点超时配置，默认15秒
        )

    def _should_filter_video(self, item: dict) -> bool:
        """
        判断是否应该过滤该视频

        Args:
            item: 从资源站点获取的单个视频条目数据

        Returns:
            bool: True表示应该过滤（排除），False表示不过滤（保留）
        """
        # 获取视频类型名称
        type_name = item.get("type_name", "")

        # 定义需要过滤的视频类型
        filtered_types = ["预告片", "电影解说", "影视解说"]

        # 判断是否为需要过滤的类型
        return type_name in filtered_types

    def _map_item_to_video(self, site_id: str, site_name: str, item: dict) -> Video:
        """
        将各站点条目映射至统一 Video 模型

        Args:
            site_id: 资源站点ID
            site_name: 资源站点名称
            item: 从资源站点获取的单个视频条目数据

        Returns:
            Video: 统一格式的视频对象
        """
        # 使用数据映射工具将不同站点的数据格式统一为标准格式
        video_data = map_video_fields(site_id, site_name, item)
        # 从标准化的字典数据创建Video对象
        return Video.from_dict(video_data)

    async def _process_single_site(
        self, client: httpx.AsyncClient, site, query: str, page: int, page_size: int
    ):
        """
        处理单个站点的搜索请求

        Args:
            client: httpx异步客户端
            site: 站点配置
            query: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            dict: 站点搜索结果
        """
        try:
            # 发送搜索请求并获取原始响应数据
            site_result = await self._fetch_site_raw(client, site, query, page)

            # 检查请求是否成功
            if site_result.get("success"):
                # 处理成功的站点结果
                data = site_result.get("data", {})
                videos = []

                # 验证数据格式：确保data是字典类型
                if not isinstance(data, dict):
                    self.logger.warning(
                        f"站点 {site.name} 返回的数据格式异常: {type(data)}"
                    )
                    return {
                        "type": "site_error",
                        "site_id": site.site_id,
                        "site_name": site.name,
                        "elapsed_ms": site_result.get("elapsed_ms", 0),
                        "error": "数据格式错误：期望字典类型",
                    }

                # 从资源站返回的数据中提取总记录数
                # 不同站点的数据结构可能不同，需要安全获取
                total_count = 0
                if isinstance(data, dict):
                    total_count = data.get("total", 0)

                    # 使用数据提取工具从响应中提取视频列表
                # 不同站点的视频列表可能在不同的字段中
                items = extract_video_items(data)

                # 统计过滤前后的数据量
                original_count = len(items)  # 原始数据总数
                filtered_count = 0  # 被过滤掉的数据数量

                # 将每个视频条目转换为统一的Video对象
                for item in items:
                    # 检查是否需要过滤该视频
                    if self._should_filter_video(item):
                        filtered_count += 1  # 记录被过滤的数量
                        continue  # 跳过需要过滤的视频类型

                    video = self._map_item_to_video(site.site_id, site.name, item)
                    # 只保留有效的视频数据（必须有ID和标题）
                    if video.id and video.title:
                        videos.append(video.to_dict())

                # 计算实际展示的视频数量
                display_count = len(videos)

                # 返回成功的站点搜索结果
                return {
                    "type": "site_success",
                    "site_id": site.site_id,
                    "site_name": site.name,
                    "elapsed_ms": site_result.get("elapsed_ms", 0),
                    "total_count": total_count,  # 资源站返回的总数
                    "original_count": original_count,  # 原始数据总数
                    "filtered_count": filtered_count,  # 被过滤掉的数据数量
                    "display_count": display_count,  # 实际展示的视频数量
                    "videos": videos,
                }
            else:
                # 请求失败，返回错误信息
                return {
                    "type": "site_error",
                    "site_id": site.site_id,
                    "site_name": site.name,
                    "elapsed_ms": site_result.get("elapsed_ms", 0),
                    "error": site_result.get("error", "未知错误"),
                }

        except Exception as e:
            # 捕获并处理所有异常，确保单个站点的错误不影响整体服务
            return {
                "type": "site_error",
                "site_id": site.site_id,
                "site_name": site.name,
                "error": f"请求异常: {str(e)}",
            }

    def search_single_site(self, query: str, page: int, page_size: int, site_id: str):
        """
        同步搜索单个指定的资源站点

        Args:
            query: 搜索关键词
            page: 页码，从1开始
            page_size: 每页显示的视频数量
            site_id: 指定的资源站ID

        Returns:
            dict: 站点搜索结果
        """
        # 首先验证请求的站点是否存在且已启用
        is_valid, error_msg, site = self.resource_manager.validate_site(site_id)
        if not is_valid:
            # 站点验证失败，返回错误响应
            return {
                "success": False,
                "error": error_msg,
                "site_id": site_id,
                "site_name": site.name if site else "未知站点",
                "videos": [],
                "total_count": 0,
            }

        # 定义内部异步函数，用于处理实际的搜索逻辑
        # 使用异步上下文管理器确保HTTP客户端正确关闭
        async def process_single_site():
            async with httpx.AsyncClient() as client:
                return await self._process_single_site(
                    client, site, query, page, page_size
                )

        # 使用asyncio.run将异步函数转换为同步执行
        # 这样可以在同步接口中使用异步的HTTP请求能力
        result = asyncio.run(process_single_site())

        # 格式化搜索结果，添加分页信息等
        return self._format_search_result(result, page, page_size)

    def _format_search_result(self, result: dict, page: int, page_size: int) -> dict:
        """
        格式化搜索结果

        Args:
            result: 原始搜索结果
            page: 页码
            page_size: 每页大小

        Returns:
            格式化后的搜索结果
        """
        # 根据搜索结果类型进行不同的格式化处理
        if result.get("type") == "site_success":
            # 成功结果的格式化
            total_count = result.get("total_count", 0)

            return {
                "success": True,
                "site_id": result.get("site_id"),
                "site_name": result.get("site_name"),
                "videos": result.get("videos", []),
                "total_count": total_count,
                "original_count": result.get("original_count", 0),  # 原始数据总数
                "filtered_count": result.get("filtered_count", 0),  # 被过滤掉的数据数量
                "display_count": result.get("display_count", 0),  # 实际展示的视频数量
                "elapsed_ms": result.get("elapsed_ms", 0),
                # 计算并添加分页信息（当前页、总页数、是否有下一页等）
                "pagination": calculate_pagination(page, page_size, total_count),
            }
        else:
            # 失败结果的格式化，确保返回结构一致
            return {
                "success": False,
                "error": result.get("error", "搜索失败"),
                "site_id": result.get("site_id"),
                "site_name": result.get("site_name"),
                "videos": [],
                "total_count": 0,
                # 即使失败也要提供分页信息，保持API响应结构一致
                "pagination": calculate_pagination(page, page_size, 0),
            }

    def get_video_detail(
        self, keyword: str, page: int, site_id: str, vod_id: str
    ) -> dict:
        """
        获取指定视频的详细信息

        通过重新发起搜索请求，从结果中找到匹配的视频条目并返回完整信息

        Args:
            keyword: 搜索关键词
            page: 页码
            site_id: 资源站ID
            vod_id: 视频ID

        Returns:
            包含视频详细信息的字典
        """
        try:
            # 首先验证站点是否有效
            is_valid, error_msg, site = self.resource_manager.validate_site(site_id)
            if not is_valid:
                return {"success": False, "error": error_msg, "video": None}

            # 发起搜索请求获取该页的所有视频
            search_result = self.search_single_site(
                query=keyword,
                page=page,
                page_size=50,  # 增大页面大小以确保找到目标视频
                site_id=site_id,
            )

            if not search_result.get("success"):
                return {
                    "success": False,
                    "error": search_result.get("error", "搜索失败"),
                    "video": None,
                }

            # 从搜索结果中查找匹配的视频
            videos = search_result.get("videos", [])
            target_video = None

            for video in videos:
                if str(video.get("id")) == str(vod_id):
                    target_video = video
                    break

            if not target_video:
                return {
                    "success": False,
                    "error": f"未找到ID为 {vod_id} 的视频",
                    "video": None,
                }

            # 返回找到的视频详细信息
            return {
                "success": True,
                "video": target_video,
                "site_id": site_id,
                "site_name": search_result.get("site_name"),
                "message": "获取视频详情成功",
            }

        except Exception as e:
            self.logger.error(f"获取视频详情失败: {str(e)}")
            return {
                "success": False,
                "error": f"获取视频详情失败: {str(e)}",
                "video": None,
            }


if __name__ == "__main__":
    # 测试代码：演示如何使用VideoSearchService进行视频搜索
    # 创建服务实例
    service = VideoSearchService()

    # 执行搜索测试
    # 搜索关键词：喜羊羊
    # 页码：第1页
    # 每页数量：10条
    # 目标站点：lzm3u8
    result = service.search_single_site(
        "喜羊羊", page=1, page_size=10, site_id="lzm3u8"
    )

    # 输出搜索结果用于调试
    print(result)
