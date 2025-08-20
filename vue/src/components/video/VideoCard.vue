<template>
    <div class="video-card" @click="handleCardClick">
        <div class="video-card__poster">
            <img v-if="!hasImageError && video.thumbnail" :src="video.thumbnail" :alt="displayTitle" loading="lazy"
                @error="handleImageError" @load="handleImageLoad" />
            <div v-else class="video-card__placeholder" :class="{ 'video-card__placeholder--loading': isLoading }">
                <i class="fa fa-file-video-o video-card__placeholder-icon"></i>
                <span class="video-card__placeholder-text">{{ isLoading ? '加载中...' : '暂无封面' }}</span>
            </div>
            <div v-if="video.status" class="video-card__status">{{ video.status }}</div>
            <div v-if="video.quality" class="video-card__quality">{{ video.quality }}</div>
        </div>
        <div class="video-card__content">
            <div class="video-card__title" :title="displayTitle">{{ displayTitle }}</div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSearchStore } from '@/stores/search'

const router = useRouter()
const searchStore = useSearchStore()

const props = defineProps({
    video: {
        type: Object,
        required: true
    }
})

// 图片加载状态管理
const hasImageError = ref(!props.video.thumbnail)
const isLoading = ref(!!props.video.thumbnail)

// 统一的标题处理
const displayTitle = computed(() => props.video.title || '暂无标题')

// 图片加载成功处理
const handleImageLoad = () => {
    isLoading.value = false
    hasImageError.value = false
}

// 图片加载错误处理
const handleImageError = () => {
    isLoading.value = false
    hasImageError.value = true
}

// 卡片点击处理
const handleCardClick = () => {
    const video = props.video

    if (!video.platform || !video.id) {
        console.warn('视频信息不完整，无法跳转:', video)
        return
    }

    // 获取当前搜索关键词和站点ID
    const keyword = searchStore.searchKeyword
    const siteId = searchStore.getSiteIdByName(video.platform)

    // 跳转到详情页
    router.push({
        name: 'videoDetail',
        params: {
            siteId: siteId,
            vodId: video.id
        },
        query: {
            keyword: keyword || '',
            page: 1
        }
    })

    console.log('跳转到视频详情:', {
        siteId,
        vodId: video.id,
        keyword,
        title: video.title
    })
}

// 初始化时如果没有缩略图则不显示加载状态
onMounted(() => {
    if (!props.video.thumbnail) {
        isLoading.value = false
        hasImageError.value = true
    }
})
</script>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.video-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-light);
    border-radius: var(--border-radius-base);
    box-shadow: var(--box-shadow-card);
    transition: all var(--transition-base);
    overflow: hidden;
    cursor: pointer;

    &:hover {
        border-color: var(--primary-color);
        box-shadow: var(--box-shadow-card-hover);
        transform: translateY(-2px);
    }

    &__poster {
        position: relative;
        width: 100%;
        height: 280px;
        overflow: hidden;
        background-color: var(--bg-secondary);

        img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: opacity var(--transition-base);
        }
    }

    // 占位符样式优化
    &__placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        color: var(--text-tertiary);
        transition: all var(--transition-base);

        &--loading {
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);

            .video-card__placeholder-icon {
                animation: pulse 1.5s ease-in-out infinite;
            }
        }

        &:hover {
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, #e8e9eb 100%);
            color: var(--text-secondary);
        }
    }

    &__placeholder-icon {
        font-size: 48px;
        margin-bottom: var(--spacing-small);
        color: var(--text-disabled);
        transition: color var(--transition-base);

        .video-card__placeholder--loading & {
            color: var(--primary-color);
        }
    }

    &__placeholder-text {
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
        color: var(--text-tertiary);
        transition: color var(--transition-base);

        .video-card__placeholder--loading & {
            color: var(--text-secondary);
        }
    }

    &__status {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 2px 6px;
        font-size: 11px;
        border-radius: var(--border-radius-small);
        font-weight: var(--font-weight-medium);
    }

    &__quality {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 2px 6px;
        font-size: 11px;
        border-radius: var(--border-radius-small);
        font-weight: var(--font-weight-medium);
    }

    &__content {
        padding: var(--spacing-small);
    }

    &__title {
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
        line-height: var(--line-height-tight);
        color: var(--text-primary);
        @include text-ellipsis(1);
        min-height: 20px;
    }

    // 响应式适配
    @include respond-to(md) {
        &__poster {
            height: 240px;
        }

        &__placeholder-icon {
            font-size: 40px;
        }
    }

    @include respond-to(sm) {
        &__poster {
            height: 220px;
        }

        &__placeholder-icon {
            font-size: 36px;
        }

        &__content {
            padding: var(--spacing-mini);
        }

        &__title {
            font-size: var(--font-size-mini);
            min-height: 28px;
        }
    }
}

// 脉冲动画关键帧
@keyframes pulse {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.5;
    }
}
</style>