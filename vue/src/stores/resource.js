import { ref, computed } from "vue";
import { defineStore } from "pinia";
import {
	getResourceSites,
	toggleSiteStatus,
	testSiteConnection,
} from "@/services/api";

export const useResourceStore = defineStore("resource", () => {
	// 状态
	const sites = ref([]);
	const isLoading = ref(false);
	const error = ref(null);
	const testingStates = ref({}); // 记录各站点的测试状态
	const isBatchTesting = ref(false); // 批量测试状态

	// 计算属性
	const enabledSites = computed(() => {
		return sites.value.filter((site) => site.enabled);
	});

	const stats = computed(() => {
		return {
			total: sites.value.length,
			enabled: enabledSites.value.length,
			disabled: sites.value.filter((site) => !site.enabled).length,
		};
	});

	// 动作
	const fetchSites = async () => {
		try {
			isLoading.value = true;
			error.value = null;

			const response = await getResourceSites();
			sites.value = response.sites || [];
		} catch (err) {
			error.value = err.message || "获取资源站点失败";
			console.error("获取资源站点失败:", err);
		} finally {
			isLoading.value = false;
		}
	};

	const toggleSite = async (siteId) => {
		try {
			const site = sites.value.find((s) => s.site_id === siteId);
			if (!site) {
				throw new Error("站点不存在");
			}

			// 乐观更新
			const originalStatus = site.enabled;
			site.enabled = !site.enabled;

			try {
				const response = await toggleSiteStatus(siteId);
				// 确保状态与服务器同步
				site.enabled = response.enabled;
			} catch (err) {
				// 回滚状态
				site.enabled = originalStatus;
				throw err;
			}
		} catch (err) {
			error.value = err.message || "切换站点状态失败";
			console.error("切换站点状态失败:", err);
			throw err;
		}
	};

	const testSite = async (siteId) => {
		try {
			// 设置测试状态
			testingStates.value[siteId] = { testing: true, result: null };

			const result = await testSiteConnection(siteId);

			// 更新测试结果
			testingStates.value[siteId] = {
				testing: false,
				result: result,
				timestamp: Date.now(),
			};

			return result;
		} catch (err) {
			// 更新测试错误
			testingStates.value[siteId] = {
				testing: false,
				result: {
					success: false,
					error: err.message || "测试失败",
				},
				timestamp: Date.now(),
			};

			console.error("测试站点连接失败:", err);
			throw err;
		}
	};

	const testAllSites = async () => {
		try {
			// 设置批量测试状态
			isBatchTesting.value = true;

			// 只测试已启用的站点
			const enabledSitesList = enabledSites.value;

			if (enabledSitesList.length === 0) {
				throw new Error("没有已启用的站点可供测试");
			}

			// 清空之前的测试结果（内联clearAllTestResults功能）
			testingStates.value = {};

			// 并发测试所有启用的站点
			const testPromises = enabledSitesList.map((site) =>
				testSite(site.site_id).catch((error) => ({
					siteId: site.site_id,
					error: error.message,
				}))
			);

			const results = await Promise.allSettled(testPromises);

			// 统计测试结果
			let successCount = 0;
			let failureCount = 0;

			results.forEach((result, index) => {
				const siteId = enabledSitesList[index].site_id;
				const testState = getSiteTestState(siteId);

				if (testState.result && testState.result.success) {
					successCount++;
				} else {
					failureCount++;
				}
			});

			return {
				total: enabledSitesList.length,
				success: successCount,
				failure: failureCount,
				results: results,
			};
		} catch (err) {
			console.error("批量测试站点连接失败:", err);
			throw err;
		} finally {
			isBatchTesting.value = false;
		}
	};

	const getSiteTestState = (siteId) => {
		return testingStates.value[siteId] || { testing: false, result: null };
	};

	const clearError = () => {
		error.value = null;
	};

	return {
		// 状态
		sites,
		isLoading,
		error,
		testingStates,
		isBatchTesting,

		// 计算属性
		enabledSites,
		stats,

		// 动作
		fetchSites,
		toggleSite,
		testSite,
		testAllSites,
		getSiteTestState,
		clearError,
	};
});
