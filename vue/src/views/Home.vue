<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useSearchStore } from '@/stores/search'
import { useResourceStore } from '@/stores/resource'
import { searchSingleSite } from '@/services/api'
import CommonSearch from '@/components/common/CommonSearch.vue'
import VideoCard from '@/components/video/VideoCard.vue'
import CommonTab from '@/components/common/CommonTab.vue'
import CommonPagination from '@/components/common/CommonPagination.vue'
import CommonCard from '@/components/common/CommonCard.vue'

const searchStore = useSearchStore()
const resourceStore = useResourceStore()
const hasSearched = ref(false)

// 搜索框状态
const searchInput = ref('')
const searchBoxRef = ref(null)

// 计算搜索框变体
const searchVariant = computed(() => hasSearched.value ? 'compact' : 'hero')

// 搜索框事件处理
const handleClear = () => {
    searchInput.value = ''
    handleClearRequest()
    // 聚焦搜索框
    nextTick(() => {
        searchBoxRef.value?.focus()
    })
}

// 通用异步操作处理器
const handleAsyncOperation = async (operation, loadingType = 'searching') => {
    try {
        // 设置加载状态
        if (loadingType === 'searching') {
            searchStore.setSearching(true)
        } else if (loadingType === 'paginating') {
            searchStore.setPaginating(true)
        }

        searchStore.setSearchError(null)

        // 执行异步操作
        await operation()

    } catch (error) {
        console.error('异步操作失败:', error)
        searchStore.setSearchError(error.message)
    } finally {
        // 重置加载状态
        if (loadingType === 'searching') {
            searchStore.setSearching(false)
        } else if (loadingType === 'paginating') {
            searchStore.setPaginating(false)
        }
    }
}

// 初始化搜索状态
const initializeSearch = async (keyword) => {
    searchStore.setSearchKeyword(keyword)
    searchStore.clearSearchResults()

    // 确保资源站数据已加载
    if (resourceStore.sites.length === 0) {
        await resourceStore.fetchSites()
    }

    const enabledSites = resourceStore.enabledSites
    if (enabledSites.length === 0) {
        throw new Error('没有可用的资源站')
    }

    hasSearched.value = true
    return enabledSites
}

// 处理单站点搜索结果
const processSiteSearchResult = (site, result) => {
    if (result.success && result.videos && result.videos.length > 0) {
        searchStore.addSiteResult({
            site_id: site.site_id,
            site_name: result.site_name || site.name,
            videos: result.videos,
            pagination: result.pagination,
            total_count: result.total_count,
            original_count: result.original_count || 0,
            filtered_count: result.filtered_count || 0,
            display_count: result.display_count || 0
        })
        return { success: true, videoCount: result.videos.length }
    }
    return { success: false, videoCount: 0 }
}

// 执行站点搜索
const executeSearch = async (keyword, enabledSites, page = 1) => {
    console.log(`开始并发搜索 ${enabledSites.length} 个资源站`)

    let completedSites = 0
    let successCount = 0
    let totalVideos = 0

    const searchPromises = enabledSites.map(async (site) => {
        try {
            console.log(`开始搜索站点: ${site.name} (${site.site_id})`)

            const result = await searchSingleSite(keyword, site.site_id, page, 20)
            console.log(`站点 ${site.name} 搜索完成:`, result)

            const processResult = processSiteSearchResult(site, result)
            if (processResult.success) {
                successCount++
                totalVideos += processResult.videoCount
            }

            completedSites++
            console.log(`进度: ${completedSites}/${enabledSites.length} 个站点已完成`)

            return {
                site_id: site.site_id,
                site_name: site.name,
                success: result.success,
                videos: result.videos || [],
                error: result.success ? null : result.error
            }
        } catch (error) {
            console.error(`站点 ${site.name} 搜索错误:`, error)
            completedSites++
            return {
                site_id: site.site_id,
                site_name: site.name,
                success: false,
                videos: [],
                error: error.message || '搜索失败'
            }
        }
    })

    const results = await Promise.allSettled(searchPromises)

    const finalSuccessCount = results.filter(r => r.status === 'fulfilled' && r.value.success).length
    const finalTotalVideos = results
        .filter(r => r.status === 'fulfilled')
        .reduce((sum, r) => sum + r.value.videos.length, 0)

    console.log(`搜索完成: ${finalSuccessCount}/${enabledSites.length} 个站点成功, 共找到 ${finalTotalVideos} 个视频`)
}

// 重新加载tab数据
const reloadTabData = async (tabId, keyword) => {
    console.log(`开始重新加载tab: ${tabId}`)

    // 清除该tab的数据以显示加载状态
    searchStore.clearTabData(tabId)

    // 切换到新tab
    searchStore.setActiveTab(tabId, true)

    // 获取当前tab对应的真实站点ID
    const siteId = searchStore.getSiteIdByName(tabId)

    // 重新请求该tab的数据
    const result = await searchSingleSite(keyword, siteId, 1, 20)

    if (result.success && result.videos && result.videos.length > 0) {
        searchStore.addSiteResult({
            site_id: siteId,
            site_name: result.site_name || tabId,
            videos: result.videos,
            pagination: result.pagination,
            total_count: result.total_count,
            original_count: result.original_count || 0,
            filtered_count: result.filtered_count || 0,
            display_count: result.display_count || 0
        })
        console.log(`tab ${tabId} 数据重新加载完成`)
    } else {
        throw new Error(result.error || '加载失败')
    }
}

// 加载分页数据
const loadPageData = async (keyword, currentTab, currentPage) => {
    console.log(`开始请求 ${currentTab} 的第 ${currentPage} 页数据`)

    // 获取当前tab对应的真实站点ID
    const siteId = searchStore.getSiteIdByName(currentTab)

    // 只请求当前tab对应的资源站
    const result = await searchSingleSite(keyword, siteId, currentPage, 20)

    if (result.success && result.videos) {
        // 使用后端返回的分页信息更新当前tab
        searchStore.addSiteResult({
            site_id: siteId,
            site_name: currentTab,
            videos: result.videos,
            pagination: result.pagination,
            total_count: result.pagination.total_count, // 确保总数量不丢失
            original_count: result.original_count || 0,
            filtered_count: result.filtered_count || 0,
            display_count: result.display_count || 0,
            replace: true // 标记为替换模式，不是追加模式
        })

        console.log(`${currentTab} 第 ${currentPage} 页数据加载完成`)
    } else {
        throw new Error(result.error || '加载失败')
    }
}

// 处理SearchBox组件发送的搜索请求
const handleSearchRequest = async (keyword, page = 1) => {
    console.log('开始分站点搜索:', keyword)

    // 更新URL参数以保持搜索状态
    const url = new URL(window.location)
    if (keyword) {
        url.searchParams.set('q', keyword)
    } else {
        url.searchParams.delete('q')
    }
    window.history.replaceState({}, '', url)

    await handleAsyncOperation(async () => {
        const enabledSites = await initializeSearch(keyword)
        console.log('启用的资源站:', enabledSites)

        await executeSearch(keyword, enabledSites, page)
    })
}

// 处理清空请求
const handleClearRequest = () => {
    hasSearched.value = false
    searchStore.clearSearch()
}

// 处理tab切换
const handleTabChange = async (tabId) => {
    console.log(`切换到tab: ${tabId}`)

    // 更新URL参数
    const url = new URL(window.location)
    url.searchParams.set('tab', tabId)
    url.searchParams.delete('page') // 切换tab时重置页码
    window.history.replaceState({}, '', url)

    // 如果切换到的tab没有数据，需要重新加载
    if (!searchStore.searchResults[tabId] || searchStore.searchResults[tabId].length === 0) {
        const keyword = searchStore.searchKeyword
        if (keyword) {
            await handleAsyncOperation(async () => {
                await reloadTabData(tabId, keyword)
            })
        }
    } else {
        // 如果tab有数据，直接切换并重置为第一页
        searchStore.setActiveTab(tabId, true)
    }
}

// 分页页码状态
const paginatingPage = ref(1)

// 处理分页变化
const handlePageChange = async (pageInfo) => {
    const { currentPage } = pageInfo
    const keyword = searchStore.searchKeyword
    const currentTab = searchStore.activeTab

    if (!keyword || !currentTab) {
        return
    }

    // 更新URL参数
    const url = new URL(window.location)
    if (currentPage > 1) {
        url.searchParams.set('page', currentPage.toString())
    } else {
        url.searchParams.delete('page')
    }
    window.history.replaceState({}, '', url)

    paginatingPage.value = currentPage

    await handleAsyncOperation(async () => {
        await loadPageData(keyword, currentTab, currentPage)
    }, 'paginating')
}

onMounted(() => {
    // 自动聚焦搜索框
    searchBoxRef.value?.focus()

    // 从URL参数获取状态
    const urlParams = new URLSearchParams(window.location.search)
    const urlKeyword = urlParams.get('q')
    const urlTab = urlParams.get('tab')
    const urlPage = urlParams.get('page')

    // 检查是否有有效的搜索状态（本地存储已在store初始化时自动恢复）
    if (searchStore.searchKeyword && searchStore.hasSearchResults) {
        // 如果store中有搜索状态，恢复UI状态
        searchInput.value = searchStore.searchKeyword
        hasSearched.value = true

        // 检查URL参数是否与store状态一致，不一致则以URL为准
        if (urlKeyword && urlKeyword !== searchStore.searchKeyword) {
            // URL中有不同的搜索关键词，重新搜索
            searchInput.value = urlKeyword
            handleSearchRequest(urlKeyword)
            return
        }

        // 恢复tab状态
        if (urlTab && searchStore.searchResults[urlTab]) {
            searchStore.setActiveTab(urlTab, false)
        }

        // 恢复页码状态
        if (urlPage && parseInt(urlPage) > 1) {
            const pageNum = parseInt(urlPage)
            const currentTab = searchStore.activeTab
            if (currentTab && searchStore.searchResults[currentTab]) {
                const currentPagination = searchStore.currentTabPagination
                if (currentPagination.current_page !== pageNum) {
                    handlePageChange({ currentPage: pageNum })
                }
            }
        }
    } else if (urlKeyword) {
        // 没有store状态但有URL参数，按URL参数搜索
        searchInput.value = urlKeyword
        handleSearchRequest(urlKeyword)
    }
})

onUnmounted(() => {
    // 移除状态清理，保持搜索结果
    // searchStore.clearSearch()
})
</script>

<template>
    <div :class="['home-page', { 'centered': !hasSearched }]">
        <!-- 页面标题 -->
        <h1 :class="[
            'home-page__title',
            { 'home-page__title--centered': !hasSearched, 'home-page__title--compact': hasSearched }
        ]">影视聚合搜索</h1>

        <!-- 搜索容器 -->
        <div :class="[
            'search-container',
            { 'centered': !hasSearched, 'top': hasSearched }
        ]">
            <!-- 搜索框组件 -->
            <CommonSearch ref="searchBoxRef" v-model="searchInput" :variant="searchVariant" placeholder="请输入要搜索的视频名称..."
                :loading="searchStore.isSearching" :disabled="searchStore.isSearching" :autofocus="true"
                @search="handleSearchRequest" @clear="handleClear" />
        </div>

        <!-- 搜索结果区域 -->
        <div v-if="hasSearched" class="results-section">
            <div class="results-container">
                <!-- 错误信息 -->
                <div v-if="searchStore.searchError && !searchStore.hasSearchResults" class="error-message">
                    <h3 class="message-title">搜索失败</h3>
                    <p class="message-text">{{ searchStore.searchError }}</p>
                    <button @click="handleSearchRequest(searchStore.searchKeyword)" class="retry-btn">重试</button>
                </div>

                <!-- 搜索结果 - 有结果时优先显示，支持流式搜索实时展示 -->
                <div v-else-if="searchStore.hasSearchResults" class="search-results">
                    <!-- 标签页 -->
                    <CommonTab :tabs="searchStore.availableTabs" :active-tab="searchStore.activeTab"
                        @tab-change="handleTabChange" />

                    <!-- 搜索进行中的提示 -->
                    <div v-if="searchStore.isSearching" class="searching-hint">
                        <p>正在搜索更多资源站点...</p>
                    </div>

                    <!-- 分页加载提示 -->
                    <div v-if="searchStore.isPaginating" class="paginating-hint">
                        <p>正在加载第 {{ paginatingPage }} 页数据...</p>
                    </div>

                    <!-- 数据统计信息 -->
                    <div v-if="searchStore.currentTabStatistics.original_count > 0" class="statistics-container">
                        <CommonCard>
                            <div class="statistics-content">
                                <div class="statistics-title">数据统计</div>
                                <div class="statistics-details">
                                    <span class="statistics-item">
                                        原始数据：<strong>{{ searchStore.currentTabStatistics.original_count }}</strong> 条
                                    </span>
                                    <span class="statistics-item">
                                        过滤后：<strong>{{ searchStore.currentTabStatistics.display_count }}</strong> 条
                                    </span>
                                    <span class="statistics-item">
                                        已过滤：<strong>{{ searchStore.currentTabStatistics.filtered_count }}</strong> 条
                                    </span>
                                </div>
                            </div>
                        </CommonCard>
                    </div>

                    <!-- 横向滚动视频列表 -->
                    <div class="video-grid-container">
                        <div class="video-grid">
                            <VideoCard v-for="video in searchStore.currentTabResults"
                                :key="`${video.platform}-${video.id}`" :video="video" />
                        </div>
                    </div>

                    <!-- 分页组件 -->
                    <div v-if="searchStore.currentTabPagination.total_pages > 1" class="pagination-container">
                        <CommonPagination :current-page="searchStore.currentTabPagination.current_page"
                            :total-pages="searchStore.currentTabPagination.total_pages"
                            :show-input="searchStore.currentTabPagination.total_pages > 10" :size="'base'"
                            :compact="true" :disabled="searchStore.isPaginating" @pagechange="handlePageChange" />
                    </div>


                </div>

                <!-- 纯加载状态 - 仅在搜索中且无结果时显示 -->
                <div v-else-if="searchStore.isSearching" class="loading-state">
                    <div class="loading-lines">
                        <div class="loading-line"></div>
                        <div class="loading-line"></div>
                        <div class="loading-line"></div>
                    </div>
                    <div class="loading-content">
                        <p class="loading-text">正在搜索中...</p>
                    </div>
                </div>

                <!-- 无结果状态 -->
                <div v-else class="no-results">
                    <h3 class="message-title">没有找到相关内容</h3>
                    <p class="message-text">请尝试其他关键词或检查拼写</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.home-page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    padding-top: var(--header-height);
    background-color: var(--bg-primary);

    &.centered {
        justify-content: center;
    }
}

.home-page__title {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-bold);
    text-align: center;
    color: var(--text-primary);
    transition: font-size var(--transition-base), margin var(--transition-base);

    &--centered {
        font-size: var(--font-size-3xl);
        margin-bottom: var(--spacing-xl);
    }

    &--compact {
        font-size: var(--font-size-2xl);
        margin-bottom: var(--spacing-base);
    }
}

.search-container {
    transition: all var(--transition-slow);
    width: 100%;

    &.centered {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-xl);
    }

    &.top {
        background-color: var(--bg-primary);
        border-bottom: 1px solid var(--border-light);
        padding: var(--spacing-xl) var(--spacing-base);
        display: flex;
        justify-content: center;
    }
}

.results-section {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.results-container {

    margin: 0 var(--spacing-xl);
    padding: 0 var(--spacing-base);
}

.search-results {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.error-message,
.no-results {
    background-color: var(--bg-primary);
    border-radius: var(--border-radius-large);
    padding: var(--spacing-3xl);
    margin-bottom: var(--spacing-xl);
    text-align: center;
    border: 1px solid var(--border-light);
}

.message-title {
    margin-bottom: var(--spacing-base);
    color: var(--text-primary);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
}

.message-text {
    margin-bottom: var(--spacing-large);
    color: var(--text-secondary);
    line-height: var(--line-height-base);
}

.retry-btn {
    background-color: var(--primary-color);
    color: white;
    padding: var(--spacing-small) var(--spacing-large);
    border: none;
    border-radius: var(--border-radius-base);
    cursor: pointer;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    transition: background-color var(--transition-base);

    &:hover {
        background-color: var(--primary-dark);
    }

    &:active {
        background-color: var(--primary-dark);
        transform: translateY(1px);
    }
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-3xl);
    text-align: center;
}

.loading-text {
    color: var(--text-secondary);
    margin-top: var(--spacing-base);
    font-size: var(--font-size-base);
}

.loading-lines {
    display: flex;
    gap: 4px;

    .loading-line {
        width: 3px;
        height: 20px;
        background: var(--text-secondary);
        animation: loading-lines 1.2s ease-in-out infinite;

        &:nth-child(1) {
            animation-delay: -0.4s;
        }

        &:nth-child(2) {
            animation-delay: -0.2s;
        }
    }
}



.video-grid-container {
    padding: 0 var(--spacing-base) var(--spacing-base);
}

.video-grid {
    display: grid;
    gap: var(--spacing-base);
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));

    @include respond-to(md) {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    }

    @include respond-to(sm) {
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: var(--spacing-small);
    }
}

.pagination-container {
    display: flex;
    justify-content: center;
    padding: var(--spacing-xl) var(--spacing-base);
    margin-top: var(--spacing-base);
    border-top: 1px solid var(--border-light);

    @include respond-to(sm) {
        padding: var(--spacing-large) var(--spacing-small);
    }
}



.loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-base);
}

.searching-hint {
    text-align: center;
    padding: var(--spacing-base);
    background: var(--bg-tertiary);
    border-radius: var(--radius-base);
    border: 1px solid var(--border-light);

    p {
        margin: 0;
        color: var(--text-secondary);
        font-size: var(--font-size-small);
    }
}

.paginating-hint {
    text-align: center;
    padding: var(--spacing-base);
    background: var(--bg-tertiary);
    border-radius: var(--radius-base);
    border: 1px solid var(--border-light);

    p {
        margin: 0;
        color: var(--text-secondary);
        font-size: var(--font-size-small);
    }
}

.statistics-container {
    margin-bottom: var(--spacing-base);
    padding: 0 var(--spacing-base);
}

.statistics-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-small);
}

.statistics-title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    margin-bottom: var(--spacing-small);
}

.statistics-details {
    display: flex;
    gap: var(--spacing-large);
    flex-wrap: wrap;

    @include respond-to(sm) {
        flex-direction: column;
        gap: var(--spacing-small);
    }
}

.statistics-item {
    font-size: var(--font-size-small);
    color: var(--text-secondary);

    strong {
        color: var(--text-primary);
        font-weight: var(--font-weight-medium);
    }
}

// 减少动画模式
@media (prefers-reduced-motion: reduce) {
    * {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
    }
}
</style>