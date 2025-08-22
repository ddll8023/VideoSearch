<script setup>
// 接收父组件传递的侧边栏收起状态
const props = defineProps({
    collapsed: {
        type: Boolean,
        default: false
    }
})

// 定义事件，用于向父组件传递切换侧边栏的请求
const emit = defineEmits(['toggle'])

// 切换侧边栏
const handleToggleSidebar = () => {
    emit('toggle')
}
</script>

<template>
    <!-- 顶部工具栏 -->
    <header class="admin-header">
        <div class="admin-header__content">
            <div class="admin-header__left">
                <button @click="handleToggleSidebar" class="admin-header__sidebar-toggle"
                    :title="collapsed ? '展开侧边栏' : '收起侧边栏'">
                    <i :class="['fa', collapsed ? 'fa-indent' : 'fa-outdent']"></i>
                </button>
            </div>
        </div>
    </header>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.admin-header {
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-light);
    box-shadow: var(--box-shadow-small);
    position: sticky;
    top: 0;
    z-index: var(--z-index-sticky);

    &__content {
        height: var(--header-height);
        padding: 0 var(--spacing-2xl);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    &__left {
        display: flex;
        align-items: center;
        gap: var(--spacing-base);
    }

    &__sidebar-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border: none;
        background: var(--bg-tertiary);
        color: var(--text-secondary);
        border-radius: var(--border-radius-base);
        cursor: pointer;
        transition: all var(--transition-base);
        font-size: var(--font-size-base);

        &:hover {
            background: var(--primary-color);
            color: var(--text-white);
            transform: translateY(-1px);
        }

        &:active {
            transform: translateY(0);
        }
    }



    // 响应式适配
    @include respond-to(md) {
        &__content {
            padding: 0 var(--spacing-base);
        }
    }
}
</style>