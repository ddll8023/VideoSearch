import { ref, computed, watch } from "vue";
import { defineStore } from "pinia";

export const useSearchStore = defineStore("search", () => {
	// 搜索状态
	const searchKeyword = ref("");
	const searchResults = ref({});
	const activeTab = ref("");
	const isSearching = ref(false);
	const isPaginating = ref(false);
	const searchError = ref(null);

	// 分页信息 - 为每个tab维护独立的分页状态（内部私有）
	const tabPagination = ref({});
	const pageSize = 20;

	// 过滤统计信息 - 为每个tab维护独立的统计状态（内部私有）
	const tabStatistics = ref({});

	// 站点名称到站点ID的映射（内部私有）
	const siteIdMapping = ref({});

	// 本地存储相关
	const STORAGE_KEY = "videoSearch_state";
	const STORAGE_EXPIRY = 2 * 60 * 60 * 1000; // 2小时过期

	// 计算属性
	const hasSearchResults = computed(() => {
		return Object.keys(searchResults.value).length > 0;
	});

	const availableTabs = computed(() => {
		return Object.keys(searchResults.value).map((platform) => ({
			id: platform,
			name: platform,
			count:
				tabPagination.value[platform]?.total_count ||
				searchResults.value[platform]?.total_count ||
				0,
		}));
	});

	const currentTabResults = computed(() => {
		if (!activeTab.value || !searchResults.value[activeTab.value]) {
			return [];
		}

		const tabData = searchResults.value[activeTab.value];
		const pagination = tabPagination.value[activeTab.value];

		if (!pagination) {
			// 如果没有分页信息，返回前20个结果
			return tabData.slice(0, pageSize);
		}

		// 检查是否是替换模式的数据（当前页数据）
		// 如果数据长度等于page_size且不是第一页，说明是替换模式
		if (tabData.length <= pageSize && pagination.current_page > 1) {
			// 替换模式：直接返回存储的当前页数据
			return tabData;
		}

		// 追加模式：根据当前页返回对应的数据切片
		const startIndex = (pagination.current_page - 1) * pageSize;
		const endIndex = startIndex + pageSize;
		return tabData.slice(startIndex, endIndex);
	});

	// 当前tab的分页信息
	const currentTabPagination = computed(() => {
		if (!activeTab.value || !tabPagination.value[activeTab.value]) {
			return {
				current_page: 1,
				page_size: pageSize,
				total_count: 0,
				total_pages: 0,
			};
		}
		return tabPagination.value[activeTab.value];
	});

	// 当前tab的统计信息
	const currentTabStatistics = computed(() => {
		if (!activeTab.value || !tabStatistics.value[activeTab.value]) {
			return {
				original_count: 0,
				filtered_count: 0,
				display_count: 0,
			};
		}
		return tabStatistics.value[activeTab.value];
	});

	// 动作
	const setSearchKeyword = (keyword) => {
		searchKeyword.value = keyword;
	};

	const setActiveTab = (tab, resetToFirstPage = true) => {
		activeTab.value = tab;

		// 切换tab时处理分页信息
		if (resetToFirstPage && tab && searchResults.value[tab]) {
			// 如果该tab已有分页信息，只重置当前页码，保留其他分页信息
			if (tabPagination.value[tab]) {
				tabPagination.value[tab].current_page = 1;
			} else {
				// 如果没有分页信息，则进行初始化（通常不会执行到这里，因为addSiteResult会设置分页信息）
				const totalCount = searchResults.value[tab].total_count;
				const totalPages = Math.ceil(totalCount / pageSize) || 1;

				tabPagination.value[tab] = {
					current_page: 1,
					page_size: pageSize,
					total_count: totalCount,
					total_pages: totalPages,
				};
			}
		}
	};

	const setSearching = (status) => {
		isSearching.value = status;
	};

	const setPaginating = (status) => {
		isPaginating.value = status;
	};

	const setSearchError = (error) => {
		searchError.value = error;
	};

	const clearSearch = () => {
		searchKeyword.value = "";
		searchResults.value = {};
		activeTab.value = "";
		searchError.value = null;
		tabPagination.value = {};
		tabStatistics.value = {};
		siteIdMapping.value = {};
		clearLocalStorage();

		console.log("搜索状态已清空");
	};

	// 新增：仅清空搜索结果但保留关键词的方法
	const clearSearchResults = () => {
		searchResults.value = {};
		activeTab.value = "";
		searchError.value = null;
		tabStatistics.value = {};
		siteIdMapping.value = {};

		console.log("搜索结果已清空，保留关键词");
	};

	const addSiteResult = (siteData) => {
		const {
			site_id,
			site_name,
			videos,
			pagination,
			total_count,
			replace = false,
		} = siteData;
		if (videos && videos.length > 0) {
			// 记录站点ID和站点名称的映射关系
			if (site_id && site_name) {
				siteIdMapping.value[site_name] = site_id;
			}

			// 创建新的searchResults对象来确保响应性
			const newResults = { ...searchResults.value };

			// 如果该平台还没有结果，初始化
			if (!newResults[site_name]) {
				newResults[site_name] = [];
			}

			if (replace) {
				// 替换模式：直接替换当前页的数据
				newResults[site_name] = videos;
			} else {
				// 追加模式：添加新的视频到对应平台
				newResults[site_name].push(...videos);
			}

			// 更新searchResults，触发响应式更新
			searchResults.value = newResults;

			// 设置分页信息（内联setTabPagination功能）
			if (pagination) {
				if (!tabPagination.value[site_name]) {
					tabPagination.value[site_name] = {};
				}
				tabPagination.value[site_name] = {
					...tabPagination.value[site_name],
					...pagination,
					total_count: total_count,
				};
			} else if (!replace) {
				// 只在非替换模式下计算本地分页信息
				const totalCount = newResults[site_name].length;
				const totalPages = Math.ceil(totalCount / pageSize) || 1;

				if (!tabPagination.value[site_name]) {
					tabPagination.value[site_name] = {};
				}
				tabPagination.value[site_name] = {
					...tabPagination.value[site_name],
					current_page: 1,
					page_size: pageSize,
					total_count: total_count,
					total_pages: totalPages,
				};
			}

			// 如果还没有活跃标签页，设置为第一个有结果的平台
			if (!activeTab.value) {
				activeTab.value = site_name;
			}

			console.log(
				`${replace ? "替换" : "添加"}站点结果: ${site_name}, 视频数量: ${
					videos.length
				}, 当前平台总数: ${Object.keys(newResults).length}${
					pagination
						? `, 分页信息: ${pagination.current_page}/${pagination.total_pages}`
						: ""
				}`
			);
		}
	};

	// 根据站点名称获取站点ID
	const getSiteIdByName = (siteName) => {
		return siteIdMapping.value[siteName] || siteName;
	};

	// 清除指定tab的数据
	const clearTabData = (tabName) => {
		if (searchResults.value[tabName]) {
			const newResults = { ...searchResults.value };
			delete newResults[tabName];
			searchResults.value = newResults;
		}

		if (tabPagination.value[tabName]) {
			const newPagination = { ...tabPagination.value };
			delete newPagination[tabName];
			tabPagination.value = newPagination;
		}

		console.log(`已清除tab数据: ${tabName}`);
	};

	// 保存状态到本地存储
	const saveToLocalStorage = () => {
		try {
			const state = {
				searchKeyword: searchKeyword.value,
				searchResults: searchResults.value,
				activeTab: activeTab.value,
				tabPagination: tabPagination.value,
				siteIdMapping: siteIdMapping.value,
				timestamp: Date.now(),
			};
			localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
		} catch (error) {
			console.warn("保存搜索状态到本地存储失败:", error);
		}
	};

	// 从本地存储恢复状态
	const loadFromLocalStorage = () => {
		try {
			const saved = localStorage.getItem(STORAGE_KEY);
			if (!saved) return false;

			const state = JSON.parse(saved);
			const now = Date.now();

			// 检查是否过期
			if (!state.timestamp || now - state.timestamp > STORAGE_EXPIRY) {
				localStorage.removeItem(STORAGE_KEY);
				return false;
			}

			// 恢复状态
			if (state.searchKeyword) searchKeyword.value = state.searchKeyword;
			if (state.searchResults) searchResults.value = state.searchResults;
			if (state.activeTab) activeTab.value = state.activeTab;
			if (state.tabPagination) tabPagination.value = state.tabPagination;
			if (state.siteIdMapping) siteIdMapping.value = state.siteIdMapping;

			console.log("已从本地存储恢复搜索状态");
			return true;
		} catch (error) {
			console.warn("从本地存储恢复搜索状态失败:", error);
			localStorage.removeItem(STORAGE_KEY);
			return false;
		}
	};

	// 清除本地存储
	const clearLocalStorage = () => {
		try {
			localStorage.removeItem(STORAGE_KEY);
		} catch (error) {
			console.warn("清除本地存储失败:", error);
		}
	};

	// 自动保存关键状态变化到本地存储
	watch(
		[searchKeyword, searchResults, activeTab, tabPagination],
		() => {
			// 只有当有搜索结果时才保存
			if (searchKeyword.value && Object.keys(searchResults.value).length > 0) {
				saveToLocalStorage();
			}
		},
		{ deep: true }
	);

	// 初始化时尝试从本地存储恢复状态
	loadFromLocalStorage();

	return {
		// 状态
		searchKeyword,
		searchResults,
		activeTab,
		isSearching,
		isPaginating,
		searchError,

		// 计算属性
		hasSearchResults,
		availableTabs,
		currentTabResults,
		currentTabPagination,

		// 动作
		setSearchKeyword,
		setActiveTab,
		setSearching,
		setPaginating,
		setSearchError,
		clearSearch,
		clearSearchResults,
		addSiteResult,
		getSiteIdByName,
		clearTabData,
		saveToLocalStorage,
		loadFromLocalStorage,
		clearLocalStorage,
	};
});
