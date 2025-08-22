<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Props
const props = defineProps({
    collapsed: {
        type: Boolean,
        default: false
    }
})

// Emits
const emit = defineEmits(['toggle'])

// 移动端菜单状态
const isMobileMenuOpen = ref(false)

// 菜单配置
const menuItems = ref([
    {
        id: 'dashboard',
        title: '控制台',
        icon: 'tachometer-alt',
        route: 'adminDashboard',
        active: true
    },
    {
        id: 'resource',
        title: '资源管理',
        icon: 'server',
        children: [
            {
                id: 'resource-sites',
                title: '站点配置',
                route: 'resourceSites'
            },
            {
                id: 'resource-monitor',
                title: '资源监控',
                route: 'resourceMonitor'
            }
        ]
    },
    {
        id: 'system',
        title: '系统管理',
        icon: 'cogs',
        children: [
            {
                id: 'system-monitor',
                title: '系统监控',
                route: 'systemMonitor'
            },
            {
                id: 'system-logs',
                title: '系统日志',
                route: 'systemLogs'
            }
        ]
    },
    {
        id: 'users',
        title: '用户管理',
        icon: 'users',
        route: 'userManagement',
        disabled: true
    },
    {
        id: 'statistics',
        title: '数据统计',
        icon: 'chart-bar',
        route: 'statistics',
        disabled: true
    }
])

// 展开的子菜单
const expandedMenus = ref(new Set(['resource', 'system']))

// 切换子菜单展开状态
const toggleSubmenu = (menuId) => {
    if (props.collapsed) return

    if (expandedMenus.value.has(menuId)) {
        expandedMenus.value.delete(menuId)
    } else {
        expandedMenus.value.add(menuId)
    }
}

// 导航到指定路由
const navigateTo = (routeName) => {
    if (!routeName) return

    router.push({ name: routeName })
    isMobileMenuOpen.value = false
}

// 检查菜单项是否激活
const isMenuActive = (item) => {
    if (item.route) {
        return route.name === item.route
    }
    if (item.children) {
        return item.children.some(child => route.name === child.route)
    }
    return false
}

// 切换移动端菜单
const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 计算侧边栏样式类
const sidebarClasses = computed(() => [
    'admin-sidebar',
    {
        'admin-sidebar--collapsed': props.collapsed,
        'admin-sidebar--mobile-open': isMobileMenuOpen.value
    }
])
</script>

<template>
    <!-- 移动端遮罩层 -->
    <div v-show="isMobileMenuOpen" class="admin-sidebar__mobile-backdrop" @click="toggleMobileMenu"></div>

    <!-- 侧边栏主体 -->
    <aside :class="sidebarClasses">
        <!-- 顶部Logo区域 -->
        <div class="admin-sidebar__header">
            <div class="admin-sidebar__logo">
                <div class="admin-sidebar__logo-icon">
                    <i class="fa fa-film"></i>
                </div>
                <transition name="fade">
                    <span v-show="!collapsed" class="admin-sidebar__logo-text">
                        VideoSearch
                    </span>
                </transition>
            </div>
        </div>

        <!-- 导航菜单 -->
        <nav class="admin-sidebar__nav">
            <ul class="admin-sidebar__menu">
                <li v-for="item in menuItems" :key="item.id" :class="[
                    'admin-sidebar__menu-item',
                    {
                        'admin-sidebar__menu-item--active': isMenuActive(item),
                        'admin-sidebar__menu-item--disabled': item.disabled,
                        'admin-sidebar__menu-item--has-children': item.children,
                        'admin-sidebar__menu-item--expanded': expandedMenus.has(item.id)
                    }
                ]">
                    <!-- 主菜单项 -->
                    <div class="admin-sidebar__menu-link"
                        @click="item.children ? toggleSubmenu(item.id) : navigateTo(item.route)"
                        :title="collapsed ? item.title : ''">
                        <i :class="['fa', `fa-${item.icon}`, 'admin-sidebar__menu-icon']"></i>
                        <transition name="fade">
                            <span v-show="!collapsed" class="admin-sidebar__menu-text">
                                {{ item.title }}
                            </span>
                        </transition>
                        <i v-if="item.children && !collapsed" :class="[
                            'fa',
                            'fa-chevron-down',
                            'admin-sidebar__menu-arrow',
                            { 'admin-sidebar__menu-arrow--expanded': expandedMenus.has(item.id) }
                        ]"></i>
                    </div>

                    <!-- 子菜单 -->
                    <transition name="slide-down">
                        <ul v-show="item.children && expandedMenus.has(item.id) && !collapsed"
                            class="admin-sidebar__submenu">
                            <li v-for="child in item.children" :key="child.id" :class="[
                                'admin-sidebar__submenu-item',
                                { 'admin-sidebar__submenu-item--active': route.name === child.route }
                            ]">
                                <div class="admin-sidebar__submenu-link" @click="navigateTo(child.route)">
                                    <span class="admin-sidebar__submenu-text">{{ child.title }}</span>
                                </div>
                            </li>
                        </ul>
                    </transition>
                </li>
            </ul>
        </nav>

        <!-- 底部操作区域 -->
        <div class="admin-sidebar__footer">
            <div class="admin-sidebar__collapse-btn" @click="$emit('toggle')" :title="collapsed ? '展开菜单' : '收起菜单'">
                <i :class="['fa', collapsed ? 'fa-angle-right' : 'fa-angle-left']"></i>
            </div>
        </div>
    </aside>

    <!-- 移动端菜单按钮 -->
    <button class="admin-sidebar__mobile-toggle" @click="toggleMobileMenu"
        :class="{ 'admin-sidebar__mobile-toggle--active': isMobileMenuOpen }">
        <i class="fa fa-bars"></i>
    </button>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.admin-sidebar {
    width: var(--sidebar-width);
    background: var(--bg-primary);
    border-right: 1px solid var(--border-light);
    box-shadow: var(--box-shadow-base);
    display: flex;
    flex-direction: column;
    transition: all var(--transition-base);
    z-index: var(--z-index-fixed);

    &--collapsed {
        width: var(--sidebar-collapsed-width);
    }

    // 移动端样式
    @include respond-to(md) {
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        transform: translateX(-100%);
        width: var(--sidebar-width);
        z-index: calc(var(--z-index-modal) + 10);

        &--mobile-open {
            transform: translateX(0);
        }
    }

    &__mobile-backdrop {
        display: none;

        @include respond-to(md) {
            display: block;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--bg-overlay);
            z-index: var(--z-index-modal);
        }
    }

    &__mobile-toggle {
        display: none;

        @include respond-to(md) {
            display: flex;
            position: fixed;
            top: var(--spacing-base);
            left: var(--spacing-base);
            width: 44px;
            height: 44px;
            background: var(--primary-color);
            color: var(--text-white);
            border: none;
            border-radius: var(--border-radius-base);
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: calc(var(--z-index-modal) + 20);
            box-shadow: var(--box-shadow-large);
            transition: all var(--transition-base);

            &:hover {
                transform: translateY(-2px);
                box-shadow: var(--box-shadow-xl);
            }

            &--active {
                background: var(--danger-color);
            }
        }
    }

    &__header {
        padding: var(--spacing-xl) var(--spacing-base);
        border-bottom: 1px solid var(--border-light);
        flex-shrink: 0;
    }

    &__logo {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);
    }

    &__logo-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        border-radius: var(--border-radius-base);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-white);
        font-size: var(--font-size-large);
        flex-shrink: 0;
    }

    &__logo-text {
        font-size: var(--font-size-large);
        font-weight: var(--font-weight-bold);
        color: var(--text-primary);
        white-space: nowrap;
    }

    &__nav {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: var(--spacing-base) 0;
    }

    &__menu {
        list-style: none;
        margin: 0;
        padding: 0;
    }

    &__menu-item {
        margin: var(--spacing-mini) var(--spacing-small);

        &--disabled {
            opacity: 0.5;
            pointer-events: none;
        }
    }

    &__menu-link {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);
        padding: var(--spacing-small) var(--spacing-base);
        border-radius: var(--border-radius-base);
        color: var(--text-secondary);
        cursor: pointer;
        transition: all var(--transition-base);
        text-decoration: none;
        position: relative;
        min-height: 44px;

        &:hover {
            background: var(--bg-tertiary);
            color: var(--primary-color);
        }

        .admin-sidebar__menu-item--active & {
            background: var(--primary-color);
            color: var(--text-white);
            box-shadow: var(--box-shadow-small);

            &:hover {
                background: var(--primary-dark);
                color: var(--text-white);
            }
        }
    }

    &__menu-icon {
        width: 18px;
        text-align: center;
        flex-shrink: 0;
        font-size: var(--font-size-base);
    }

    &__menu-text {
        flex: 1;
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
        white-space: nowrap;
    }

    &__menu-arrow {
        font-size: var(--font-size-mini);
        transition: transform var(--transition-base);
        flex-shrink: 0;

        &--expanded {
            transform: rotate(180deg);
        }
    }

    &__submenu {
        list-style: none;
        margin: var(--spacing-mini) 0 0 0;
        padding: 0;

        border-radius: var(--border-radius-base);
        overflow: hidden;
    }

    &__submenu-item {
        &--active {
            .admin-sidebar__submenu-link {
                background: var(--primary-color);
                color: var(--text-white);

                &:hover {
                    background: var(--primary-dark);
                    color: var(--text-white);
                }
            }
        }
    }

    &__submenu-link {
        display: flex;
        align-items: center;
        padding: var(--spacing-small) var(--spacing-xl);
        color: var(var(--text-secondary));
        cursor: pointer;
        transition: all var(--transition-base);
        min-height: 36px;

        &:hover {
            background: var(--bg-tertiary);
            color: var(--primary-color);
        }
    }

    &__submenu-text {
        font-size: var(--font-size-mini);
        font-weight: var(--font-weight-normal);
    }

    &__footer {
        padding: var(--spacing-base);
        border-top: 1px solid var(--border-light);
        flex-shrink: 0;
    }

    &__collapse-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 36px;
        background: var(--bg-tertiary);
        border: none;
        border-radius: var(--border-radius-base);
        color: var(--text-secondary);
        cursor: pointer;
        transition: all var(--transition-base);
        font-size: var(--font-size-small);

        &:hover {
            background: var(--primary-color);
            color: var(--text-white);
        }

        @include respond-to(md) {
            display: none;
        }
    }
}

// 动画
.fade-enter-active,
.fade-leave-active {
    transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
    transition: all var(--transition-base);
    overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
    max-height: 0;
    opacity: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
    max-height: 300px;
    opacity: 1;
}
</style>