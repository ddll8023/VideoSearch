<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import CommonButton from '@/components/common/CommonButton.vue'

const router = useRouter()
const route = useRoute()
const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)

// 导航配置数据
const navigationConfig = {
    // 主导航项（显示在桌面端中间和移动端菜单）
    mainItems: [
        {
            name: 'home',
            label: '主页',
            icon: 'home',
            showInMobile: true
        },
        {
            name: 'history',
            label: '历史记录',
            icon: 'history',
            showInMobile: true
        }
    ],
    // 操作按钮（显示在右侧）
    actionItems: [
        {
            name: 'settings',
            label: '设置',
            icon: 'cog',
            showInMobile: false,
            isIconOnly: true
        }
    ]
}

// 统一的导航处理函数
const handleNavigation = (routeName) => {
    if (route.name === routeName) return // 避免重复导航

    router.push({ name: routeName })
    isMobileMenuOpen.value = false
}

// 移动端菜单控制
const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 滚动监听
const handleScroll = () => {
    isScrolled.value = window.scrollY > 10
}

onMounted(() => {
    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
    <!-- 顶部导航栏 -->
    <header :class="['app-header', { 'app-header--scrolled': isScrolled }]">
        <nav class="app-header__nav">
            <div class="app-header__container">
                <div class="app-header__content">
                    <!-- 左侧：标题和图标 -->
                    <div class="app-header__brand">
                        <div class="app-header__logo">
                            <i class="fa fa-film"></i>
                        </div>
                        <h1 class="app-header__title">VideoSearch</h1>
                    </div>

                    <!-- 中间：导航链接 - 桌面端 -->
                    <div class="app-header__nav-desktop">
                        <CommonButton v-for="item in navigationConfig.mainItems" :key="item.name"
                            @click="handleNavigation(item.name)"
                            :type="route.name === item.name ? 'primary' : 'default'" size="small" plain
                            class="app-header__nav-item">
                            {{ item.label }}
                        </CommonButton>
                    </div>

                    <!-- 右侧：设置和菜单按钮 -->
                    <div class="app-header__actions">
                        <!-- 操作按钮 -->
                        <CommonButton v-for="item in navigationConfig.actionItems" :key="item.name"
                            @click="handleNavigation(item.name)"
                            :type="route.name === item.name ? 'primary' : 'default'" size="small" :icon="item.icon"
                            circle plain :title="item.label" class="app-header__action-item">
                        </CommonButton>

                        <!-- 移动端菜单按钮 -->
                        <CommonButton @click="toggleMobileMenu" type="default" size="small" icon="bars" circle plain
                            title="菜单" class="app-header__mobile-toggle">
                        </CommonButton>
                    </div>
                </div>

                <!-- 移动端导航菜单 -->
                <div :class="['app-header__mobile-menu', { 'app-header__mobile-menu--open': isMobileMenuOpen }]">
                    <div class="app-header__mobile-menu-content">
                        <CommonButton v-for="item in navigationConfig.mainItems.filter(item => item.showInMobile)"
                            :key="`mobile-${item.name}`" @click="handleNavigation(item.name)"
                            :type="route.name === item.name ? 'primary' : 'default'" size="small" block plain
                            class="app-header__mobile-nav-item">
                            <i v-if="item.icon" :class="`fa fa-${item.icon}`" class="app-header__mobile-nav-icon"></i>
                            {{ item.label }}
                        </CommonButton>
                    </div>
                </div>
            </div>
        </nav>
    </header>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: var(--z-index-fixed);
    background: var(--bg-header);
    backdrop-filter: blur(var(--glass-blur-base)) saturate(var(--glass-saturation)) brightness(var(--glass-brightness));
    border-bottom: 1px solid var(--border-header);
    transition: all var(--transition-base);
    display: flex;
    align-items: center;
    min-height: var(--header-height);

    &--scrolled {
        background: var(--bg-header-scrolled);
        backdrop-filter: blur(var(--glass-blur-scrolled)) saturate(var(--glass-saturation)) brightness(var(--glass-brightness));
        box-shadow: 0 4px 20px var(--shadow-header);
        border-bottom-color: var(--border-header-scrolled);
    }

    &__nav {
        width: 100%;
        height: var(--header-height);
        display: flex;
        align-items: center;
    }

    &__container {
        width: 100%;
        max-width: none;
        margin: 0;
        padding-left: var(--spacing-small);
        padding-right: var(--spacing-base);
        height: 100%;

        @include respond-to(lg) {
            padding-left: var(--spacing-small);
            padding-right: var(--spacing-large);
        }

        @include respond-to(md) {
            padding-left: var(--spacing-small);
            padding-right: var(--spacing-base);
        }

        @include respond-to(sm) {
            padding-left: var(--spacing-small);
            padding-right: var(--spacing-small);
        }
    }

    &__content {
        width: 100%;
        height: var(--header-height);
        min-height: var(--header-height);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    &__brand {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);
        flex: 0 0 auto;
    }

    &__logo {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: var(--border-radius-base);
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        color: white;
        font-size: var(--font-size-large);
        box-shadow: var(--shadow-card);
    }

    &__title {
        font-size: var(--font-size-xl);
        font-weight: var(--font-weight-bold);
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        white-space: nowrap;

        @include respond-to(md) {
            font-size: var(--font-size-large);
        }

        @include respond-to(sm) {
            font-size: var(--font-size-base);
        }
    }

    &__nav-desktop {
        gap: var(--spacing-xl);
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;

        @include respond-to(md) {
            display: none;
        }
    }

    &__nav-item {
        transition: all var(--transition-base);

        &:hover {
            transform: translateY(-1px);
        }
    }

    &__actions {
        gap: var(--spacing-base);
        flex: 0 0 auto;
        display: flex;
        align-items: center;
    }

    &__action-item {
        transition: all var(--transition-base);

        &:hover {
            transform: translateY(-1px);
        }
    }

    &__mobile-toggle {
        display: none;

        @include respond-to(md) {
            display: flex;
        }
    }

    &__mobile-menu {
        display: none;
        overflow: hidden;
        transition: all var(--transition-base);
        max-height: 0;

        @include respond-to(md) {
            display: block;
        }

        &--open {
            max-height: 200px;
        }
    }

    &__mobile-menu-content {
        padding: var(--spacing-base) 0;
        border-top: 1px solid var(--border-header);
        background: var(--bg-header);
        backdrop-filter: blur(var(--glass-blur-base)) saturate(var(--glass-saturation)) brightness(var(--glass-brightness));
    }

    &__mobile-nav-item {
        margin: var(--spacing-mini) 0;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        text-align: left;
    }

    &__mobile-nav-icon {
        margin-right: var(--spacing-small);
        width: 16px;
        text-align: center;
    }
}
</style>