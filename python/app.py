from flask import Flask
from flask_cors import CORS
from settings import Config
from blueprints.video import video_bp
from blueprints.resource import resource_bp
import logging
from utils.logger import setup_logging
from utils.response import error_response, not_found_response


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 配置日志系统
    logging_config = app.config.get("LOGGING_CONFIG", {})
    setup_logging(
        log_level=logging_config.get("level", "INFO"),
        log_file=(
            logging_config.get("log_file")
            if logging_config.get("enable_file")
            else None
        ),
        max_file_size=logging_config.get("max_file_size", 10 * 1024 * 1024),
        backup_count=logging_config.get("backup_count", 5),
        enable_console=logging_config.get("enable_console", True),
        json_format=logging_config.get("json_format", True),
    )

    # 获取应用日志器
    logger = logging.getLogger("video_search.app")
    logger.info("VideoSearch应用启动", extra={"component": "app"})

    # 配置CORS
    CORS(
        app,
        origins=app.config.get(
            "CORS_ORIGINS",
            [
                "http://localhost:5174",
                "http://localhost:8080",
                "http://localhost:5173",
            ],
        ),
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # 注册蓝图
    app.register_blueprint(video_bp, url_prefix="/api/video")
    app.register_blueprint(resource_bp, url_prefix="/api/resource")

    # 错误处理器
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404错误: {error}", extra={"error_code": 404})
        return not_found_response("接口"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500错误: {error}", extra={"error_code": 500}, exc_info=True)
        return error_response(message="服务器内部错误", error_code=500), 500

    return app


# 创建全局应用实例供uWSGI使用
application = create_app()

# 为Gunicorn提供标准的app实例名
app = application

if __name__ == "__main__":
    # 开发模式直接运行
    application.run(debug=True, host="0.0.0.0", port=5000)
