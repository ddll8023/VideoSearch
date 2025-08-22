<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useResourceStore } from '@/stores/resource'
import CommonSwitch from '@/components/common/CommonSwitch.vue'
import CommonCard from '@/components/common/CommonCard.vue'
import AppHeader from '@/components/user/AppHeader.vue'

const resourceStore = useResourceStore()
const saveMessage = ref('')
const refreshInterval = ref(null)

// 切换站点状态
const handleToggleSite = async (siteId) => {
    try {
        await resourceStore.toggleSite(siteId)
        showMessage('站点状态已更新')
    } catch (error) {
        showMessage('切换失败: ' + error.message, 'error')
    }
}

// 测试站点连接
const handleTestSite = async (siteId) => {
    try {
        const result = await resourceStore.testSite(siteId)
        if (result.success) {
            showMessage(`连接成功 (${result.elapsed_ms}ms)`)
        } else {
            showMessage(`连接失败: ${result.message}`, 'error')
        }
    } catch (error) {
        showMessage('测试失败: ' + error.message, 'error')
    }
}

// 测试所有站点连接
const handleTestAllSites = async () => {
    try {
        if (resourceStore.stats.enabled === 0) {
            showMessage('没有已启用的站点可供测试', 'error')
            return
        }

        showMessage(`开始测试 ${resourceStore.stats.enabled} 个启用站点的连接...`)
        const results = await resourceStore.testAllSites()

        if (results.success === results.total) {
            showMessage(`所有站点测试完成！全部 ${results.total} 个站点连接正常`)
        } else if (results.failure === results.total) {
            showMessage(`所有站点测试完成！全部 ${results.total} 个站点连接失败`, 'error')
        } else {
            showMessage(`所有站点测试完成！${results.success} 个成功，${results.failure} 个失败`)
        }
    } catch (error) {
        showMessage('批量测试失败: ' + error.message, 'error')
    }
}

// 刷新站点列表
const handleRefresh = async () => {
    try {
        await resourceStore.fetchSites()
        showMessage('站点列表已刷新')
    } catch (error) {
        showMessage('刷新失败: ' + error.message, 'error')
    }
}

// 显示消息
const showMessage = (message, type = 'success') => {
    saveMessage.value = { text: message, type }
    setTimeout(() => {
        saveMessage.value = ''
    }, 3000)
}

onMounted(async () => {
    await resourceStore.fetchSites()

    // 设置定期刷新
    refreshInterval.value = setInterval(() => {
        if (!resourceStore.isLoading) {
            resourceStore.fetchSites()
        }
    }, 30000) // 30秒刷新一次
})

onUnmounted(() => {
    if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
    }
})
</script>

<template>
    <div class="app-layout">
        <!-- 应用头部 -->
        <AppHeader />

        <div class="settings-page">
            <div class="container">
                <div class="page-header">
                    <h1>设置</h1>
                    <div class="actions">
                        <button @click="handleTestAllSites" class="test-all-btn"
                            :disabled="resourceStore.isLoading || resourceStore.isBatchTesting || resourceStore.stats.enabled === 0">
                            {{ resourceStore.isBatchTesting ? '测试中...' : '测试所有连接' }}
                        </button>
                        <button @click="handleRefresh" class="refresh-btn" :disabled="resourceStore.isLoading">
                            刷新站点
                        </button>
                    </div>
                </div>

                <!-- 消息提示 -->
                <div v-if="saveMessage" :class="['message', `message--${saveMessage.type || 'success'}`]">
                    {{ saveMessage.text }}
                </div>

                <!-- 错误提示 -->
                <div v-if="resourceStore.error" class="message message--error">
                    {{ resourceStore.error }}
                    <button @click="resourceStore.clearError" class="message-close">×</button>
                </div>

                <!-- 资源站点设置 -->
                <div class="settings-section">
                    <div class="section-header">
                        <h2>资源站点配置</h2>
                        <p>管理视频资源站点，启用或禁用特定站点</p>
                        <div class="stats">
                            <span class="stat-item">
                                总计: {{ resourceStore.stats.total }}
                            </span>
                            <span class="stat-item stat-enabled">
                                已启用: {{ resourceStore.stats.enabled }}
                            </span>
                            <span class="stat-item stat-disabled">
                                已禁用: {{ resourceStore.stats.disabled }}
                            </span>
                        </div>
                    </div>

                    <div v-if="resourceStore.isLoading" class="loading-state">
                        <div class="loading-spinner"></div>
                        <p>加载中...</p>
                    </div>

                    <div v-else-if="resourceStore.sites.length === 0" class="empty-state">
                        <p>暂无资源站点配置</p>
                        <button @click="handleRefresh" class="refresh-btn">重新加载</button>
                    </div>

                    <div v-else class="site-grid-container">
                        <div class="site-grid">
                            <CommonCard v-for="site in resourceStore.sites" :key="site.site_id">

                                <!-- 站点名称 - Header -->
                                <template #header>
                                    <div class="site-card-header">
                                        <h3 class="site-name">{{ site.name }}</h3>
                                        <span
                                            :class="['site-status', site.enabled ? 'status-enabled' : 'status-disabled']">
                                            {{ site.enabled ? '已启用' : '已禁用' }}
                                        </span>
                                    </div>
                                </template>

                                <!-- 站点详情 - Body -->
                                <div class="site-card-body">
                                    <div class="site-details">
                                        <div class="site-detail-item">
                                            <span class="site-detail-label">站点ID:</span>
                                            <span class="site-id">{{ site.site_id }}</span>
                                        </div>
                                        <div class="site-detail-item">
                                            <span class="site-detail-label">地址:</span>
                                            <span class="site-url">{{ site.base_url }}</span>
                                        </div>
                                    </div>

                                    <!-- 测试结果 -->
                                    <div v-if="resourceStore.getSiteTestState(site.site_id).result" class="test-result">
                                        <span
                                            :class="['test-text', resourceStore.getSiteTestState(site.site_id).result?.success ? 'test-success' : 'test-error']">
                                            {{ resourceStore.getSiteTestState(site.site_id).result?.success
                                                ? `连接正常
                                            (${resourceStore.getSiteTestState(site.site_id).result.elapsed_ms}ms)`
                                                : `连接失败: ${resourceStore.getSiteTestState(site.site_id).result.error ||
                                                resourceStore.getSiteTestState(site.site_id).result.message}` }}
                                        </span>
                                    </div>
                                </div>

                                <!-- 操作按钮 - Footer -->
                                <template #footer>
                                    <div class="site-actions">
                                        <div class="action-group">
                                            <span class="action-label">启用状态:</span>
                                            <CommonSwitch :model-value="site.enabled"
                                                @update:model-value="handleToggleSite(site.site_id)" size="base" />
                                        </div>
                                        <button @click="handleTestSite(site.site_id)"
                                            :disabled="resourceStore.getSiteTestState(site.site_id).testing"
                                            class="test-btn">
                                            {{ resourceStore.getSiteTestState(site.site_id).testing ? '测试中...' : '测试连接'
                                            }}
                                        </button>
                                    </div>
                                </template>
                            </CommonCard>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.app-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.settings-page {
    flex: 1;
    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
    padding: var(--spacing-2xl) var(--spacing-base);
    padding-top: calc(var(--spacing-2xl) + var(--header-height));
}

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-2xl);
    padding: var(--spacing-xl);
    background: var(--bg-primary);
    border-radius: var(--border-radius-large);
    box-shadow: var(--box-shadow-card);
    border: 1px solid var(--border-light);

    h1 {
        font-size: var(--font-size-3xl);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .actions {
        display: flex;
        gap: var(--spacing-base);
    }
}

.refresh-btn,
.test-btn,
.test-all-btn {
    @include button-base;
}

.refresh-btn {
    background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
    color: var(--text-primary);
    border: 1px solid var(--border-light);
    box-shadow: var(--box-shadow-small);

    &:hover:not(:disabled) {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        color: var(--text-white);
        border-color: var(--primary-color);
        box-shadow: var(--box-shadow-base);
        transform: translateY(-1px);
    }
}

.test-all-btn {
    background: linear-gradient(135deg, var(--success-color), rgba(5, 150, 105, 0.8));
    color: var(--text-white);
    border: 1px solid var(--success-color);
    box-shadow: var(--box-shadow-small);

    &:hover:not(:disabled) {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        border-color: var(--primary-color);
        box-shadow: var(--box-shadow-base);
        transform: translateY(-1px);
    }
}

.test-btn {
    background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
    color: var(--text-primary);
    border: 1px solid var(--border-light);
    font-size: var(--font-size-mini);
    padding: var(--spacing-mini) var(--spacing-small);
    box-shadow: var(--box-shadow-small);

    &:hover:not(:disabled) {
        background: linear-gradient(135deg, var(--info-color), var(--primary-light));
        color: var(--text-white);
        border-color: var(--info-color);
        box-shadow: var(--box-shadow-base);
        transform: translateY(-1px);
    }
}

.message {
    padding: var(--spacing-base) var(--spacing-large);
    border-radius: var(--border-radius-base);
    margin-bottom: var(--spacing-xl);
    text-align: center;
    animation: slideIn 0.3s ease-out;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-base);
    font-weight: var(--font-weight-medium);
    box-shadow: var(--box-shadow-base);

    &--success {
        @include status-variant('success');
        border: 1px solid;
    }

    &--error {
        @include status-variant('danger');
        border: 1px solid;
    }
}

.message-close {
    background: none;
    border: none;
    font-size: var(--font-size-large);
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--border-radius-full);
    transition: all var(--transition-fast);

    &:hover {
        background: rgba(0, 0, 0, 0.1);
        transform: scale(1.1);
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-20px) scale(0.95);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.settings-section {
    background: var(--bg-primary);
    border-radius: var(--border-radius-large);
    box-shadow: var(--box-shadow-card);
    margin-bottom: var(--spacing-2xl);
    overflow: hidden;
    border: 1px solid var(--border-light);
    transition: all var(--transition-base);

    &:hover {
        box-shadow: var(--box-shadow-card-hover);
        transform: translateY(-2px);
    }
}

.section-header {
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--border-light);
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);

    h2 {
        font-size: var(--font-size-xl);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0 0 var(--spacing-small) 0;
        display: flex;
        align-items: center;
        gap: var(--spacing-small);

        &::before {
            content: '';
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
            border-radius: var(--border-radius-mini);
        }
    }

    p {
        color: var(--text-secondary);
        margin: 0 0 var(--spacing-base) 0;
        font-size: var(--font-size-small);
        line-height: var(--line-height-loose);
    }
}

.stats {
    display: flex;
    gap: var(--spacing-base);
    flex-wrap: wrap;
    margin-top: var(--spacing-base);
}

.stat-item {
    padding: var(--spacing-small) var(--spacing-base);
    background: var(--bg-primary);
    border-radius: var(--border-radius-base);
    font-size: var(--font-size-mini);
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
    border: 1px solid var(--border-light);
    box-shadow: var(--box-shadow-small);
    transition: all var(--transition-base);

    &:hover {
        transform: translateY(-1px);
        box-shadow: var(--box-shadow-base);
    }

    &.stat-enabled {
        @include status-variant('success');
    }

    &.stat-disabled {
        @include status-variant('warning');
    }
}

.empty-state {
    padding: var(--spacing-3xl);
    text-align: center;
    color: var(--text-secondary);

    p {
        margin-bottom: var(--spacing-xl);
        font-size: var(--font-size-base);
        line-height: var(--line-height-loose);
    }
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--spacing-3xl);

    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--border-light);
        border-top: 3px solid var(--primary-color);
        border-radius: var(--border-radius-full);
        animation: spin 1s linear infinite;
        margin-bottom: var(--spacing-xl);
    }

    p {
        color: var(--text-secondary);
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-medium);
    }
}

// 站点网格布局
.site-grid-container {
    padding: var(--spacing-xl);
}

.site-grid {
    display: grid;
    gap: var(--spacing-large);
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));

    @include respond-to(lg) {
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: var(--spacing-base);
    }

    @include respond-to(md) {
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: var(--spacing-base);
    }

    @include respond-to(sm) {
        grid-template-columns: 1fr;
        gap: var(--spacing-base);
    }
}

// 站点卡片样式
.site-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-base);

    .site-name {
        font-size: var(--font-size-large);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0;
        flex: 1;
        @include text-ellipsis(1);
    }
}

.site-card-body {
    .site-details {
        margin-bottom: var(--spacing-base);
    }

    .site-detail-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);
        margin-bottom: var(--spacing-small);

        &:last-child {
            margin-bottom: 0;
        }
    }

    .site-detail-label {
        font-size: var(--font-size-mini);
        color: var(--text-secondary);
        font-weight: var(--font-weight-medium);
        min-width: 60px;
        flex-shrink: 0;
    }

    .site-id {
        @include info-box;
        color: var(--text-tertiary);
    }

    .site-url {
        @include info-box;
        color: var(--text-tertiary);
        word-break: break-all;
        flex: 1;
        @include text-ellipsis(1);
    }
}

.site-status {
    font-size: var(--font-size-mini);
    padding: var(--spacing-mini) var(--spacing-small);
    border-radius: var(--border-radius-base);
    font-weight: var(--font-weight-medium);
    border: 1px solid;
    white-space: nowrap;

    &.status-enabled {
        @include status-variant('success');
    }

    &.status-disabled {
        @include status-variant('warning');
    }
}

.test-result {
    margin-top: var(--spacing-base);
    padding-top: var(--spacing-base);
    border-top: 1px solid var(--border-light);
}

.test-text {
    font-size: var(--font-size-mini);
    padding: var(--spacing-small) var(--spacing-base);
    border-radius: var(--border-radius-base);
    display: inline-block;
    font-weight: var(--font-weight-medium);
    border: 1px solid;
    width: 100%;
    text-align: center;

    &.test-success {
        @include status-variant('success');
    }

    &.test-error {
        @include status-variant('danger');
    }
}

.site-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-base);

    .action-group {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);

        .action-label {
            font-size: var(--font-size-mini);
            color: var(--text-secondary);
            font-weight: var(--font-weight-medium);
            white-space: nowrap;
        }
    }
}






// 响应式设计优化
@include respond-to(md) {
    .settings-page {
        padding: var(--spacing-xl) var(--spacing-small);
    }

    .page-header {
        flex-direction: column;
        gap: var(--spacing-large);
        align-items: stretch;
        text-align: center;
        padding: var(--spacing-large);

        h1 {
            font-size: var(--font-size-2xl);
        }

        .actions {
            justify-content: center;
        }
    }

    .site-grid-container {
        padding: var(--spacing-base);
    }

    .site-actions {
        flex-direction: column;
        align-items: stretch;
        gap: var(--spacing-base);

        .action-group {
            justify-content: space-between;
            width: 100%;
        }

        .test-btn {
            width: 100%;
        }
    }

    .stats {
        justify-content: center;
    }
}

@include respond-to(sm) {
    .settings-page {
        padding: var(--spacing-large) var(--spacing-mini);
    }

    .page-header {
        padding: var(--spacing-base);
        margin-bottom: var(--spacing-xl);

        h1 {
            font-size: var(--font-size-xl);
        }
    }

    .section-header {
        padding: var(--spacing-base);

        h2 {
            font-size: var(--font-size-large);
        }
    }

    .site-card-body {
        .site-detail-item {
            margin-bottom: var(--spacing-mini);
        }

        .site-detail-label {
            min-width: 50px;
            font-size: 11px;
        }

        .site-id,
        .site-url {
            font-size: 11px;
            padding: 1px var(--spacing-mini);
        }
    }

    .site-actions {
        .action-label {
            font-size: 11px;
        }
    }

    .stats {
        gap: var(--spacing-small);
    }

    .stat-item {
        padding: var(--spacing-mini) var(--spacing-small);
        font-size: 11px;
    }
}
</style>