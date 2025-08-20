from flask import Response, jsonify
import datetime


def calculate_pagination(page: int, page_size: int, total_count: int) -> dict:
    """
    计算分页信息的工具函数

    Args:
        page: 当前页码
        page_size: 每页大小
        total_count: 总数据量

    Returns:
        包含分页信息的字典
    """
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    return {
        "current_page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "next_page": page + 1 if page < total_pages else None,
        "previous_page": page - 1 if page > 1 else None,
    }


def success_response(
    data=None, message: str = "操作成功", status_code: int = 200
) -> Response:
    """
    成功响应格式化

    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码

    Returns:
        格式化的成功响应字典
    """
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.datetime.now().isoformat(),
        "data": data,
    }

    return jsonify(response)


def error_response(
    message: str = "操作失败",
    error_code: int = 500,
    details: str | None = None,
) -> Response:
    """
    错误响应格式化

    Args:
        message: 错误消息
        error_code: 错误状态码
        details: 详细错误信息

    Returns:
        格式化的错误响应字典
    """
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.datetime.now().isoformat(),
        "data": None,
    }

    if details:
        response["details"] = details

    return jsonify(response)


def validation_error_response(
    errors: dict[str, str], message: str = "参数验证失败"
) -> Response:
    """
    参数验证错误响应

    Args:
        errors: 验证错误字典 {字段名: 错误信息}
        message: 错误消息

    Returns:
        格式化的验证错误响应
    """
    response = {
        "success": False,
        "message": message,
        "error_code": 400,
        "timestamp": datetime.datetime.now().isoformat(),
        "data": None,
        "details": "请检查输入参数",
        "validation_errors": errors,
    }
    return jsonify(response)


def not_found_response(resource: str = "资源", message: str | None = None) -> Response:
    """
    资源不存在响应

    Args:
        resource: 资源名称
        message: 自定义错误消息

    Returns:
        格式化的404响应
    """
    if message is None:
        message = f"{resource}不存在"

    return error_response(
        message=message, error_code=404, details=f"请求的{resource}未找到"
    )
