<script setup>
import { ref } from 'vue'

const currentTime = ref(new Date().toLocaleString())
</script>

<template>
    <div class="admin-dashboard">
        <!-- 页面标题 -->
        <div class="page-header">
            <h1>管理控制台</h1>
            <p class="page-subtitle">VideoSearch 管理端 - 当前时间：{{ currentTime }}</p>
        </div>

        <!-- 欢迎卡片 -->
        <div class="welcome-card">
            <div class="welcome-icon">
                <i class="fa fa-cogs"></i>
            </div>
            <h2>欢迎使用管理控制台</h2>
            <p>系统运行正常，所有服务已就绪</p>
            <div class="status-badge">
                <span class="status-text">开发中</span>
            </div>
        </div>

        <!-- 功能模块卡片 -->
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fa fa-server"></i>
                </div>
                <h3>资源管理</h3>
                <p>管理视频资源站点配置</p>
                <div class="feature-status">
                    <span class="status-dot status-ready"></span>
                    <span>已就绪</span>
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fa fa-chart-line"></i>
                </div>
                <h3>系统监控</h3>
                <p>监控系统运行状态</p>
                <div class="feature-status">
                    <span class="status-dot status-developing"></span>
                    <span>开发中</span>
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fa fa-users"></i>
                </div>
                <h3>用户管理</h3>
                <p>管理系统用户和权限</p>
                <div class="feature-status">
                    <span class="status-dot status-planned"></span>
                    <span>计划中</span>
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fa fa-database"></i>
                </div>
                <h3>数据统计</h3>
                <p>查看使用数据统计</p>
                <div class="feature-status">
                    <span class="status-dot status-planned"></span>
                    <span>计划中</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.admin-dashboard {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-3xl);
}

.page-header {
    margin-bottom: var(--spacing-xl);

    h1 {
        font-size: var(--font-size-3xl);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0 0 var(--spacing-small) 0;
    }

    .page-subtitle {
        font-size: var(--font-size-base);
        color: var(--text-secondary);
        margin: 0;
    }
}

.welcome-card {
    background: var(--bg-primary);
    border-radius: var(--border-radius-xl);
    padding: var(--spacing-3xl);
    text-align: center;
    box-shadow: var(--box-shadow-card);
    border: 1px solid var(--border-light);

    .welcome-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto var(--spacing-2xl);
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        border-radius: var(--border-radius-full);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-white);
        font-size: 32px;
    }

    h2 {
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0 0 var(--spacing-base) 0;
    }

    p {
        font-size: var(--font-size-base);
        color: var(--text-secondary);
        margin: 0 0 var(--spacing-2xl) 0;
    }

    .status-badge {
        display: inline-block;
        background: var(--warning-color);
        color: var(--text-white);
        padding: var(--spacing-small) var(--spacing-large);
        border-radius: var(--border-radius-base);
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
    }
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-2xl);
}

.feature-card {
    background: var(--bg-primary);
    border-radius: var(--border-radius-xl);
    padding: var(--spacing-2xl);
    box-shadow: var(--box-shadow-card);
    border: 1px solid var(--border-light);
    transition: all var(--transition-base);

    &:hover {
        transform: translateY(-2px);
        box-shadow: var(--box-shadow-card-hover);
    }

    .feature-icon {
        width: 60px;
        height: 60px;
        background: var(--bg-tertiary);
        border-radius: var(--border-radius-large);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-color);
        font-size: 24px;
        margin-bottom: var(--spacing-large);
    }

    h3 {
        font-size: var(--font-size-xl);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0 0 var(--spacing-small) 0;
    }

    p {
        font-size: var(--font-size-base);
        color: var(--text-secondary);
        margin: 0 0 var(--spacing-large) 0;
        line-height: var(--line-height-base);
    }

    .feature-status {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);
        font-size: var(--font-size-small);
        color: var(--text-tertiary);

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: var(--border-radius-full);

            &.status-ready {
                background: var(--success-color);
            }

            &.status-developing {
                background: var(--warning-color);
            }

            &.status-planned {
                background: var(--info-color);
            }
        }
    }
}

@media (max-width: 768px) {
    .page-header h1 {
        font-size: var(--font-size-2xl);
    }

    .welcome-card {
        padding: var(--spacing-2xl);
    }

    .feature-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-large);
    }
}
</style>