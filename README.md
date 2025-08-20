# VideoSearch 项目技术说明文档

## 项目概述

VideoSearch 是一个聚合视频搜索系统，通过整合多个视频资源站的API，为用户提供统一的视频搜索服务。系统采用前后端分离架构，后端基于Flask框架构建RESTful API，前端使用Vue.js构建用户界面。

## 技术架构

### 后端架构

- **核心框架**: Flask
- **主要依赖**: flask, flask-cors, httpx
- **架构模式**: 应用工厂模式 + 蓝图路由

#### 核心组件

1. **视频搜索服务 (VideoSearchService)**
   - 实现异步并发搜索多个视频资源站
   - 统一不同来源的数据格式为标准Video模型
   - 支持搜索结果分页和过滤
   - 内置请求性能监控和日志记录

2. **资源管理器 (ResourceManager)**
   - 管理多个视频资源站的配置信息
   - 提供站点启用/禁用功能
   - 支持站点连接测试和状态验证
   - 统计站点使用情况

3. **HTTP客户端 (HttpClient)**
   - 封装异步HTTP请求逻辑
   - 提供统一的请求日志记录和性能监控
   - 处理请求参数标准化

4. **数据模型 (Video)**
   - 定义统一的视频数据结构
   - 包含平台、标题、描述、播放源等字段
   - 支持数据序列化和反序列化

### 前端架构

- **核心框架**: Vue 3
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **HTTP客户端**: Axios

#### 核心功能模块

1. **视频搜索模块**
   - 提供搜索界面和结果展示
   - 支持并发搜索多个资源站
   - 实现搜索结果分页显示

2. **资源管理模块**
   - 展示所有视频资源站信息
   - 提供站点启用/禁用功能
   - 支持站点连接测试

## API 接口设计

### 视频搜索接口

- `GET /api/video/search`
  - 功能：搜索视频
  - 参数：query (关键词), page (页码), page_size (每页数量)

- `GET /api/video/search/{site_id}`
  - 功能：搜索指定站点的视频
  - 参数：site_id (站点ID), query (关键词), page (页码)

### 资源管理接口

- `GET /api/resource/sites`
  - 功能：获取所有资源站信息

- `POST /api/resource/sites/{site_id}/toggle`
  - 功能：切换资源站启用状态

- `POST /api/resource/sites/{site_id}/test`
  - 功能：测试资源站连接

## 配置管理

系统通过 `resource_sites.json` 文件管理所有视频资源站的配置信息，包括：
- 站点ID和名称
- API基础URL
- 启用状态
- 请求超时时间
- 搜索参数配置

## 部署说明

1. 后端服务默认运行在 5000 端口
2. 前端服务默认运行在 5173 端口
3. 可通过 `start_backend.bat` 和 `start_frontend.bat` 启动服务