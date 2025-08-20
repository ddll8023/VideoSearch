<template>
  <div class="common-card">
    <!-- 头部插槽 -->
    <div v-if="$slots.header" class="common-card__header">
      <slot name="header"></slot>
    </div>

    <!-- 主体内容插槽 -->
    <div class="common-card__body">
      <slot></slot>
    </div>

    <!-- 底部插槽 -->
    <div v-if="$slots.footer" class="common-card__footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
// 保留props以保持组件接口兼容性，但简化实现
defineProps({
  size: {
    type: String,
    default: 'base'
  },
  variant: {
    type: String,
    default: 'default'
  }
})
</script>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.common-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--border-radius-base);
  transition: all var(--transition-base);
  overflow: hidden;
  position: relative;
  box-shadow: var(--box-shadow-card);

  // 卡片区域
  &__header {
    padding: var(--spacing-base);
    border-bottom: 1px solid var(--border-light);
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  }

  &__body {
    padding: var(--spacing-base);
    flex: 1;
  }

  &__footer {
    padding: var(--spacing-base);
    border-top: 1px solid var(--border-light);
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  }

  // 响应式适配
  @include respond-to(sm) {

    &__header,
    &__body,
    &__footer {
      padding: var(--spacing-small);
    }
  }
}
</style>