"""
视频资源站配置管理模块

管理多个视频资源站的基本配置信息
"""

import os
import json
from dataclasses import dataclass, asdict


@dataclass
class ResourceSiteConfig:
    """视频资源站配置"""

    # 基础信息
    site_id: str
    name: str
    base_url: str
    enabled: bool = True
    timeout: int = 15
    search_endpoint: str = "wd"
    page_param: str = "pg"
    action_param: str = "ac"

    @classmethod
    def from_dict(cls, data: dict) -> "ResourceSiteConfig":
        """从字典创建配置对象"""
        name = data.get("name")
        base_url = data.get("base_url")
        site_id = data.get("site_id")

        # 验证必需字段
        if not name or not base_url:
            raise ValueError("name和base_url是必需字段")

        return cls(
            site_id=site_id,
            name=name,
            base_url=base_url,
            enabled=data.get("enabled", True),
            timeout=data.get("timeout", 15),
            search_endpoint=data.get("search_endpoint", "wd"),
            page_param=data.get("page_param", "pg"),
            action_param=data.get("action_param", "ac"),
        )


class ResourceConfig:
    """资源站配置管理器"""

    def __init__(self, config_file: str | None = None):
        """初始化配置管理器"""
        # 配置文件路径
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), "resource_sites.json"
        )
        # 资源站配置字典
        self.sites: dict[str, ResourceSiteConfig] = {}
        # 加载配置文件
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                # 读取配置文件
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data: dict = json.load(f)

                # 清空现有配置
                self.sites.clear()

                # 获取sites数组
                sites_list = config_data.get("sites", [])
                print(f"配置中存在: {len(sites_list)}个资源站")
                # print(sites_list)
                for site_data in sites_list:
                    site_id = site_data.get("site_id")
                    if site_id:
                        self.sites[site_id] = ResourceSiteConfig.from_dict(site_data)

            except Exception as e:
                print(f"加载配置文件失败: {e}")
        else:
            print(f"配置文件不存在: {self.config_file}")

    def get_enabled_sites(self) -> list[ResourceSiteConfig]:
        """获取已启用的资源站配置"""
        return [site for site in self.sites.values() if site.enabled]

    def get_site(self, site_id: str) -> ResourceSiteConfig | None:
        """根据ID获取资源站配置"""
        return self.sites.get(site_id)

    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {"sites": [asdict(site) for site in self.sites.values()]}

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            raise

    def to_dict_list(self) -> list[dict]:
        """
        将所有资源站配置转换为字典列表

        Returns:
            资源站配置字典列表
        """
        return [asdict(site) for site in self.sites.values()]
