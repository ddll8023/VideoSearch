from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any


@dataclass
class Video:
    """视频数据模型 - 框架构建版本"""

    platform: str
    id: str
    title: str
    description: str = ""
    thumbnail: str = ""
    view_count: int = 0
    upload_date: str = ""
    channel: str = ""
    actor: str = ""
    area: str = ""
    language: str = ""
    year: str = ""
    status: str = ""
    type_name: str = ""
    play_sources: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Video":
        """从字典创建视频对象"""
        # 过滤出只包含Video字段的数据，避免传入多余字段
        valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
