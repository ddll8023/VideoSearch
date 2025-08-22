<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVideoStore } from '@/stores/video'
import { useSearchStore } from '@/stores/search'
import CommonButton from '@/components/common/CommonButton.vue'
import CommonCard from '@/components/common/CommonCard.vue'
import CommonTab from '@/components/common/CommonTab.vue'
import AppHeader from '@/components/user/AppHeader.vue'
import BackButton from '@/components/user/BackButton.vue'

const route = useRoute()
const router = useRouter()
const videoStore = useVideoStore()
const searchStore = useSearchStore()

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

// 播放器状态已移除

// 计算属性
const videoInfo = computed(() => videoStore.currentVideo)

// 转换播放源数据为CommonTab格式
const playSourceTabs = computed(() => {
    if (!videoStore.availableFormats) return []
    return videoStore.availableFormats.map(format => {
        const formatMap = {
            'm3u8': 'M3U8',
            'mp4': 'MP4',
            'mkv': 'MKV',
            'avi': 'AVI'
        }
        const formatName = formatMap[format.key.toLowerCase()] || format.key.toUpperCase()

        return {
            id: format.key,
            name: formatName,
            count: format.episodes.length
        }
    })
})

// 返回搜索结果
const handleGoBack = () => {
    const query = {}

    // 优先使用props中的keyword，其次使用store中的搜索关键词
    const keyword = props.keyword || searchStore.searchKeyword
    if (keyword) {
        query.q = keyword
    }

    // 如果有活跃的tab，添加tab参数
    if (searchStore.activeTab) {
        query.tab = searchStore.activeTab
    }

    // 如果有当前页码信息，添加页码参数
    if (searchStore.currentTabPagination?.current_page > 1) {
        query.page = searchStore.currentTabPagination.current_page
    }

    router.push({
        name: 'home',
        query: Object.keys(query).length > 0 ? query : undefined
    })
}

// 切换播放源
const handleTabChange = (tabId) => {
    videoStore.setSelectedPlaySource(tabId)
}

// 切换剧集 - 跳转到播放页面
const handleEpisodeChange = (episode) => {
    // 设置选中的剧集
    videoStore.setSelectedEpisode(episode)

    // 跳转到播放页面
    router.push({
        name: 'videoPlayer',
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



// 获取视频详情
const fetchVideoDetail = async () => {
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

onMounted(() => {
    fetchVideoDetail()
})

onUnmounted(() => {
    // 清理状态（可选）
    // videoStore.clearVideo()
})
</script>

<template>
    <div class="app-layout">
        <!-- 应用头部 -->
        <AppHeader />

        <div class="video-detail">

            <!-- 加载状态 -->
            <div v-if="videoStore.isLoading" class="video-detail__loading">
                <div class="loading-spinner">
                    <i class="fa fa-spinner fa-spin"></i>
                </div>
                <p class="loading-text">正在获取视频详情...</p>
            </div>

            <!-- 错误状态 -->
            <div v-else-if="videoStore.error" class="video-detail__error">
                <i class="fa fa-exclamation-triangle error-icon"></i>
                <h3 class="error-title">获取失败</h3>
                <p class="error-message">{{ videoStore.error }}</p>
                <CommonButton @click="fetchVideoDetail" variant="primary">重试</CommonButton>
            </div>

            <!-- 视频详情内容 -->
            <div v-else-if="videoStore.hasVideo" class="video-detail__content">
                <!-- 返回按钮 -->
                <div class="video-detail__back-button">
                    <BackButton @click="handleGoBack" />
                </div>

                <!-- 视频基本信息 -->
                <CommonCard class="video-info-card">
                    <div class="video-info">
                        <div class="video-info__poster">
                            <img v-if="videoInfo.thumbnail" :src="videoInfo.thumbnail" :alt="videoInfo.title"
                                class="poster-image" />
                            <div v-else class="poster-placeholder">
                                <i class="fa fa-image"></i>
                            </div>
                        </div>

                        <div class="video-info__details">
                            <h1 class="video-title">{{ videoInfo.title }}</h1>

                            <div class="video-meta">
                                <!-- 第一行：状态、年份、地区 -->
                                <div class="meta-row">
                                    <div v-if="videoInfo.status" class="meta-item">
                                        <span class="meta-label">状态:</span>
                                        <span class="meta-value">{{ videoInfo.status }}</span>
                                    </div>
                                    <div v-if="videoInfo.year" class="meta-item">
                                        <span class="meta-label">年份:</span>
                                        <span class="meta-value">{{ videoInfo.year }}</span>
                                    </div>
                                    <div v-if="videoInfo.area" class="meta-item">
                                        <span class="meta-label">地区:</span>
                                        <span class="meta-value">{{ videoInfo.area }}</span>
                                    </div>
                                </div>

                                <!-- 第二行：语言、类型、演员 -->
                                <div class="meta-row">
                                    <div v-if="videoInfo.language" class="meta-item">
                                        <span class="meta-label">语言:</span>
                                        <span class="meta-value">{{ videoInfo.language }}</span>
                                    </div>
                                    <div v-if="videoInfo.channel" class="meta-item">
                                        <span class="meta-label">类型:</span>
                                        <span class="meta-value">{{ videoInfo.channel }}</span>
                                    </div>
                                    <div v-if="videoInfo.actor" class="meta-item">
                                        <span class="meta-label">演员:</span>
                                        <span class="meta-value">{{ videoInfo.actor }}</span>
                                    </div>
                                </div>
                            </div>

                            <div v-if="videoInfo.description" class="video-description">
                                <h3 class="description-title">剧情简介</h3>
                                <div class="description-content" v-html="videoInfo.description"></div>
                            </div>
                        </div>
                    </div>
                </CommonCard>

                <!-- 播放源选择 -->
                <CommonCard v-if="videoStore.hasPlaySources" class="play-sources-card">
                    <div class="play-sources">
                        <h3 class="sources-title">播放源</h3>

                        <!-- 播放格式选择 -->
                        <CommonTab :tabs="playSourceTabs" :activeTab="videoStore.selectedPlaySource"
                            @tab-change="handleTabChange" class="format-tabs" />

                        <!-- 剧集列表 -->
                        <div v-if="videoStore.currentEpisodes.length > 0" class="episodes-list">
                            <h4 class="episodes-title">选择集数</h4>
                            <div class="episodes-grid">
                                <CommonButton v-for="(episode, index) in videoStore.currentEpisodes" :key="index"
                                    :type="videoStore.selectedEpisode === episode ? 'primary' : 'default'"
                                    @click="handleEpisodeChange(episode)">
                                    {{ episode.name }}
                                </CommonButton>
                            </div>
                        </div>
                    </div>
                </CommonCard>
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

.video-detail {
    flex: 1;
    background-color: var(--bg-primary);

    &__header {
        padding: var(--spacing-base) var(--spacing-xl);
        background-color: var(--bg-primary);
    }



    &__loading,
    &__error {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 400px;
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
            line-height: var(--line-height-base);
        }
    }

    &__content {
        padding: var(--spacing-xl);
        max-width: 90vw;
        margin: 0 auto;
        padding-top: calc(var(--spacing-xl) + var(--header-height));
    }

    &__back-button {
        margin-bottom: var(--spacing-xl);
    }
}

// 视频信息卡片
.video-info-card {
    margin-bottom: var(--spacing-xl);
}

// 播放源卡片
.play-sources-card {
    margin-bottom: var(--spacing-xl);


}



.video-info {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: var(--spacing-xl);

    @include respond-to(md) {
        grid-template-columns: 150px 1fr;
        gap: var(--spacing-large);
    }

    @include respond-to(sm) {
        grid-template-columns: 1fr;
        gap: var(--spacing-base);
    }

    &__poster {
        .poster-image {
            width: 100%;
            height: auto;
            border-radius: var(--border-radius-base);
            box-shadow: var(--box-shadow-card);
        }

        .poster-placeholder {
            width: 100%;
            aspect-ratio: 3/4;
            background-color: var(--bg-secondary);
            border-radius: var(--border-radius-base);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-tertiary);
            font-size: var(--font-size-2xl);
        }
    }

    &__details {
        .video-title {
            font-size: var(--font-size-2xl);
            font-weight: var(--font-weight-bold);
            color: var(--text-primary);
            margin-bottom: var(--spacing-large);
            line-height: var(--line-height-tight);
        }
    }
}

.video-meta {
    margin-bottom: var(--spacing-large);

    .meta-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--spacing-base);
        margin-bottom: var(--spacing-small);

        &:last-child {
            margin-bottom: 0;
        }
    }

    .meta-item {
        display: flex;
        gap: var(--spacing-small);
        min-width: 0;
        /* 允许flex item收缩 */

        .meta-label {
            color: var(--text-secondary);
            font-weight: var(--font-weight-medium);
            flex-shrink: 0;
        }

        .meta-value {
            color: var(--text-primary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            min-width: 0;
            /* 允许文本收缩 */
        }
    }
}

.video-description {
    .description-title {
        font-size: var(--font-size-large);
        font-weight: var(--font-weight-medium);
        color: var(--text-primary);
        margin-bottom: var(--spacing-base);
    }

    .description-content {
        color: var(--text-secondary);
        line-height: var(--line-height-loose);

        p {
            margin-bottom: var(--spacing-base);
        }
    }
}

.play-sources {
    .sources-title {
        font-size: var(--font-size-large);
        font-weight: var(--font-weight-medium);
        color: var(--text-primary);
        margin-bottom: var(--spacing-large);
    }

    .format-tabs {
        margin-bottom: var(--spacing-large);
        border-bottom: 1px solid var(--border-light);
        position: relative;

    }
}



.episodes-list {
    .episodes-title {
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-medium);
        color: var(--text-primary);
        margin-bottom: var(--spacing-base);
    }

    .episodes-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: var(--spacing-small);


    }
}
</style>