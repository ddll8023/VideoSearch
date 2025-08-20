<script setup>
import { defineProps, defineEmits, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'

// 定义props
const props = defineProps({
    tabs: {
        type: Array,
        required: true,
        default: () => []
    },
    activeTab: {
        type: String,
        required: true,
        default: ''
    }
})

// 定义事件
const emit = defineEmits(['tab-change'])

// 处理tab切换
const handleTabClick = (tabId) => {
    emit('tab-change', tabId)
}

// tabs与指示器引用
const tabsRef = ref(null)
const indicatorRef = ref(null)

const getActiveButton = () => {
    const el = tabsRef.value?.querySelector(`[data-id="${props.activeTab}"]`)
    return el || null
}

const updateIndicator = () => {
    const indEl = indicatorRef.value
    const tabsEl = tabsRef.value
    const btn = getActiveButton()
    if (!indEl || !btn || !tabsEl) return
    const offsetLeft = btn.offsetLeft
    const offsetWidth = btn.offsetWidth
    const scrollLeft = tabsEl.scrollLeft || 0
    indEl.style.width = `${offsetWidth}px`
    indEl.style.transform = `translateX(${offsetLeft - scrollLeft}px)`
}

const scrollActiveIntoView = () => {
    const btn = getActiveButton()
    if (!btn) return
    if (btn.scrollIntoView) {
        btn.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    }
}

onMounted(async () => {
    await nextTick()
    updateIndicator()
    scrollActiveIntoView()
    window.addEventListener('resize', updateIndicator)
    tabsRef.value?.addEventListener('scroll', updateIndicator)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', updateIndicator)
    tabsRef.value?.removeEventListener('scroll', updateIndicator)
})

watch(() => props.activeTab, async () => {
    await nextTick()
    updateIndicator()
    scrollActiveIntoView()
})

watch(() => props.tabs, async () => {
    await nextTick()
    updateIndicator()
})

</script>

<template>
    <div class="tabs-container">
        <!-- Tab导航 -->
        <div class="tabs-wrapper">
            <div class="tabs" role="tablist" ref="tabsRef">
                <button v-for="tab in tabs" :key="tab.id" @click="handleTabClick(tab.id)" role="tab"
                    :aria-selected="activeTab === tab.id" :tabindex="activeTab === tab.id ? 0 : -1" :data-id="tab.id"
                    @keydown.enter.prevent="handleTabClick(tab.id)" @keydown.space.prevent="handleTabClick(tab.id)"
                    :class="[
                        'tab-item',
                        { 'tab-active': activeTab === tab.id }
                    ]">
                    <!-- 图标插槽 -->
                    <slot :name="`icon-${tab.id}`" :tab="tab" :isActive="activeTab === tab.id">
                        <i v-if="tab.icon" :class="tab.icon" class="tab-icon"></i>
                    </slot>
                    <!-- 标签名称 -->
                    <span class="tab-name">{{ tab.name }}</span>
                    <!-- 计数显示 -->
                    <span v-if="tab.count !== undefined" class="tab-count">({{ tab.count }})</span>
                </button>
                <div ref="indicatorRef" class="tab-indicator"></div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.tabs-container {
    margin-bottom: var(--spacing-xl);
}

.tabs-wrapper {
    position: relative;
}

.tabs {
    position: relative;
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
        display: none;
    }
}

.tab-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-small);
    padding: var(--spacing-base) var(--spacing-xl);
    position: relative;
    cursor: pointer;
    white-space: nowrap;
    color: var(--text-secondary);
    font-weight: var(--font-weight-normal);
    transition: color var(--transition-base), font-weight var(--transition-base), background-color var(--transition-base), border-radius var(--transition-base);
    border: none;
    background: transparent;
    border-radius: 0;

    // 添加右侧分隔线
    &::after {
        content: '';
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 1px;
        height: 60%;
        background-color: var(--border-light);
        opacity: 0.5;
    }

    // 最后一个标签不显示分隔线
    &:last-child::after {
        display: none;
    }

    // 悬浮效果（排除激活状态）
    &:not(.tab-active):hover {
        color: var(--primary-color);
        background-color: var(--bg-tertiary);
        border-radius: var(--border-radius-small);
    }

    // 激活状态
    &.tab-active {
        color: var(--primary-color);
        font-weight: var(--font-weight-medium);
        background-color: transparent;
        border-radius: 0;
    }

    .tab-icon {
        font-size: var(--font-size-base);
        opacity: 0.8;
    }

    .tab-name {
        font-size: var(--font-size-base);
    }

    .tab-count {
        font-size: var(--font-size-mini);
        opacity: 0.7;
        color: inherit;
    }

    &.tab-active .tab-icon,
    &.tab-active .tab-count {
        opacity: 1;
    }
}

/* 指示器样式 */
.tab-indicator {
    position: absolute;
    left: 0;
    bottom: -1px;
    height: 3px;
    width: 0;
    border-radius: var(--border-radius-small);
    background: var(--primary-color);
    transform: translateX(0);
    transition: transform var(--transition-base), width var(--transition-base);
    pointer-events: none;
    z-index: 2;
}

/* 响应式设计 */
@include respond-above(sm) {
    .tabs {
        padding: 0 var(--spacing-base);
    }
}

@include respond-above(md) {
    .tabs {
        padding: 0;
    }
}

/* 无障碍和动画偏好 */
@media (prefers-reduced-motion: reduce) {
    .tab-item {
        transition: none;
    }

    .tab-indicator {
        transition: none;
    }
}

/* 焦点状态 */
.tab-item:focus-visible {
    outline: 2px solid var(--focus-ring-color);
    outline-offset: 2px;
    border-radius: var(--border-radius-small);
}
</style>
