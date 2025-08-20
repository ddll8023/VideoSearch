<script setup>
import { computed } from 'vue'

// Props 定义
const props = defineProps({
    // 按钮类型
    type: {
        type: String,
        default: 'default',
        validator: (value) => ['primary', 'default'].includes(value)
    },
    // 按钮尺寸
    size: {
        type: String,
        default: 'small',
        validator: (value) => ['small', 'large'].includes(value)
    },
    // 禁用状态
    disabled: {
        type: Boolean,
        default: false
    },
    // 图标名称
    icon: {
        type: String,
        default: ''
    },
    // 块级显示
    block: {
        type: Boolean,
        default: false
    },
    // 朴素按钮
    plain: {
        type: Boolean,
        default: false
    },
    // 圆形按钮
    circle: {
        type: Boolean,
        default: false
    }
})

// 事件定义
const emit = defineEmits(['click'])

// 计算样式类名
const buttonClasses = computed(() => {
    return [
        'common-button',
        `common-button--${props.type}`,
        `common-button--${props.size}`,
        {
            'common-button--disabled': props.disabled,
            'common-button--block': props.block,
            'common-button--plain': props.plain,
            'common-button--circle': props.circle
        }
    ]
})

// 点击事件处理
const handleClick = (event) => {
    if (props.disabled) {
        return
    }
    emit('click', event)
}
</script>

<template>
    <button :class="buttonClasses" :disabled="disabled" @click="handleClick">
        <span class="common-button__content">
            <!-- 左侧图标 -->
            <i v-if="icon" :class="['common-button__icon', 'common-button__icon--left', `fa fa-${icon}`]"></i>

            <!-- 文本内容 -->
            <span v-if="!circle" class="common-button__text">
                <slot></slot>
            </span>
        </span>
    </button>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.common-button {
    @include button-reset;

    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid transparent;
    font-family: var(--font-family-base);
    font-weight: var(--font-weight-medium);
    text-align: center;
    vertical-align: middle;
    cursor: pointer;
    user-select: none;
    transition: all var(--transition-base);
    white-space: nowrap;
    text-decoration: none;

    &:focus {
        outline: none;
        box-shadow: 0 0 0 2px var(--focus-ring-color);
    }

    // 小型按钮
    &--small {
        height: 32px;
        padding: 0 var(--spacing-base);
        font-size: var(--font-size-small);
        border-radius: var(--border-radius-base);
    }

    // 大型按钮
    &--large {
        height: 80px;
        padding: 0 var(--spacing-large);
        font-size: var(--font-size-2xl);
        border-radius: var(--border-radius-large);
    }

    // 默认按钮样式
    &--default {
        background-color: var(--bg-primary);
        border-color: var(--border-color);
        color: var(--text-primary);

        &:hover:not(.common-button--disabled) {
            background-color: var(--bg-secondary);
            border-color: var(--primary-color);
            color: var(--primary-color);
        }

        &:active:not(.common-button--disabled) {
            background-color: var(--bg-tertiary);
            transform: translateY(1px);
        }

        &.common-button--plain {
            background-color: transparent;

            &:hover:not(.common-button--disabled) {
                background-color: var(--bg-secondary);
            }
        }
    }

    // 主要按钮样式
    &--primary {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
        color: white;

        &:hover:not(.common-button--disabled) {
            background-color: var(--primary-light);
            border-color: var(--primary-light);
            transform: translateY(-1px);
            box-shadow: var(--shadow-card);
        }

        &:active:not(.common-button--disabled) {
            background-color: var(--primary-dark);
            border-color: var(--primary-dark);
            transform: translateY(1px);
        }

        &.common-button--plain {
            background-color: transparent;
            color: var(--primary-color);

            &:hover:not(.common-button--disabled) {
                background-color: var(--primary-color);
                color: white;
            }
        }
    }



    // 块级按钮
    &--block {
        width: 100%;
        display: flex;
    }

    &--circle {
        border-radius: var(--border-radius-full);
        padding: 0;
        width: 32px;

        &.common-button--large {
            width: 80px;
        }
    }

    // 禁用状态
    &--disabled {
        opacity: 0.5;
        cursor: not-allowed;

        &:hover {
            transform: none !important;
            box-shadow: none !important;
        }
    }



    // 内容区域
    &__content {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--spacing-mini);
    }

    // 图标样式
    &__icon {
        font-size: inherit;

        &--left {
            margin-right: var(--spacing-mini);
        }
    }

    // 文本内容
    &__text {
        display: inline-block;
    }



    // 圆形按钮图标居中修复
    &--circle {
        .common-button__icon {
            margin: 0;
        }
    }
}
</style>