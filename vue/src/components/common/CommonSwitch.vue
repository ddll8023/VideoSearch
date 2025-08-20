<script setup>
import { computed } from 'vue'

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    },
    size: {
        type: String,
        default: 'base',
        validator: (value) => ['base'].includes(value)
    },
    type: {
        type: String,
        default: 'default',
        validator: (value) => ['default'].includes(value)
    }
})

const emit = defineEmits(['update:modelValue', 'change'])

const switchClasses = computed(() => [
    'common-switch',
    `common-switch--${props.size}`,
    `common-switch--${props.type}`,
    {
        'common-switch--checked': props.modelValue
    }
])

const handleClick = () => {
    const newValue = !props.modelValue
    emit('update:modelValue', newValue)
    emit('change', newValue)
}
</script>

<template>
    <button :class="switchClasses" @click="handleClick" type="button">
        <span class="common-switch__track">
            <span class="common-switch__thumb">
            </span>
        </span>
    </button>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.common-switch {
    position: relative;
    display: inline-flex;
    align-items: center;
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    outline: none;
    transition: var(--transition-base);

    &:focus-visible {
        outline: 2px solid var(--primary-color);
        outline-offset: 2px;
        border-radius: 999px;
    }

    &:active {
        transform: scale(0.98);
    }
}

.common-switch__track {
    position: relative;
    display: block;
    border-radius: 999px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    transition: var(--transition-base);

    // 默认类型 - 使用主色调
    .common-switch--default.common-switch--checked & {
        background: var(--primary-color);
        border-color: var(--primary-color);
    }

    .common-switch--default:hover & {
        border-color: var(--border-dark);
    }

    .common-switch--default.common-switch--checked:hover & {
        background: var(--primary-dark);
        border-color: var(--primary-dark);
    }

    .common-switch--default:active & {
        border-color: var(--primary-color);
    }

    .common-switch--default.common-switch--checked:active & {
        background: var(--primary-color);
        border-color: var(--primary-color);
    }

    // 通用hover效果
    .common-switch:hover:not(.common-switch--checked) & {
        border-color: var(--border-dark);
        background: #e5e7eb;
    }

    // 通用active效果
    .common-switch:active:not(.common-switch--checked) & {
        background: #d1d5db;
        border-color: var(--primary-color);
    }
}

.common-switch__thumb {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary);
    border-radius: 50%;
    box-shadow: var(--box-shadow-base);
    transition: var(--transition-base);
    border: 1px solid var(--border-light);

    // Hover时增强阴影
    .common-switch:hover & {
        box-shadow: var(--box-shadow-large);
    }

    // Active时轻微缩放
    .common-switch:active & {
        transform: scale(0.95);
    }

    // 修复在checked状态下active时的transform
    .common-switch--base.common-switch--checked:active & {
        transform: translateX(18px) scale(0.95);
    }
}

// Base尺寸 - 44x24px (默认)
.common-switch--base {
    .common-switch__track {
        width: 44px;
        height: 24px;
    }

    .common-switch__thumb {
        width: 20px;
        height: 20px;
        top: 1px;
        left: 1px;
    }

    &.common-switch--checked .common-switch__thumb {
        transform: translateX(18px);
    }
}
</style>
