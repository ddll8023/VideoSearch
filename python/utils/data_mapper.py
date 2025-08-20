"""
数据映射工具模块

提供通用的字段映射和数据转换函数，用于处理来自不同视频资源站点的数据格式统一化
"""

from typing import Any, Dict, List


def safe_get(data: Dict[str, Any], key: str, default: str = "") -> str:
    """
    安全获取字符串字段值

    Args:
        data: 数据字典
        key: 字段名
        default: 默认值

    Returns:
        字符串值
    """
    value = data.get(key)
    if value is None:
        return default

    # 将值转换为字符串并去除首尾空白字符
    # 如果去除空白后为空字符串，则返回默认值
    stripped_value = str(value).strip()
    return stripped_value if stripped_value else default


def safe_get_int(data: Dict[str, Any], key: str, default: int = 0) -> int:
    """
    安全获取整数字段值

    Args:
        data: 数据字典
        key: 字段名
        default: 默认值

    Returns:
        整数值
    """
    try:
        value = data.get(key)
        # 检查空值或空字符串
        if value is None or value == "":
            return default

        # 先转换为float再转换为int，这样可以正确处理"1.0"这样的字符串
        # 避免直接转int时遇到浮点数字符串报错的问题
        return int(float(str(value)))
    except (ValueError, TypeError):
        # 转换失败时返回默认值，确保程序不会因为数据格式问题崩溃
        return default


def parse_play_sources(
    play_url_str: str, play_from_str: str = ""
) -> Dict[str, List[Dict[str, Any]]]:
    """
    解析拼接的播放链接字符串为按格式分类的数据结构

    支持的格式：
    - 多播放源格式: play_from="source1$$$source2", play_url="第01集$url1#第02集$url2$$$第01集$url3#第02集$url4"
    - 单播放源格式: play_from="source1", play_url="第01集$url1#第02集$url2"

    Args:
        play_url_str: 拼接的播放链接字符串
        play_from_str: 播放源标识字符串

    Returns:
        按格式分类的播放源字典: {格式类型: [播放项列表]}
        例如: {"m3u8": [{"name": "第01集", "url": "..."}], "mp4": [{"name": "第01集", "url": "..."}]}
    """
    if not play_url_str or not isinstance(play_url_str, str):
        return {}

    # 分割播放源名称和播放链接
    play_from_list = play_from_str.split("$$$") if play_from_str else [""]
    play_url_list = play_url_str.split("$$$")

    # 确保播放源和播放链接数量一致
    if len(play_from_list) != len(play_url_list):
        # 如果数量不一致，使用默认播放源名称
        while len(play_from_list) < len(play_url_list):
            play_from_list.append(f"source_{len(play_from_list) + 1}")

    play_sources = {}

    # 遍历每个播放源
    for i, (play_from, play_url) in enumerate(zip(play_from_list, play_url_list)):
        play_from = play_from.strip()
        play_url = play_url.strip()

        if not play_url:
            continue

        # 解析单个播放源的播放列表
        episodes = play_url.split("#")
        episode_list = []

        for episode in episodes:
            episode = episode.strip()
            if not episode:
                continue

            # 按 $ 分割名称和URL
            if "$" in episode:
                parts = episode.split("$", 1)  # 只分割第一个$，防止URL中包含$
                if len(parts) == 2:
                    name = parts[0].strip()
                    url = parts[1].strip()

                    # 验证名称和URL都不为空
                    if name and url:
                        episode_list.append({"name": name, "url": url})

        if episode_list:
            # 识别播放格式
            format_type = _identify_play_format(play_from, episode_list[0]["url"])

            # 合并到对应格式类型
            if format_type not in play_sources:
                play_sources[format_type] = []

            # 直接添加到格式分类中，去掉播放源名称层级
            play_sources[format_type].extend(episode_list)

    return play_sources


def _identify_play_format(play_from: str, sample_url: str) -> str:
    """
    识别播放格式类型

    Args:
        play_from: 播放源名称
        sample_url: 示例URL

    Returns:
        格式类型字符串
    """
    # 优先根据URL扩展名判断
    if ".m3u8" in sample_url.lower():
        return "m3u8"
    elif ".mp4" in sample_url.lower():
        return "mp4"
    elif ".flv" in sample_url.lower():
        return "flv"
    elif ".avi" in sample_url.lower():
        return "avi"

    # 根据播放源名称判断
    play_from_lower = play_from.lower()
    if "m3u8" in play_from_lower:
        return "m3u8"
    elif "mp4" in play_from_lower:
        return "mp4"

    # 默认根据URL特征判断
    if "index.m3u8" in sample_url:
        return "m3u8"
    elif any(ext in sample_url.lower() for ext in [".mp4", ".mkv", ".avi", ".rmvb"]):
        return "mp4"
    elif "share" in sample_url.lower() or "share" in play_from_lower:
        return "mp4"  # 将分享链接归类为mp4格式

    # 默认分类为mp4
    return "mp4"


def extract_video_items(data: Dict[str, Any]) -> list:
    """
    从不同格式的响应数据中提取视频列表

    不同的视频资源站点API返回的数据格式可能不同，此函数统一处理这些格式差异

    支持的数据格式：
    - {"list": [...]}           # 如意资源等站点格式
    - {"data": {"list": [...]}} # 嵌套格式
    - {"data": [...]}           # 直接数组格式

    Args:
        data: 响应数据

    Returns:
        视频条目列表
    """
    # 输入校验：确保数据是字典类型
    if not isinstance(data, dict):
        return []

    # 格式1: 处理 {"list": [...]} 格式（如意资源等）
    if isinstance(data.get("list"), list):
        return data.get("list")

    # 格式2: 处理 {"data": {"list": [...]}} 嵌套格式
    elif isinstance(data.get("data"), dict) and isinstance(
        data["data"].get("list"), list
    ):
        return data["data"]["list"]

    # 格式3: 处理直接返回列表的格式 {"data": [...]}
    elif isinstance(data.get("data"), list):
        return data.get("data")

    # 如果都不匹配，返回空列表，避免程序异常
    return []


def map_video_fields(
    site_id: str, site_name: str, item: Dict[str, Any]
) -> Dict[str, Any]:
    """
    将各站点视频条目映射为标准字段格式

    不同视频资源站点的字段名可能不同，此函数将其统一映射为标准格式
    便于前端统一处理和显示

    Args:
        site_id: 资源站点ID
        site_name: 资源站点名称
        item: 从资源站点获取的单个视频条目数据

    Returns:
        标准格式的视频数据字典
    """
    # 输入校验：如果不是字典类型，返回最基本的结构
    if not isinstance(item, dict):
        return {
            "platform": site_name or site_id,
            "id": "",
            "title": "",
            "play_sources": {},
        }

    # 从原始数据中提取各个字段，使用safe_get确保安全性
    vid = safe_get(item, "vod_id")  # 视频ID
    title = safe_get(item, "vod_name")  # 视频标题
    thumb = safe_get(item, "vod_pic")  # 缩略图URL
    desc = safe_get(item, "vod_content")  # 视频描述
    upload_date = safe_get(item, "vod_pubdate")  # 发布日期
    channel = safe_get(item, "vod_class")  # 分类/频道
    actor = safe_get(item, "vod_actor")  # 演员信息
    area = safe_get(item, "vod_area")  # 地区
    language = safe_get(item, "vod_lang")  # 语言
    year = safe_get(item, "vod_year")  # 年份
    status = safe_get(item, "vod_remarks")  # 状态备注
    type_name = safe_get(item, "type_name")  # 视频类型名称

    # 提取播放相关字段
    play_from = safe_get(item, "vod_play_from")  # 播放源标识
    play_url_str = safe_get(item, "vod_play_url")  # 播放链接字符串

    # 解析播放源结构
    play_sources = parse_play_sources(play_url_str, play_from)

    # 处理播放次数：尝试多个可能的字段名
    view_count = safe_get_int(item, "vod_hits")
    if view_count == 0:
        # 如果vod_hits为0，尝试另一个常见的字段名
        view_count = safe_get_int(item, "view_count")

    # 返回标准化的视频数据结构
    return {
        "platform": site_name or site_id,  # 平台名称，优先使用site_name
        "id": vid,  # 视频唯一标识
        "title": title,  # 视频标题
        "description": desc,  # 视频描述
        "thumbnail": thumb,  # 缩略图URL
        "view_count": view_count,  # 播放次数
        "upload_date": upload_date,  # 上传日期
        "channel": channel,  # 频道/分类
        "actor": actor,  # 演员
        "area": area,  # 地区
        "language": language,  # 语言
        "year": year,  # 年份
        "status": status,  # 状态信息
        "type_name": type_name,  # 视频类型名称
        "play_sources": play_sources,  # 按格式分类的播放源字典
    }
