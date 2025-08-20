import os
from datetime import timedelta


class Config:
    """基础配置类"""

    # 基础配置
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

    # HTTP客户端配置
    HTTP_TIMEOUT = 30
    HTTP_RETRIES = 3

    # API配置
    API_VERSION = "v1"
    API_TITLE = "VideoSearch API"

    # 跨域配置
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://localhost:5000",
    ]

    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 搜索配置
    SEARCH_TIMEOUT = 10
    MAX_SEARCH_RESULTS = 500

    # 资源站配置
    RESOURCE_SITES_CONFIG = {
        "enabled": True,
        "max_concurrent_requests": 5,
        "request_timeout": 15,
        "retry_attempts": 2,
        "cache_enabled": True,
        "cache_ttl": 300,  # 5分钟缓存
    }

    # 资源站API认证配置
    RESOURCE_AUTH_CONFIG = {
        "default_headers": {
            "User-Agent": "VideoSearch/1.0.0",
            "Accept": "application/json",
        },
        "test_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        "auth_methods": ["api_key", "bearer_token", "basic_auth", "none"],
    }

    # 连接测试配置
    CONNECTION_TEST_CONFIG = {
        "test_keywords": ["电影", "电视剧", "动漫", "综艺", "纪录片"],
        "response_validation": {
            "min_response_size": 100,
            "required_fields": ["code", "msg", "data"],
            "invalid_indicators": [
                "verify",
                "captcha",
                "验证",
                "人机验证",
                "Request ID",
            ],
            "valid_response_codes": [1, 0, 200],
        },
        "timeout_settings": {
            "connect_timeout": 10,
            "read_timeout": 15,
        },
    }

    # 数据映射配置
    DATA_MAPPING_CONFIG = {
        "strict_validation": False,
        "allow_missing_fields": True,
        "default_values": {
            "view_count": 0,
            "like_count": 0,
            "comment_count": 0,
        },
        "field_transformations": {
            "view_count": ["views", "play_count", "watch_count"],
            "upload_date": ["created_at", "published_at", "date"],
        },
    }

    # 响应处理配置
    RESPONSE_CONFIG = {
        "max_response_size": 10 * 1024 * 1024,  # 10MB
        "encoding": "utf-8",
        "parse_html": False,
        "follow_redirects": True,
    }

    # 错误处理配置
    ERROR_CONFIG = {
        "log_errors": True,
        "ignore_ssl_errors": False,
        "max_error_count": 5,
        "error_cooldown": 60,  # 秒
    }

    # 日志配置
    LOGGING_CONFIG = {
        "level": "INFO",
        "enable_console": True,
        "enable_file": True,
        "log_file": "logs/video_search.log",
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
        "json_format": True,  # 文件使用JSON格式，控制台使用简洁格式
    }


class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True
    ENV = "development"

    # 开发环境资源站配置
    RESOURCE_SITES_CONFIG = {
        **Config.RESOURCE_SITES_CONFIG,
        "cache_enabled": False,
        "request_timeout": 30,  # 开发环境超时时间更长
    }

    # 开发环境错误配置
    ERROR_CONFIG = {
        **Config.ERROR_CONFIG,
        "ignore_ssl_errors": True,  # 开发环境忽略SSL错误
    }

    # 开发环境日志配置
    LOGGING_CONFIG = {
        **Config.LOGGING_CONFIG,
        "level": "INFO",  # 开发环境也使用INFO级别，减少噪音
        "log_file": "logs/video_search_dev.log",
    }


class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False
    ENV = "production"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # 生产环境资源站配置
    RESOURCE_SITES_CONFIG = {
        **Config.RESOURCE_SITES_CONFIG,
        "max_concurrent_requests": 10,
        "cache_ttl": 600,  # 生产环境缓存时间更长
    }

    # 生产环境响应配置
    RESPONSE_CONFIG = {
        **Config.RESPONSE_CONFIG,
        "max_response_size": 5 * 1024 * 1024,  # 生产环境限制更严格
    }

    # 生产环境日志配置
    LOGGING_CONFIG = {
        **Config.LOGGING_CONFIG,
        "level": "INFO",
        "log_file": "logs/video_search_prod.log",
        "enable_console": False,  # 生产环境关闭控制台输出
    }


# 配置映射
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
