<script setup>
import { computed } from 'vue'

// Props 定义
const props = defineProps({
    // 当前页码
    currentPage: {
        type: Number,
        default: 1,
        validator: (value) => value >= 1
    },
    // 总页数
    totalPages: {
        type: Number,
        default: 1,
        validator: (value) => value >= 1
    },
    // 是否显示页码输入框
    showInput: {
        type: Boolean,
        default: false
    },
    // 当前页前后显示的页码数
    visibleRange: {
        type: Number,
        default: 2,
        validator: (value) => value >= 1
    },
    // 组件尺寸
    size: {
        type: String,
        default: 'base',
        validator: (value) => ['mini', 'small', 'base', 'large'].includes(value)
    },
    // 是否启用精简模式（大量页码时使用省略号）
    compact: {
        type: Boolean,
        default: true
    },
    // 是否禁用整个分页组件
    disabled: {
        type: Boolean,
        default: false
    }
})

// 事件定义
const emit = defineEmits(['pagechange'])

// 计算样式类名
const paginationClasses = computed(() => {
    return [
        'common-pagination',
        `common-pagination--${props.size}`
    ]
})

// 生成需要显示的页码数组（包含可能的省略号）
const pageNumbers = computed(() => {
    const pages = []
    const totalPages = props.totalPages
    const currentPage = props.currentPage
    const visibleRange = props.visibleRange

    // 如果总页数较少或不启用精简模式，直接显示所有页码
    if (totalPages <= 2 * visibleRange + 3 || !props.compact) {
        for (let i = 1; i <= totalPages; i++) {
            pages.push(i)
        }
        return pages
    }

    // 精简模式，使用省略号
    pages.push(1)

    // 计算显示范围
    const startRange = Math.max(2, currentPage - visibleRange)
    const endRange = Math.min(totalPages - 1, currentPage + visibleRange)

    // 添加前面的省略号
    if (startRange > 2) {
        pages.push('...')
    }

    // 添加范围内的页码
    for (let i = startRange; i <= endRange; i++) {
        pages.push(i)
    }

    // 添加后面的省略号
    if (endRange < totalPages - 1) {
        pages.push('...')
    }

    pages.push(totalPages)

    return pages
})

// 通用页面跳转处理函数
const handlePageJump = (targetPage) => {
    if (!props.disabled && targetPage !== props.currentPage && targetPage >= 1 && targetPage <= props.totalPages) {
        emit('pagechange', {
            currentPage: targetPage,
            totalPages: props.totalPages
        })
    }
}

// 事件处理：页码点击
const handlePageClick = (page) => {
    if (!props.disabled && page && page !== '...') {
        handlePageJump(page)
    }
}





// 事件处理：页码输入
const handlePageInput = (event) => {
    if (props.disabled) return

    if (event.key === 'Enter' || event.type === 'blur') {
        let page = parseInt(event.target.value)

        // 验证页码有效性
        if (isNaN(page) || page < 1) {
            page = 1
        } else if (page > props.totalPages) {
            page = props.totalPages
        }

        event.target.value = page

        if (page !== props.currentPage) {
            emit('pagechange', {
                currentPage: page,
                totalPages: props.totalPages
            })
        }
    }
}
</script>

<template>
    <div :class="paginationClasses">
        <!-- 前导航按钮（首页、上一页） -->
        <button class="common-pagination__btn common-pagination__btn--nav"
            :class="{ 'common-pagination__btn--disabled': props.disabled || props.currentPage <= 1 }"
            :disabled="props.disabled || props.currentPage <= 1" @click="() => handlePageJump(1)" title="首页">
            <i class="fa fa-angle-double-left"></i>
        </button>
        <button class="common-pagination__btn common-pagination__btn--nav"
            :class="{ 'common-pagination__btn--disabled': props.disabled || props.currentPage <= 1 }"
            :disabled="props.disabled || props.currentPage <= 1" @click="() => handlePageJump(props.currentPage - 1)"
            title="上一页">
            <i class="fa fa-angle-left"></i>
        </button>

        <!-- 页码按钮 -->
        <template v-for="page in pageNumbers" :key="page">
            <span v-if="page === '...'" class="common-pagination__ellipsis">...</span>
            <button v-else class="common-pagination__btn common-pagination__btn--page"
                :class="{ 'common-pagination__btn--active': page === props.currentPage, 'common-pagination__btn--disabled': props.disabled }"
                :disabled="props.disabled" @click="handlePageClick(page)" :title="`第 ${page} 页`">
                {{ page }}
            </button>
        </template>

        <!-- 后导航按钮（下一页、末页） -->
        <button class="common-pagination__btn common-pagination__btn--nav"
            :class="{ 'common-pagination__btn--disabled': props.disabled || props.currentPage >= props.totalPages }"
            :disabled="props.disabled || props.currentPage >= props.totalPages"
            @click="() => handlePageJump(props.currentPage + 1)" title="下一页">
            <i class="fa fa-angle-right"></i>
        </button>
        <button class="common-pagination__btn common-pagination__btn--nav"
            :class="{ 'common-pagination__btn--disabled': props.disabled || props.currentPage >= props.totalPages }"
            :disabled="props.disabled || props.currentPage >= props.totalPages"
            @click="() => handlePageJump(props.totalPages)" title="末页">
            <i class="fa fa-angle-double-right"></i>
        </button>

        <!-- 页码输入框 -->
        <div v-if="props.showInput" class="common-pagination__input-group">
            <span class="common-pagination__input-label">跳至</span>
            <input type="number" class="common-pagination__input" :value="props.currentPage" :min="1"
                :max="props.totalPages" :disabled="props.disabled" @keypress="handlePageInput"
                @blur="handlePageInput" />
            <span class="common-pagination__input-suffix">页 / 共 {{ props.totalPages }} 页</span>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.common-pagination {
    display: flex;
    align-items: center;
    gap: var(--spacing-mini);
    font-family: var(--font-family-base);

    // 尺寸变体 - 使用CSS自定义属性优化
    &--mini {
        --pagination-btn-size: 24px;
        --pagination-input-width: 48px;
        --pagination-font-size: var(--font-size-mini);
    }

    &--small {
        --pagination-btn-size: 28px;
        --pagination-input-width: 52px;
        --pagination-font-size: var(--font-size-small);
    }

    &--base {
        --pagination-btn-size: 32px;
        --pagination-input-width: 56px;
        --pagination-font-size: var(--font-size-base);
    }

    &--large {
        --pagination-btn-size: 40px;
        --pagination-input-width: 64px;
        --pagination-font-size: var(--font-size-large);
    }

    // 按钮基础样式
    &__btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: var(--pagination-btn-size, 32px);
        height: var(--pagination-btn-size, 32px);
        font-size: var(--pagination-font-size, var(--font-size-base));
        border: 1px solid var(--border-light);
        background-color: var(--bg-primary);
        color: var(--text-secondary);
        border-radius: var(--border-radius-base);
        cursor: pointer;
        transition: all var(--transition-base);
        font-weight: var(--font-weight-medium);
        user-select: none;

        &:hover:not(&--disabled) {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            color: white;
            transform: translateY(-1px);
            box-shadow: var(--box-shadow-card);
        }

        &:active:not(&--disabled) {
            transform: translateY(0);
            box-shadow: var(--box-shadow-small);
        }

        &:focus {
            outline: none;
            box-shadow: 0 0 0 2px var(--focus-ring-color);
        }

        // 激活状态（当前页）
        &--active {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            color: white;

            &:hover {
                background-color: var(--primary-light);
                border-color: var(--primary-light);
                transform: none;
            }
        }

        // 禁用状态
        &--disabled {
            opacity: 0.5;
            cursor: not-allowed;
            background-color: var(--bg-secondary);
            color: var(--text-disabled);

            &:hover {
                background-color: var(--bg-secondary);
                border-color: var(--border-light);
                color: var(--text-disabled);
                transform: none;
                box-shadow: none;
            }
        }
    }

    // 省略号
    &__ellipsis {
        display: flex;
        align-items: center;
        justify-content: center;
        width: var(--pagination-btn-size, 32px);
        height: var(--pagination-btn-size, 32px);
        font-size: var(--pagination-font-size, var(--font-size-base));
        color: var(--text-tertiary);
        font-weight: var(--font-weight-medium);
        user-select: none;
    }

    // 输入框组
    &__input-group {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);
        margin-left: var(--spacing-base);
    }

    &__input-label,
    &__input-suffix {
        color: var(--text-secondary);
        font-weight: var(--font-weight-medium);
        font-size: var(--pagination-font-size, var(--font-size-base));
        white-space: nowrap;
    }

    &__input {
        width: var(--pagination-input-width, 56px);
        height: var(--pagination-btn-size, 32px);
        font-size: var(--pagination-font-size, var(--font-size-base));
        border: 1px solid var(--border-light);
        border-radius: var(--border-radius-base);
        padding: 0 var(--spacing-small);
        text-align: center;
        font-family: var(--font-family-base);
        font-weight: var(--font-weight-medium);
        color: var(--text-primary);
        background-color: var(--bg-primary);
        transition: all var(--transition-base);

        &:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px var(--focus-ring-color);
        }

        &:hover:not(:disabled) {
            border-color: var(--primary-light);
        }

        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            background-color: var(--bg-secondary);
            color: var(--text-disabled);
            border-color: var(--border-light);
        }

        // 移除数字输入框的默认箭头
        &::-webkit-outer-spin-button,
        &::-webkit-inner-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }

        &[type=number] {
            -moz-appearance: textfield;
        }
    }

    // 响应式样式
    @include respond-to(sm) {
        gap: var(--spacing-mini);

        &__input-group {
            margin-left: var(--spacing-small);
            gap: var(--spacing-mini);
        }

        // 小屏幕下隐藏部分文字
        &__input-suffix {
            display: none;
        }
    }
}
</style>
