from flask import Blueprint, request
from services.video_search import VideoSearchService
from utils.response import success_response, error_response, validation_error_response

video_bp = Blueprint("video", __name__)
video_service = VideoSearchService()


def validate_search_params(
    query: str, site_id: str, page: int, page_size: int
) -> dict | None:
    """
    验证搜索参数

    Args:
        query: 搜索关键词
        site_id: 资源站ID
        page: 页码
        page_size: 每页大小

    Returns:
        验证错误字典，如果验证通过则返回None
    """
    errors = {}

    if not query.strip():
        errors["wd"] = "搜索关键词不能为空"

    if not site_id.strip():
        errors["site_id"] = "资源站ID不能为空"

    if page < 1:
        errors["page"] = "页码必须大于0"

    if page_size < 1 or page_size > 100:
        errors["pageSize"] = "每页数量必须在1-100之间"

    return errors if errors else None


@video_bp.route("/search", methods=["GET"])
def search_videos():
    """视频搜索接口"""
    try:
        # 获取查询参数
        query = request.args.get("wd", "").strip()
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("pageSize", 20, type=int)
        site_id = request.args.get("site_id", "").strip()

        # 参数验证
        validation_errors = validate_search_params(query, site_id, page, page_size)
        if validation_errors:
            return validation_error_response(validation_errors), 400

        # 单个资源站搜索
        result = video_service.search_single_site(
            query=query, page=page, page_size=page_size, site_id=site_id
        )

        return success_response(data=result, message="搜索完成")

    except Exception as e:
        return error_response(message=f"搜索失败: {str(e)}", error_code=500), 500


@video_bp.route("/detail", methods=["GET"])
def get_video_detail():
    """视频详情接口"""
    try:
        # 获取查询参数
        keyword = request.args.get("keyword", "").strip()
        page = request.args.get("page", 1, type=int)
        site_id = request.args.get("site_id", "").strip()
        vod_id = request.args.get("vod_id", "").strip()

        # 参数验证
        errors = {}
        if not keyword:
            errors["keyword"] = "搜索关键词不能为空"
        if not site_id:
            errors["site_id"] = "资源站ID不能为空"
        if not vod_id:
            errors["vod_id"] = "视频ID不能为空"
        if page < 1:
            errors["page"] = "页码必须大于0"

        if errors:
            return validation_error_response(errors), 400

        # 获取视频详情
        result = video_service.get_video_detail(
            keyword=keyword, page=page, site_id=site_id, vod_id=vod_id
        )

        if result.get("success"):
            return success_response(data=result, message="获取视频详情成功")
        else:
            return (
                error_response(
                    message=result.get("error", "获取详情失败"), error_code=404
                ),
                404,
            )

    except Exception as e:
        return (
            error_response(message=f"获取视频详情失败: {str(e)}", error_code=500),
            500,
        )
