<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVideoStore } from '@/stores/video'
import VideoPlayerCore from '@/components/video/VideoPlayerCore.vue'
import CommonButton from '@/components/common/CommonButton.vue'
import CommonCard from '@/components/common/CommonCard.vue'
import AppHeader from '@/components/user/AppHeader.vue'
import BackButton from '@/components/user/BackButton.vue'

const route = useRoute()
const router = useRouter()
const videoStore = useVideoStore()

// 路由参数
const props = defineProps({
    siteId: {
        type: String,
        required: true
    },
    vodId: {
        type: String,
        required: true
    },
    keyword: {
        type: String,
        default: ''
    },
    page: {
        type: [String, Number],
        default: 1
    }
})

// 播放器状态
const isPlayerReady = ref(false)
const isFullscreen = ref(false)

// 剧集列表滚动容器引用
const episodesScrollRef = ref(null)

// 计算属性
const videoInfo = computed(() => videoStore.currentVideo)
const currentPlayUrl = computed(() => {
    if (!videoStore.selectedEpisode || !videoStore.selectedEpisode.url) {
        return ''
    }
    return videoStore.selectedEpisode.url
})

// 当前剧集在列表中的索引
const currentEpisodeIndex = computed(() => {
    if (!videoStore.currentEpisodes || !videoStore.selectedEpisode) return -1
    return videoStore.currentEpisodes.findIndex(ep => ep.url === videoStore.selectedEpisode.url)
})

// 是否有上一集
const hasPrevEpisode = computed(() => currentEpisodeIndex.value > 0)

// 是否有下一集
const hasNextEpisode = computed(() =>
    currentEpisodeIndex.value >= 0 &&
    currentEpisodeIndex.value < videoStore.currentEpisodes.length - 1
)

// 返回详情页
const handleGoBack = () => {
    router.push({
        name: 'videoDetail',
        params: {
            siteId: props.siteId,
            vodId: props.vodId
        },
        query: {
            keyword: props.keyword,
            page: props.page
        }
    })
}

// 切换剧集
const handleEpisodeChange = (episode) => {
    videoStore.setSelectedEpisode(episode)
}

// 上一集
const handlePrevEpisode = () => {
    if (hasPrevEpisode.value) {
        const prevEpisode = videoStore.currentEpisodes[currentEpisodeIndex.value - 1]
        handleEpisodeChange(prevEpisode)
    }
}

// 下一集
const handleNextEpisode = () => {
    if (hasNextEpisode.value) {
        const nextEpisode = videoStore.currentEpisodes[currentEpisodeIndex.value + 1]
        handleEpisodeChange(nextEpisode)
    }
}

// 播放器事件处理
const handlePlayerReady = () => {
    isPlayerReady.value = true
}

const handleFullscreenChange = (fullscreen) => {
    isFullscreen.value = fullscreen
}

// 检查数据是否存在，不存在则重新获取
const checkVideoData = async () => {
    if (!videoStore.hasVideo) {
        try {
            await videoStore.fetchVideoDetail(
                props.keyword || '',
                props.page || 1,
                props.siteId,
                props.vodId
            )
        } catch (error) {
            console.error('获取视频详情失败:', error)
        }
    }
}

// 滚动到当前播放的剧集
const scrollToActiveEpisode = async () => {
    await nextTick()
    if (episodesScrollRef.value && currentEpisodeIndex.value >= 0) {
        const activeButton = episodesScrollRef.value.querySelector('.common-button--primary')
        if (activeButton) {
            activeButton.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            })
        }
    }
}

// 监听选中剧集变化，自动滚动到当前剧集
watch(
    () => videoStore.selectedEpisode,
    () => {
        if (!isFullscreen.value) {
            scrollToActiveEpisode()
        }
    },
    { flush: 'post' }
)

onMounted(() => {
    checkVideoData()
    // 初始化时滚动到当前剧集
    setTimeout(() => {
        scrollToActiveEpisode()
    }, 500)
})

onUnmounted(() => {
    // 不清理视频数据，保持状态供详情页使用
})
</script>

<template>
    <div class="app-layout">
        <!-- 应用头部 -->
        <AppHeader />

        <div class="video-player-page" :class="{ 'video-player-page--fullscreen': isFullscreen }">

            <!-- 加载状态 -->
            <div v-if="videoStore.isLoading" class="video-player-page__loading">
                <div class="loading-spinner">
                    <i class="fa fa-spinner fa-spin"></i>
                </div>
                <p class="loading-text">正在加载视频...</p>
            </div>

            <!-- 错误状态 -->
            <div v-else-if="videoStore.error" class="video-player-page__error">
                <i class="fa fa-exclamation-triangle error-icon"></i>
                <h3 class="error-title">加载失败</h3>
                <p class="error-message">{{ videoStore.error }}</p>
                <CommonButton @click="checkVideoData" variant="primary">重试</CommonButton>
            </div>

            <!-- 播放器内容 -->
            <div v-else-if="videoStore.hasVideo && currentPlayUrl" class="video-player-page__content">
                <!-- 返回按钮和标题区域 -->
                <div v-if="!isFullscreen" class="video-player-page__header">
                    <BackButton @click="handleGoBack" />
                    <div class="header-info">
                        <h2 class="video-title">{{ videoInfo.title }}</h2>
                        <span v-if="videoStore.selectedEpisode?.name" class="episode-name">{{
                            videoStore.selectedEpisode.name }}</span>
                    </div>
                </div>

                <!-- 播放区域容器 -->
                <div class="player-layout">
                    <!-- 主播放区域 -->
                    <div class="main-player-area">
                        <!-- 视频播放器 -->
                        <div class="player-container">
                            <VideoPlayerCore :src="currentPlayUrl" :title="videoInfo.title"
                                :episode="videoStore.selectedEpisode?.name || ''" @ready="handlePlayerReady"
                                @fullscreen-change="handleFullscreenChange" class="video-player" />
                        </div>
                    </div>

                    <!-- 右侧剧集列表 -->
                    <div v-if="!isFullscreen && videoStore.currentEpisodes.length > 1" class="sidebar-episodes">
                        <CommonCard class="episodes-sidebar-card">
                            <div class="episodes-header">
                                <h3 class="episodes-title">剧集列表</h3>
                                <span class="episodes-count">共 {{ videoStore.currentEpisodes.length }} 集</span>
                            </div>

                            <div ref="episodesScrollRef" class="episodes-scroll-container">
                                <div class="episodes-grid">
                                    <CommonButton v-for="(episode, index) in videoStore.currentEpisodes" :key="index"
                                        :type="videoStore.selectedEpisode === episode ? 'primary' : 'default'"
                                        @click="handleEpisodeChange(episode)" class="episodes-btn">
                                        {{ episode.name }}
                                    </CommonButton>
                                </div>
                            </div>
                        </CommonCard>
                    </div>
                </div>
            </div>

            <!-- 无播放源状态 -->
            <div v-else-if="videoStore.hasVideo" class="video-player-page__empty">
                <i class="fa fa-play-circle-o empty-icon"></i>
                <h3 class="empty-title">暂无播放源</h3>
                <p class="empty-message">该视频暂时无法播放</p>
                <CommonButton @click="handleGoBack" variant="outline">返回详情</CommonButton>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.app-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.video-player-page {
    flex: 1;
    background-color: var(--bg-primary);
    display: flex;
    flex-direction: column;

    &--fullscreen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: var(--z-index-modal);
        background-color: #000;
    }







    &__loading,
    &__error,
    &__empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex: 1;
        padding: var(--spacing-3xl);
        text-align: center;
    }

    &__loading {
        .loading-spinner {
            font-size: var(--font-size-3xl);
            color: var(--primary-color);
            margin-bottom: var(--spacing-base);
        }

        .loading-text {
            color: var(--text-secondary);
            font-size: var(--font-size-base);
        }
    }

    &__error {
        .error-icon {
            font-size: var(--font-size-3xl);
            color: var(--danger-color);
            margin-bottom: var(--spacing-base);
        }

        .error-title {
            color: var(--text-primary);
            font-size: var(--font-size-xl);
            font-weight: var(--font-weight-medium);
            margin-bottom: var(--spacing-small);
        }

        .error-message {
            color: var(--text-secondary);
            margin-bottom: var(--spacing-large);
        }
    }

    &__empty {
        .empty-icon {
            font-size: var(--font-size-3xl);
            color: var(--text-tertiary);
            margin-bottom: var(--spacing-base);
        }

        .empty-title {
            color: var(--text-primary);
            font-size: var(--font-size-xl);
            font-weight: var(--font-weight-medium);
            margin-bottom: var(--spacing-small);
        }

        .empty-message {
            color: var(--text-secondary);
            margin-bottom: var(--spacing-large);
        }
    }

    &__content {
        flex: 1;
        display: flex;
        flex-direction: column;
        position: relative;
        max-width: 90vw;
        margin: 0 auto;
        width: 100%;
        padding: var(--spacing-xl);
        padding-top: calc(var(--spacing-xl) + var(--header-height));

        @include respond-to(md) {
            padding: var(--spacing-base);
        }
    }

    &__header {
        display: flex;
        align-items: center;
        gap: var(--spacing-base);
        margin-bottom: var(--spacing-xl);

        .header-info {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-tiny);

            .video-title {
                font-size: var(--font-size-large);
                font-weight: var(--font-weight-medium);
                color: var(--text-primary);
                margin: 0;
                line-height: 1.2;

                @include respond-to(md) {
                    font-size: var(--font-size-base);
                }
            }

            .episode-name {
                font-size: var(--font-size-small);
                color: var(--text-secondary);
                font-weight: var(--font-weight-normal);

                @include respond-to(md) {
                    font-size: var(--font-size-tiny);
                }
            }
        }
    }
}

// 播放区域容器
.player-layout {
    display: flex;
    gap: var(--spacing-xl);

    @include respond-to(lg) {
        flex-direction: row;
        align-items: flex-start;
    }

    @include respond-to(md) {
        gap: var(--spacing-base);
        flex-direction: column;
    }

    @include respond-to(sm) {
        flex-direction: column;
    }
}

// 主播放区域
.main-player-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);

    @include respond-to(md) {
        gap: var(--spacing-base);
    }
}

.player-container {
    position: relative;
    width: 100%;
    background-color: #000;
    border-radius: var(--border-radius-base);
    overflow: hidden;
    box-shadow: var(--box-shadow-card);

    .video-player {
        width: 100%;
        height: 75vh;

        @include respond-to(lg) {
            height: 55vh;
        }

        @include respond-to(md) {
            height: 50vh;
        }

        @include respond-to(sm) {
            height: 40vh;
        }
    }
}

// 右侧剧集列表
.sidebar-episodes {
    width: 360px;
    flex-shrink: 0;

    @include respond-to(xl) {
        width: 300px;
    }

    @include respond-to(lg) {
        width: 280px;
    }

    @include respond-to(md) {
        width: 100%;
        margin-top: var(--spacing-xl);
    }

    .episodes-sidebar-card {
        padding: var(--spacing-large);
        height: fit-content;
        height: 75vh;
        display: flex;
        flex-direction: column;

        @include respond-to(lg) {
            min-height: 55vh;
            max-height: 55vh;
        }

        @include respond-to(md) {
            min-height: 50vh;
            max-height: 50vh;
        }

        @include respond-to(sm) {
            min-height: 40vh;
            max-height: 40vh;
        }
    }

    .episodes-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-large);
        flex-shrink: 0;

        .episodes-title {
            font-size: var(--font-size-large);
            font-weight: var(--font-weight-medium);
            color: var(--text-primary);
            margin: 0;
        }

        .episodes-count {
            font-size: var(--font-size-small);
            color: var(--text-secondary);
        }
    }

    .episodes-scroll-container {
        flex: 1;
        overflow-y: auto;
        height: calc(75vh - 120px);

        @include respond-to(lg) {
            height: calc(55vh - 120px);
        }

        @include respond-to(md) {
            height: calc(50vh - 120px);
        }

        @include respond-to(sm) {
            height: calc(40vh - 120px);
        }

        // 自定义滚动条样式
        &::-webkit-scrollbar {
            width: 6px;
        }

        &::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: var(--border-radius-small);
        }

        &::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: var(--border-radius-small);

            &:hover {
                background: var(--text-tertiary);
            }
        }
    }

    .episodes-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
        gap: var(--spacing-small);

        @include respond-to(lg) {
            grid-template-columns: repeat(2, 1fr);
        }

        @include respond-to(md) {
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        }

        .episodes-btn {
            width: 64px;
        }

    }
}

// 全屏模式下的样式
.video-player-page--fullscreen {
    .player-container {
        height: 100vh;
        border-radius: 0;
        box-shadow: none;

        .video-player {
            height: 100vh;
            min-height: 100vh;
        }
    }
}
</style>