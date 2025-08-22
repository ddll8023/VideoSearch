<script setup>
import { ref } from 'vue'
import AdminSidebar from './AdminSidebar.vue'
import AdminHeader from './AdminHeader.vue'

// 侧边栏收起状态
const isSidebarCollapsed = ref(false)

// 切换侧边栏收起状态
const toggleSidebar = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<template>
    <div class="admin-layout">
        <!-- 侧边栏 -->
        <AdminSidebar :collapsed="isSidebarCollapsed" @toggle="toggleSidebar" class="admin-layout__sidebar" />

        <!-- 主内容区域 -->
        <main :class="['admin-layout__main', { 'admin-layout__main--collapsed': isSidebarCollapsed }]">
            <!-- 顶部工具栏 -->
            <AdminHeader :collapsed="isSidebarCollapsed" @toggle="toggleSidebar" />

            <!-- 页面内容 -->
            <div class="admin-layout__content">
                <router-view />
            </div>
        </main>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.admin-layout {
    display: flex;
    min-height: 100vh;
    background: var(--bg-secondary);

    &__sidebar {
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        z-index: var(--z-index-fixed);
        transition: width var(--transition-base);
    }

    &__main {
        flex: 1;
        transition: margin-left var(--transition-base);
        min-height: 100vh;
        display: flex;
        flex-direction: column;


    }



    &__content {
        flex: 1;
        padding: var(--spacing-2xl);
        overflow-y: auto;
    }

    // 响应式适配
    @include respond-to(md) {
        &__main {
            margin-left: 0;

            &--collapsed {
                margin-left: 0;
            }
        }



        &__content {
            padding: var(--spacing-base);
        }
    }
}
</style>