<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Hls from 'hls.js'
import CommonButton from '@/components/common/CommonButton.vue'

const props = defineProps({
    src: {
        type: String,
        required: true
    },
    title: {
        type: String,
        default: ''
    },
    episode: {
        type: String,
        default: ''
    },
    autoplay: {
        type: Boolean,
        default: true
    },
    controls: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(['ready', 'fullscreen-change', 'time-update', 'ended'])

// 播放器引用
const videoRef = ref(null)
const containerRef = ref(null)

// 播放器状态
const isPlaying = ref(false)
const isLoading = ref(false)
const isFullscreen = ref(false)
const volume = ref(1)
const currentTime = ref(0)
const duration = ref(0)
const buffered = ref(0)
const error = ref(null)

// HLS 实例
let hls = null

// 格式检测
const isHLS = (url) => {
    return url && (url.includes('.m3u8') || url.toLowerCase().includes('m3u8'))
}

// 初始化播放器
const initPlayer = async () => {
    if (!videoRef.value || !props.src) return

    try {
        isLoading.value = true
        error.value = null

        // 清理之前的实例
        if (hls) {
            hls.destroy()
            hls = null
        }

        const video = videoRef.value

        if (isHLS(props.src)) {
            // HLS 流媒体播放
            if (Hls.isSupported()) {
                hls = new Hls({
                    enableWorker: true,
                    lowLatencyMode: false,
                    backBufferLength: 90
                })

                hls.loadSource(props.src)
                hls.attachMedia(video)

                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    console.log('HLS manifest parsed')
                    if (props.autoplay) {
                        video.play().catch(e => {
                            console.log('Autoplay failed:', e)
                        })
                    }
                })

                hls.on(Hls.Events.ERROR, (event, data) => {
                    console.error('HLS error:', data)
                    if (data.fatal) {
                        error.value = `播放错误: ${data.details || '未知错误'}`
                    }
                })

            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                // Safari 原生支持
                video.src = props.src
                if (props.autoplay) {
                    video.play().catch(e => {
                        console.log('Autoplay failed:', e)
                    })
                }
            } else {
                error.value = '您的浏览器不支持HLS播放'
            }
        } else {
            // 普通视频文件
            video.src = props.src
            if (props.autoplay) {
                video.play().catch(e => {
                    console.log('Autoplay failed:', e)
                })
            }
        }

    } catch (err) {
        console.error('播放器初始化失败:', err)
        error.value = `初始化失败: ${err.message}`
    } finally {
        isLoading.value = false
    }
}

// 播放控制
const play = () => {
    if (videoRef.value) {
        videoRef.value.play()
    }
}

const pause = () => {
    if (videoRef.value) {
        videoRef.value.pause()
    }
}

const togglePlay = () => {
    if (isPlaying.value) {
        pause()
    } else {
        play()
    }
}

const setCurrentTime = (time) => {
    if (videoRef.value) {
        videoRef.value.currentTime = time
    }
}

const setVolume = (vol) => {
    if (videoRef.value) {
        videoRef.value.volume = Math.max(0, Math.min(1, vol))
        volume.value = videoRef.value.volume
    }
}

// 全屏控制
const enterFullscreen = async () => {
    try {
        if (containerRef.value.requestFullscreen) {
            await containerRef.value.requestFullscreen()
        } else if (containerRef.value.webkitRequestFullscreen) {
            await containerRef.value.webkitRequestFullscreen()
        } else if (containerRef.value.mozRequestFullScreen) {
            await containerRef.value.mozRequestFullScreen()
        }
    } catch (err) {
        console.error('进入全屏失败:', err)
    }
}

const exitFullscreen = async () => {
    try {
        if (document.exitFullscreen) {
            await document.exitFullscreen()
        } else if (document.webkitExitFullscreen) {
            await document.webkitExitFullscreen()
        } else if (document.mozCancelFullScreen) {
            await document.mozCancelFullScreen()
        }
    } catch (err) {
        console.error('退出全屏失败:', err)
    }
}

const toggleFullscreen = () => {
    if (isFullscreen.value) {
        exitFullscreen()
    } else {
        enterFullscreen()
    }
}

// 事件处理器
const handlePlay = () => {
    isPlaying.value = true
}

const handlePause = () => {
    isPlaying.value = false
}

const handleTimeUpdate = () => {
    if (videoRef.value) {
        currentTime.value = videoRef.value.currentTime
        emit('time-update', currentTime.value)
    }
}

const handleDurationChange = () => {
    if (videoRef.value) {
        duration.value = videoRef.value.duration || 0
    }
}

const handleProgress = () => {
    if (videoRef.value && videoRef.value.buffered.length > 0) {
        buffered.value = videoRef.value.buffered.end(0)
    }
}

const handleLoadedData = () => {
    isLoading.value = false
    emit('ready')
}

const handleError = (e) => {
    console.error('Video error:', e)
    error.value = '视频加载失败'
    isLoading.value = false
}

const handleEnded = () => {
    isPlaying.value = false
    emit('ended')
}

// 全屏状态监听
const handleFullscreenChange = () => {
    const fullscreenElement = document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement

    isFullscreen.value = !!fullscreenElement
    emit('fullscreen-change', isFullscreen.value)
}

// 格式化时间
const formatTime = (seconds) => {
    if (!seconds || !isFinite(seconds)) return '00:00'

    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 监听src变化重新初始化
watch(() => props.src, () => {
    if (props.src) {
        nextTick(() => {
            initPlayer()
        })
    }
}, { immediate: true })

// 生命周期
onMounted(() => {
    // 添加全屏事件监听
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
    // 清理HLS实例
    if (hls) {
        hls.destroy()
        hls = null
    }

    // 移除全屏事件监听
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
})

// 暴露方法
defineExpose({
    play,
    pause,
    togglePlay,
    setCurrentTime,
    setVolume,
    toggleFullscreen,
    enterFullscreen,
    exitFullscreen
})
</script>

<template>
    <div ref="containerRef" class="video-player-core" :class="{ 'video-player-core--fullscreen': isFullscreen }">
        <!-- 视频元素 -->
        <video ref="videoRef" class="video-player-core__video" :controls="controls" preload="metadata"
            crossorigin="anonymous" playsinline @play="handlePlay" @pause="handlePause" @timeupdate="handleTimeUpdate"
            @durationchange="handleDurationChange" @progress="handleProgress" @loadeddata="handleLoadedData"
            @error="handleError" @ended="handleEnded">
            您的浏览器不支持视频播放
        </video>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="video-player-core__loading">
            <div class="loading-spinner">
                <i class="fa fa-spinner fa-spin"></i>
            </div>
            <p class="loading-text">正在加载视频...</p>
        </div>

        <!-- 错误状态 -->
        <div v-if="error" class="video-player-core__error">
            <i class="fa fa-exclamation-triangle error-icon"></i>
            <p class="error-text">{{ error }}</p>
            <CommonButton @click="initPlayer" type="primary" icon="refresh">
                重试
            </CommonButton>
        </div>

        <!-- 自定义控制栏 -->
        <div v-if="!controls && !isLoading && !error" class="video-player-core__controls">
            <!-- 播放/暂停按钮 -->
            <CommonButton @click="togglePlay" :icon="isPlaying ? 'pause' : 'play'" circle plain />

            <!-- 进度条 -->
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-buffer"
                        :style="{ width: duration ? (buffered / duration * 100) + '%' : '0%' }"></div>
                    <div class="progress-current"
                        :style="{ width: duration ? (currentTime / duration * 100) + '%' : '0%' }"></div>
                    <input type="range" class="progress-slider" :min="0" :max="duration" :value="currentTime"
                        @input="setCurrentTime($event.target.value)" />
                </div>

                <div class="time-display">
                    <span class="current-time">{{ formatTime(currentTime) }}</span>
                    <span class="divider">/</span>
                    <span class="duration">{{ formatTime(duration) }}</span>
                </div>
            </div>

            <!-- 音量控制 -->
            <div class="volume-container">
                <CommonButton @click="setVolume(volume === 0 ? 1 : 0)"
                    :icon="volume === 0 ? 'volume-off' : volume < 0.5 ? 'volume-down' : 'volume-up'" circle plain />
                <input type="range" class="volume-slider" min="0" max="1" step="0.1" :value="volume"
                    @input="setVolume($event.target.value)" />
            </div>

            <!-- 全屏按钮 -->
            <CommonButton @click="toggleFullscreen" :icon="isFullscreen ? 'compress' : 'expand'" circle plain />
        </div>

        <!-- 视频信息覆盖层 -->
        <div v-if="(title || episode) && !isPlaying && !isLoading" class="video-player-core__overlay">
            <div class="video-info">
                <h3 v-if="title" class="video-title">{{ title }}</h3>
                <p v-if="episode" class="episode-title">{{ episode }}</p>
            </div>
            <CommonButton @click="togglePlay" icon="play" circle size="large" plain />
        </div>
    </div>
</template>

<style scoped lang="scss">
@use "@/assets/styles/index.scss" as *;

.video-player-core {
    position: relative;
    width: 100%;
    height: 100%;
    background-color: #000;
    display: flex;
    align-items: center;
    justify-content: center;

    &--fullscreen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: var(--z-index-modal);
    }

    &__video {
        width: 100%;
        height: 100%;
        object-fit: contain;
        outline: none;
    }

    &__loading,
    &__error {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--spacing-base);
        color: white;
        text-align: center;
        z-index: 10;

        .loading-spinner {
            font-size: var(--font-size-2xl);
        }

        .loading-text,
        .error-text {
            font-size: var(--font-size-base);
            margin: 0;
        }

        .error-icon {
            font-size: var(--font-size-2xl);
            color: var(--danger-color);
        }


    }

    &__controls {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
        color: white;
        padding: var(--spacing-large);
        display: flex;
        align-items: center;
        gap: var(--spacing-base);
        opacity: 0;
        transition: opacity var(--transition-base);

        @include respond-to(md) {
            padding: var(--spacing-base);
            gap: var(--spacing-small);
        }
    }

    &:hover &__controls {
        opacity: 1;
    }



    .progress-container {
        flex: 1;
        display: flex;
        align-items: center;
        gap: var(--spacing-base);

        .progress-bar {
            flex: 1;
            height: 4px;
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 2px;
            position: relative;
            cursor: pointer;

            .progress-buffer {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 2px;
                transition: width var(--transition-fast);
            }

            .progress-current {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                background-color: var(--primary-color);
                border-radius: 2px;
                transition: width var(--transition-fast);
            }

            .progress-slider {
                position: absolute;
                top: 50%;
                left: 0;
                width: 100%;
                height: 20px;
                margin-top: -10px;
                opacity: 0;
                cursor: pointer;
            }
        }

        .time-display {
            font-size: var(--font-size-small);
            font-family: var(--font-family-number);
            white-space: nowrap;

            .divider {
                margin: 0 2px;
            }
        }
    }

    .volume-container {
        display: flex;
        align-items: center;
        gap: var(--spacing-small);

        @include respond-to(md) {
            .volume-slider {
                display: none;
            }
        }

        .volume-slider {
            width: 80px;
            cursor: pointer;
        }
    }

    &__overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        text-align: center;
        z-index: 5;

        .video-info {
            margin-bottom: var(--spacing-xl);

            .video-title {
                font-size: var(--font-size-xl);
                font-weight: var(--font-weight-medium);
                margin-bottom: var(--spacing-small);
            }

            .episode-title {
                font-size: var(--font-size-base);
                color: rgba(255, 255, 255, 0.8);
                margin: 0;
            }
        }


    }
}
</style>