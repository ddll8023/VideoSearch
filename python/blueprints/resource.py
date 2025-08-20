from flask import Blueprint, request, jsonify
from dataclasses import asdict
from services.resource_manager import ResourceManager
from utils.response import success_response, error_response, not_found_response

resource_bp = Blueprint("resource", __name__)
resource_manager = ResourceManager()


@resource_bp.route("/sites", methods=["GET"])
def get_resource_sites():
    """获取所有资源站点信息"""
    try:
        sites_info = resource_manager.get_sites_info()
        stats = resource_manager.get_stats()

        return success_response(
            data={"sites": sites_info, "stats": stats}, message="获取资源站点信息成功"
        )
    except Exception as e:
        return (
            error_response(message=f"获取资源站点信息失败: {str(e)}", error_code=500),
            500,
        )


@resource_bp.route("/sites/<site_id>/toggle", methods=["POST"])
def toggle_site_status(site_id):
    """切换资源站点启用状态"""
    try:
        # 验证站点（不检查启用状态，因为要切换状态）
        site = resource_manager.resource_config.get_site(site_id)
        if not site:
            return not_found_response("资源站点"), 404

        # 切换启用状态
        new_status = resource_manager.toggle_site_status(site_id)

        return success_response(
            data={"site_id": site_id, "enabled": new_status},
            message=f"资源站点已{'启用' if new_status else '禁用'}",
        )
    except Exception as e:
        return (
            error_response(message=f"切换站点状态失败: {str(e)}", error_code=500),
            500,
        )


@resource_bp.route("/sites/<site_id>", methods=["GET"])
def get_site_info(site_id):
    """获取单个资源站点详细信息"""
    try:
        site = resource_manager.resource_config.get_site(site_id)
        if not site:
            return not_found_response("资源站点"), 404

        return success_response(data=asdict(site), message="获取站点信息成功")
    except Exception as e:
        return (
            error_response(message=f"获取站点信息失败: {str(e)}", error_code=500),
            500,
        )


@resource_bp.route("/sites/<site_id>/test", methods=["POST"])
def test_site_connection(site_id):
    """测试资源站点连接"""
    try:
        site = resource_manager.resource_config.get_site(site_id)
        if not site:
            return not_found_response("资源站点"), 404

        # 执行连接测试
        test_result = resource_manager.test_site_connection(site_id)

        return success_response(data=test_result, message="连接测试完成")
    except Exception as e:
        return error_response(message=f"连接测试失败: {str(e)}", error_code=500), 500
