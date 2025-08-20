import axios from "axios";

// 创建axios实例
const api = axios.create({
	baseURL: "http://localhost:5000",
	timeout: 30000,
	headers: {
		"Content-Type": "application/json",
	},
});

// 响应拦截器
api.interceptors.response.use(
	(response) => {
		return response.data;
	},
	(error) => {
		// 处理HTTP错误响应
		if (error.response) {
			const errorData = error.response.data;
			// 如果是后端返回的标准错误格式
			if (errorData && typeof errorData === "object" && !errorData.success) {
				return Promise.reject(new Error(errorData.message || "请求失败"));
			}
			// HTTP状态码错误
			return Promise.reject(new Error(`请求失败 (${error.response.status})`));
		}
		// 网络错误或请求超时
		const errorMessages = {
			ECONNABORTED: "请求超时，请检查网络连接",
			ETIMEDOUT: "请求超时，请稍后重试",
			ERR_NETWORK: "网络连接失败，请检查后端服务是否启动",
			ERR_BAD_RESPONSE: "服务器响应格式错误",
			ERR_BAD_REQUEST: "请求格式错误",
		};

		if (errorMessages[error.code]) {
			return Promise.reject(new Error(errorMessages[error.code]));
		}
		// 其他错误
		const errorMessage = error.message || "网络请求失败";
		return Promise.reject(new Error(errorMessage));
	}
);

/**
 * 搜索单个资源站视频
 * @param {string} wd - 搜索关键词
 * @param {string} siteId - 资源站ID
 * @param {number} page - 页码，默认1
 * @param {number} pageSize - 每页数量，默认20
 * @returns {Promise} 搜索结果
 */
export const searchSingleSite = async (wd, siteId, page = 1, pageSize = 20) => {
	try {
		// 参数验证
		if (!wd || typeof wd !== "string" || !wd.trim()) {
			throw new Error("搜索关键词不能为空");
		}

		if (!siteId || typeof siteId !== "string" || !siteId.trim()) {
			throw new Error("资源站ID不能为空");
		}

		const response = await api.get("/api/video/search", {
			params: {
				wd: wd.trim(),
				site_id: siteId.trim(),
				page: Math.max(1, parseInt(page) || 1),
				pageSize: Math.max(1, Math.min(100, parseInt(pageSize) || 20)),
			},
		});

		// 后端响应拦截器已经返回response.data，且成功时success为true
		if (response.success) {
			// 确保返回的数据包含分页信息
			const data = response.data;
			if (data.pagination) {
				return data;
			} else {
				// 如果后端没有返回分页信息，前端构造一个基本的分页信息
				return {
					...data,
					pagination: {
						current_page: page,
						page_size: pageSize,
						total_count: data.total_count || 0,
						total_pages: Math.ceil((data.total_count || 0) / pageSize) || 1,
						has_next: false,
						has_previous: false,
						next_page: null,
						previous_page: null,
					},
				};
			}
		} else {
			throw new Error(response.message || "搜索失败");
		}
	} catch (error) {
		console.error("搜索单个资源站失败:", error);
		throw error;
	}
};

/**
 * 获取资源站点信息
 * @returns {Promise} 站点信息
 */
export const getResourceSites = async () => {
	try {
		const response = await api.get("/api/resource/sites");
		return response.data;
	} catch (error) {
		console.error("获取资源站点信息失败:", error);
		throw error;
	}
};

/**
 * 切换资源站点状态
 * @param {string} siteId - 站点ID
 * @returns {Promise} 切换结果
 */
export const toggleSiteStatus = async (siteId) => {
	try {
		const response = await api.post(`/api/resource/sites/${siteId}/toggle`);
		return response.data;
	} catch (error) {
		console.error("切换站点状态失败:", error);
		throw error;
	}
};

/**
 * 测试站点连接
 * @param {string} siteId - 站点ID
 * @returns {Promise} 测试结果
 */
export const testSiteConnection = async (siteId) => {
	try {
		const response = await api.post(`/api/resource/sites/${siteId}/test`);
		return response.data;
	} catch (error) {
		console.error("测试站点连接失败:", error);
		throw error;
	}
};

/**
 * 获取视频详情信息
 * @param {string} keyword - 搜索关键词
 * @param {number} page - 页码
 * @param {string} siteId - 资源站ID
 * @param {string} vodId - 视频ID
 * @returns {Promise} 视频详情结果
 */
export const getVideoDetail = async (keyword, page, siteId, vodId) => {
	try {
		// 参数验证
		if (!keyword || typeof keyword !== "string" || !keyword.trim()) {
			throw new Error("搜索关键词不能为空");
		}

		if (!siteId || typeof siteId !== "string" || !siteId.trim()) {
			throw new Error("资源站ID不能为空");
		}

		if (!vodId || typeof vodId !== "string" || !vodId.trim()) {
			throw new Error("视频ID不能为空");
		}

		const response = await api.get("/api/video/detail", {
			params: {
				keyword: keyword.trim(),
				page: Math.max(1, parseInt(page) || 1),
				site_id: siteId.trim(),
				vod_id: vodId.trim(),
			},
		});

		// 后端响应拦截器已经返回response.data，且成功时success为true
		if (response.success) {
			return response.data;
		} else {
			throw new Error(response.message || "获取视频详情失败");
		}
	} catch (error) {
		console.error("获取视频详情失败:", error);
		throw error;
	}
};

export default api;
