<script setup>
import { ref, computed, nextTick, watch } from 'vue'

// Props 定义
const props = defineProps({
    // 搜索关键词 (v-model)
    modelValue: {
        type: String,
        default: ''
    },
    // 占位符文本
    placeholder: {
        type: String,
        default: '请输入要搜索的内容...'
    },
    // 禁用状态
    disabled: {
        type: Boolean,
        default: false
    },
    // 加载状态
    loading: {
        type: Boolean,
        default: false
    },
    // 样式变体：hero(大尺寸居中) | compact(紧凑型)
    variant: {
        type: String,
        default: 'hero',
        validator: (value) => ['hero', 'compact'].includes(value)
    },
    // 尺寸规格
    size: {
        type: String,
        default: 'base',
        validator: (value) => ['mini', 'small', 'base', 'large'].includes(value)
    },
    // 是否显示搜索按钮
    showSearchButton: {
        type: Boolean,
        default: true
    },
    // 是否自动聚焦
    autofocus: {
        type: Boolean,
        default: false
    },
    // 搜索按钮文本
    searchButtonText: {
        type: String,
        default: '搜索'
    },
    // 搜索按钮加载文本
    searchButtonLoadingText: {
        type: String,
        default: '搜索中...'
    }
})

// 事件定义
const emit = defineEmits([
    'update:modelValue',
    'search',
    'clear',
    'input',
    'focus',
    'blur',
    'keydown'
])

// 响应式数据
const searchInputRef = ref(null)
const localValue = ref(props.modelValue || '')

// 监听 props.modelValue 的变化
watch(() => props.modelValue, (newValue) => {
    localValue.value = newValue || ''
}, { immediate: true })

// 监听本地值的变化，同步到父组件
watch(localValue, (newValue) => {
    emit('update:modelValue', newValue)
})

// 计算样式类名
const searchBoxClasses = computed(() => {
    return [
        'common-search',
        `common-search--${props.variant}`,
        `common-search--${props.size}`,
        {
            'common-search--disabled': props.disabled,
            'common-search--loading': props.loading,
            'common-search--has-value': localValue.value.trim()
        }
    ]
})

// 计算可访问性属性
const accessibilityAttrs = computed(() => {
    return {
        'aria-label': props.placeholder,
        'aria-describedby': 'search-help',
        'aria-expanded': 'false',
        'aria-autocomplete': 'none',
        'role': 'searchbox'
    }
})

// 处理输入事件
const handleInput = (event) => {
    const value = event.target.value
    localValue.value = value
    emit('input', value)
}

// 处理搜索
const handleSearch = () => {
    const keyword = localValue.value.trim()
    if (!keyword || props.disabled || props.loading) return

    emit('search', keyword)
}

// 处理键盘事件
const handleKeydown = (event) => {
    emit('keydown', event)

    if (event.key === 'Enter') {
        event.preventDefault()
        handleSearch()
    } else if (event.key === 'Escape') {
        event.preventDefault()
        handleClear()
    }
}

// 处理清空
const handleClear = () => {
    localValue.value = ''
    emit('clear')

    // 聚焦搜索框
    nextTick(() => {
        focus()
    })
}

// 聚焦方法
const focus = () => {
    searchInputRef.value?.focus()
}

// 失焦方法
const blur = () => {
    searchInputRef.value?.blur()
}

// 暴露方法给父组件
defineExpose({
    focus,
    blur
})

// 自动聚焦
if (props.autofocus) {
    nextTick(() => {
        focus()
    })
}
</script>

<template>
    <div :class="searchBoxClasses" role="search" :aria-label="'搜索区域'">
        <!-- 搜索图标 -->
        <div class="common-search__icon" aria-hidden="true">
            <svg class="common-search__icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
        </div>

        <!-- 输入框容器 -->
        <div class="common-search__input-wrapper">
            <input ref="searchInputRef" :value="localValue" @input="handleInput" @keydown="handleKeydown"
                @focus="$emit('focus', $event)" @blur="$emit('blur', $event)" type="text" :placeholder="placeholder"
                class="common-search__input" :disabled="disabled || loading" v-bind="accessibilityAttrs" />

            <!-- 内置清空按钮 -->
            <button v-if="localValue.trim()" @click="handleClear" class="common-search__clear-btn" type="button"
                :title="'清空搜索内容'" :disabled="disabled || loading" :aria-label="'清空搜索内容'">
                <svg class="common-search__clear-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12">
                    </path>
                </svg>
            </button>
        </div>

        <!-- 搜索按钮 -->
        <button v-if="showSearchButton" @click="handleSearch" :disabled="!localValue.trim() || disabled || loading"
            class="common-search__search-btn" type="submit"
            :aria-label="loading ? searchButtonLoadingText : `${searchButtonText}：${localValue.trim() || '请输入搜索内容'}`">
            <!-- 按钮内容 -->
            <span class="common-search__search-btn-content">
                <span v-if="loading" class="common-search__search-btn-text">{{ searchButtonLoadingText }}</span>
                <span v-else class="common-search__search-btn-text">{{ searchButtonText }}</span>

                <!-- 加载指示器 -->
                <div v-if="loading" class="common-search__loading-spinner" aria-hidden="true"></div>
            </span>

            <!-- 按钮光效背景 -->
            <div class="common-search__search-btn-shine" aria-hidden="true"></div>
        </button>

        <!-- 隐藏的帮助文本 -->
        <div id="search-help" class="sr-only">
            按回车键搜索，按ESC键清空，使用Tab键导航
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.common-search {
    position: relative;
    display: flex;
    align-items: center;
    background-color: var(--bg-primary);
    border: 1px solid var(--border-light);
    border-radius: var(--border-radius-xl);
    box-shadow: var(--shadow-card);
    transition: box-shadow var(--transition-base), transform var(--transition-base), border-color var(--transition-base);

    &:hover {
        box-shadow: var(--shadow-card-hover);
        transform: translateY(-1px);
    }

    &:focus-within {
        box-shadow: var(--shadow-card-hover), 0 0 0 3px rgba(22, 93, 255, 0.1);
        transform: translateY(-1px);
        border-color: var(--primary-color);
    }

    // Hero变体 - 大尺寸居中样式
    &--hero {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;

        .common-search__icon {
            padding: 0 var(--spacing-large);
        }

        .common-search__input {
            padding: var(--spacing-large) 0;
            font-size: var(--font-size-large);
        }

        .common-search__search-btn {
            padding: var(--spacing-large) var(--spacing-xl);
            font-size: var(--font-size-large);
            font-weight: var(--font-weight-medium);
        }

        .common-search__clear-btn {
            right: var(--spacing-base);
            width: 32px;
            height: 32px;
        }

        @include respond-to(md) {
            max-width: 500px;

            .common-search__icon {
                padding: 0 var(--spacing-base);
            }

            .common-search__input {
                padding: var(--spacing-base) 0;
                font-size: var(--font-size-base);
            }

            .common-search__search-btn {
                padding: var(--spacing-base) var(--spacing-large);
                font-size: var(--font-size-base);
            }
        }

        @include respond-to(sm) {
            max-width: 100%;

            .common-search__search-btn {
                padding: var(--spacing-base);
                font-size: var(--font-size-small);
            }
        }
    }

    // Compact变体 - 紧凑型样式
    &--compact {
        width: 100%;
        max-width: 600px;

        .common-search__icon {
            padding: 0 var(--spacing-base);
        }

        .common-search__input {
            padding: var(--spacing-base) 0;
            font-size: var(--font-size-base);
        }

        .common-search__search-btn {
            padding: var(--spacing-base) var(--spacing-large);
            font-size: var(--font-size-base);
        }

        .common-search__clear-btn {
            right: var(--spacing-small);
            width: 24px;
            height: 24px;
        }

        @include respond-to(md) {
            max-width: 500px;
        }

        @include respond-to(sm) {
            max-width: 100%;

            .common-search__icon {
                padding: 0 var(--spacing-small);
            }

            .common-search__search-btn {
                padding: var(--spacing-small) var(--spacing-base);
                font-size: var(--font-size-small);
            }
        }
    }

    // 尺寸变体
    &--mini {
        .common-search__icon {
            padding: 0 var(--spacing-small);
        }

        .common-search__input {
            padding: var(--spacing-mini) 0;
            font-size: var(--font-size-mini);
        }

        .common-search__search-btn {
            padding: var(--spacing-mini) var(--spacing-base);
            font-size: var(--font-size-mini);
        }

        .common-search__clear-btn {
            width: 20px;
            height: 20px;
        }
    }

    &--small {
        .common-search__icon {
            padding: 0 var(--spacing-small);
        }

        .common-search__input {
            padding: var(--spacing-small) 0;
            font-size: var(--font-size-small);
        }

        .common-search__search-btn {
            padding: var(--spacing-small) var(--spacing-base);
            font-size: var(--font-size-small);
        }

        .common-search__clear-btn {
            width: 22px;
            height: 22px;
        }
    }

    &--large {
        .common-search__icon {
            padding: 0 var(--spacing-large);
        }

        .common-search__input {
            padding: var(--spacing-large) 0;
            font-size: var(--font-size-large);
        }

        .common-search__search-btn {
            padding: var(--spacing-large) var(--spacing-xl);
            font-size: var(--font-size-large);
        }

        .common-search__clear-btn {
            width: 36px;
            height: 36px;
        }
    }

    // 禁用状态
    &--disabled {
        opacity: 0.5;
        cursor: not-allowed;

        &:hover {
            transform: none !important;
            box-shadow: var(--shadow-card) !important;
        }

        .common-search__input,
        .common-search__search-btn,
        .common-search__clear-btn {
            cursor: not-allowed;
        }
    }

    // 加载状态
    &--loading {
        cursor: default;

        &:hover {
            transform: none !important;
        }
    }

    // 有值状态
    &--has-value {
        .common-search__input-wrapper {
            padding-right: 40px;
        }
    }
}

.common-search__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary);
    transition: color var(--transition-base);

    .common-search:focus-within & {
        color: var(--primary-color);
    }
}

.common-search__icon-svg {
    width: 20px;
    height: 20px;
    stroke-width: 2;
}

.common-search__input-wrapper {
    position: relative;
    flex: 1;
    display: flex;
    align-items: center;
}

.common-search__input {
    @include input-reset;

    width: 100%;
    color: var(--text-primary);
    background-color: transparent;
    transition: color var(--transition-base);

    &::placeholder {
        color: var(--text-tertiary);
        transition: color var(--transition-base);
    }

    &:focus::placeholder {
        color: var(--text-disabled);
    }

    &:disabled {
        color: var(--text-disabled);
        cursor: not-allowed;
    }
}

.common-search__clear-btn {
    @include button-reset;

    position: absolute;
    right: var(--spacing-small);
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    color: var(--text-tertiary);
    background-color: transparent;
    border-radius: var(--border-radius-full);
    transition: color var(--transition-base), background-color var(--transition-base), transform var(--transition-base);

    &:hover:not(:disabled) {
        color: var(--danger-color);
        background-color: var(--bg-secondary);
        transform: translateY(-50%) scale(1.1);
    }

    &:active:not(:disabled) {
        transform: translateY(-50%) scale(0.95);
    }

    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    svg {
        width: 16px;
        height: 16px;
        stroke-width: 2;
        transition: transform var(--transition-base);
    }

    &:hover:not(:disabled) svg {
        transform: rotate(90deg);
    }
}

.common-search__search-btn {
    @include button-reset;

    position: relative;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    border-radius: 0 var(--border-radius-xl) var(--border-radius-xl) 0;
    color: white;
    font-weight: var(--font-weight-medium);
    overflow: hidden;
    transition: background var(--transition-base), box-shadow var(--transition-base), transform var(--transition-base);

    &:hover:not(:disabled) {
        background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
        box-shadow: 0 4px 14px 0 rgba(22, 93, 255, 0.25);
    }

    &:active:not(:disabled) {
        transform: translateY(1px) scale(0.98);
    }

    &:disabled {
        background: var(--text-disabled);
        color: var(--bg-primary);
        cursor: not-allowed;
    }
}

.common-search__search-btn-content {
    position: relative;
    z-index: 10;
    display: flex;
    align-items: center;
    gap: var(--spacing-small);
}

.common-search__search-btn-text {
    display: inline-block;
}

.common-search__loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid white;
    border-top: 2px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.common-search__search-btn-shine {
    position: absolute;
    inset: 0;
    background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
    transform: translateX(-100%);
    transition: transform var(--transition-base);

    .common-search__search-btn:hover & {
        transform: translateX(100%);
        transition-duration: var(--transition-slow);
    }
}

// 可访问性工具类
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

// 减少动画模式
@media (prefers-reduced-motion: reduce) {
    * {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
    }
}

// 高对比度模式适配
@media (prefers-contrast: high) {
    .common-search {
        border-width: 2px;
    }

    .common-search__search-btn {
        border: 2px solid var(--primary-color);
    }
}
</style>