# 视频搜索 API 技术文档

## 1. 视频搜索模块 (`/api/video`)

**功能描述**

视频搜索模块负责处理单个视频资源站点的内容检索功能。系统通过异步请求指定的视频资源站点，将站点返回的视频数据统一格式化为标准 Video 模型，并提供分页功能。前端可通过并发调用多个站点实现全平台搜索。

### 1.1 视频搜索接口

**功能描述**

用户通过提供搜索关键词和指定资源站点进行视频内容检索。系统将请求指定的视频资源站点，将站点返回的视频数据统一格式化为标准 Video 模型，并提供分页功能。

- **URL**: `/api/video/search`
- **HTTP 方法**: `GET`
- **Content-Type**: `application/json`

#### 请求参数 (Query Parameters)

| 参数名     | 类型    | 是否必需 | 默认值 | 描述                  |
| :--------- | :------ | :------- | :----- | :-------------------- |
| `wd`       | String  | 是       | -      | 搜索关键词 (不能为空) |
| `site_id`  | String  | 是       | -      | 资源站 ID (不能为空)  |
| `page`     | Integer | 否       | 1      | 页码 (必须大于 0)     |
| `pageSize` | Integer | 否       | 20     | 每页数量 (范围 1-100) |

#### 请求示例

```http
GET /api/video/search?wd=喜羊羊&site_id=lzm3u8&page=1&pageSize=20
```

#### 响应 (Response)

**成功响应 (200 OK)**

```json
{
	"success": true,
	"message": "搜索完成",
	"status_code": 200,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": {
		"success": true,
		"site_id": "lzm3u8",
		"site_name": "量子资源",
		"total_count": 158,
		"elapsed_ms": 1250,
		"videos": [
			{
				"platform": "量子资源",
				"id": "12345",
				"title": "喜羊羊与灰太狼之羊村守护者",
				"description": "羊村的小羊们在面对灰太狼的威胁时，团结一心保卫家园的故事",
				"thumbnail": "https://example.com/thumb/12345.jpg",
				"duration": 1800,
				"view_count": 158423,
				"upload_date": "2024-01-10",
				"channel": "动漫",
				"actor": "祖晴,张琳,梁颖",
				"area": "中国大陆",
				"language": "国语",
				"year": "2024",
				"status": "更新至第10集"
			}
		],
		"pagination": {
			"current_page": 1,
			"page_size": 20,
			"total_count": 158,
			"total_pages": 8,
			"has_next": true,
			"has_previous": false,
			"next_page": 2,
			"previous_page": null
		}
	}
}
```

**失败响应 (400 Bad Request)**

```json
{
	"success": false,
	"message": "参数验证失败",
	"error_code": 400,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": null,
	"details": "请检查输入参数",
	"validation_errors": {
		"wd": "搜索关键词不能为空",
		"site_id": "资源站ID不能为空"
	}
}
```

**失败响应 (500 Internal Server Error)**

```json
{
	"success": false,
	"message": "搜索失败: 网络连接超时",
	"error_code": 500,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": null
}
```

---

## 2. 资源管理模块 (`/api/resource`)

**功能描述**

资源管理模块负责视频资源站点的配置管理功能，包括获取站点信息、切换站点启用状态、连接测试等功能。

### 2.1 获取资源站点列表

**功能描述**

获取系统中配置的所有视频资源站点信息及统计数据。

- **URL**: `/api/resource/sites`
- **HTTP 方法**: `GET`
- **Content-Type**: `application/json`

#### 请求参数

无

#### 请求示例

```http
GET /api/resource/sites
```

#### 响应 (Response)

**成功响应 (200 OK)**

```json
{
	"success": true,
	"message": "获取资源站点信息成功",
	"status_code": 200,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": {
		"sites": [
			{
				"site_id": "lzm3u8",
				"name": "量子资源",
				"base_url": "https://cj.lziapi.com/api.php/provide/vod/at/xml/",
				"enabled": true,
				"timeout": 15
			},
			{
				"site_id": "ffzy",
				"name": "非凡资源",
				"base_url": "https://cj.ffzyapi.com/api.php/provide/vod/at/xml/",
				"enabled": false,
				"timeout": 15
			}
		],
		"stats": {
			"total_sites": 2,
			"enabled_sites": 1
		}
	}
}
```

### 2.2 切换站点启用状态

**功能描述**

切换指定资源站点的启用/禁用状态。

- **URL**: `/api/resource/sites/{site_id}/toggle`
- **HTTP 方法**: `POST`
- **Content-Type**: `application/json`

#### 路径参数

| 参数名    | 类型   | 是否必需 | 描述      |
| :-------- | :----- | :------- | :-------- |
| `site_id` | String | 是       | 资源站 ID |

#### 请求示例

```http
POST /api/resource/sites/lzm3u8/toggle
```

#### 响应 (Response)

**成功响应 (200 OK)**

```json
{
	"success": true,
	"message": "资源站点已禁用",
	"status_code": 200,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": {
		"site_id": "lzm3u8",
		"enabled": false
	}
}
```

**失败响应 (404 Not Found)**

```json
{
	"success": false,
	"message": "资源站点不存在",
	"error_code": 404,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": null,
	"details": "请求的资源站点未找到"
}
```

### 2.3 获取单个站点信息

**功能描述**

获取指定资源站点的详细配置信息。

- **URL**: `/api/resource/sites/{site_id}`
- **HTTP 方法**: `GET`
- **Content-Type**: `application/json`

#### 路径参数

| 参数名    | 类型   | 是否必需 | 描述      |
| :-------- | :----- | :------- | :-------- |
| `site_id` | String | 是       | 资源站 ID |

#### 请求示例

```http
GET /api/resource/sites/lzm3u8
```

#### 响应 (Response)

**成功响应 (200 OK)**

```json
{
	"success": true,
	"message": "获取站点信息成功",
	"status_code": 200,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": {
		"site_id": "lzm3u8",
		"name": "量子资源",
		"base_url": "https://cj.lziapi.com/api.php/provide/vod/at/xml/",
		"enabled": true,
		"timeout": 15,
		"search_endpoint": "wd",
		"page_param": "pg",
		"action_param": "ac"
	}
}
```

### 2.4 测试站点连接

**功能描述**

测试指定资源站点的网络连接状态和响应性能。

- **URL**: `/api/resource/sites/{site_id}/test`
- **HTTP 方法**: `POST`
- **Content-Type**: `application/json`

#### 路径参数

| 参数名    | 类型   | 是否必需 | 描述      |
| :-------- | :----- | :------- | :-------- |
| `site_id` | String | 是       | 资源站 ID |

#### 请求示例

```http
POST /api/resource/sites/lzm3u8/test
```

#### 响应 (Response)

**成功响应 (200 OK)**

```json
{
	"success": true,
	"message": "连接测试完成",
	"status_code": 200,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": {
		"success": true,
		"status_code": 200,
		"elapsed_ms": 856,
		"response_size": 0,
		"message": "连接成功"
	}
}
```

**失败响应 (连接失败)**

```json
{
	"success": true,
	"message": "连接测试完成",
	"status_code": 200,
	"timestamp": "2024-01-15T10:30:45.123456",
	"data": {
		"success": false,
		"elapsed_ms": 15000,
		"error": "连接超时",
		"message": "连接失败: 连接超时"
	}
}
```

---
