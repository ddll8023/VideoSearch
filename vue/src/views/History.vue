<script setup>
// 未开发页面，无需导入任何功能模块
</script>

<template>
    <div class="history-page">
        <!-- 未开发状态 -->
        <div class="under-development">
            <div class="development-icon">🚧</div>
            <h1>历史记录</h1>
            <h2>功能开发中</h2>
            <p>此功能正在开发中，敬请期待</p>
            <button @click="$router.push({ name: 'home' })" class="back-home-btn">
                返回主页
            </button>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.history-page {
    min-height: calc(100vh - var(--header-height));
    background-color: var(--bg-tertiary);
    padding: var(--spacing-xl) 0;
}

.under-development {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-3xl);
    text-align: center;
    background: var(--bg-primary);
    border-radius: var(--border-radius-large);
    box-shadow: var(--box-shadow-card);

    .development-icon {
        font-size: 4rem;
        margin-bottom: var(--spacing-large);
    }

    h1 {
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        margin: 0 0 var(--spacing-base) 0;
    }

    h2 {
        font-size: var(--font-size-xl);
        color: var(--text-primary);
        margin: 0 0 var(--spacing-base) 0;
    }

    p {
        color: var(--text-secondary);
        margin-bottom: var(--spacing-xl);
        font-size: var(--font-size-base);
    }
}

.back-home-btn {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: var(--spacing-base) var(--spacing-xl);
    border-radius: var(--border-radius-base);
    cursor: pointer;
    font-size: var(--font-size-base);
    transition: background-color var(--transition-base);

    &:hover {
        background: var(--primary-dark);
    }
}

// 响应式设计
@include respond-to(sm) {
    .under-development {
        padding: var(--spacing-xl);

        .development-icon {
            font-size: 3rem;
        }

        h1 {
            font-size: var(--font-size-xl);
        }

        h2 {
            font-size: var(--font-size-large);
        }
    }
}
</style>