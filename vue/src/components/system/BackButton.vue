<script setup>
// 事件定义
const emit = defineEmits(['click'])

// 点击事件处理
const handleClick = (event) => {
    emit('click', event)
}
</script>

<template>
    <button class="back-button" @click="handleClick">
        <i class="fa fa-arrow-left"></i>
    </button>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.back-button {
    @include button-reset;

    width: 40px;
    height: 40px;
    border-radius: 50%;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border-light);
    background-color: var(--bg-primary);
    color: var(--text-primary);
    transition: all var(--transition-base);
    cursor: pointer;
    user-select: none;

    &:hover {
        border-color: var(--primary-color);
        background-color: var(--bg-secondary);
        color: var(--primary-color);
    }

    &:active {
        background-color: var(--bg-tertiary);
        transform: translateY(1px);
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 0 2px var(--focus-ring-color);
    }

    i {
        font-size: var(--font-size-base);
    }
}
</style>