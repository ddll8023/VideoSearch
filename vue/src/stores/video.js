import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { getVideoDetail } from "@/services/api";

export const useVideoStore = defineStore("video", () => {
	// 状态
	const currentVideo = ref(null);
	const isLoading = ref(false);
	const error = ref(null);
	const selectedPlaySource = ref(null);
	const selectedEpisode = ref(null);

	// 播放状态
	const currentPlayUrl = ref("");
	const playProgress = ref(0);
	const playDuration = ref(0);
	const isPlaying = ref(false);

	// 计算属性
	const hasVideo = computed(() => currentVideo.value !== null);
	const hasPlaySources = computed(() => {
		return (
			currentVideo.value?.play_sources &&
			Object.keys(currentVideo.value.play_sources).length > 0
		);
	});

	const availableFormats = computed(() => {
		if (!hasPlaySources.value) return [];
		return Object.keys(currentVideo.value.play_sources).map((format) => ({
			key: format,
			name: format.toUpperCase(),
			episodes: currentVideo.value.play_sources[format] || [],
		}));
	});

	const currentEpisodes = computed(() => {
		if (!selectedPlaySource.value || !hasPlaySources.value) return [];
		return currentVideo.value.play_sources[selectedPlaySource.value] || [];
	});

	// 动作
	const setLoading = (status) => {
		isLoading.value = status;
	};

	const setError = (errorMsg) => {
		error.value = errorMsg;
	};

	const clearError = () => {
		error.value = null;
	};

	const setCurrentVideo = (video) => {
		currentVideo.value = video;
		// 自动选择第一个播放源和第一集
		if (video?.play_sources) {
			const formats = Object.keys(video.play_sources);
			if (formats.length > 0) {
				selectedPlaySource.value = formats[0];
				const episodes = video.play_sources[formats[0]];
				if (episodes && episodes.length > 0) {
					selectedEpisode.value = episodes[0];
				}
			}
		}
	};

	const setSelectedPlaySource = (format) => {
		selectedPlaySource.value = format;
		// 切换播放源时自动选择第一集
		if (currentVideo.value?.play_sources?.[format]?.length > 0) {
			selectedEpisode.value = currentVideo.value.play_sources[format][0];
		}
	};

	const setSelectedEpisode = (episode) => {
		selectedEpisode.value = episode;
		// 更新播放URL
		if (episode && episode.url) {
			currentPlayUrl.value = episode.url;
		}
	};

	// 播放状态管理
	const setPlayProgress = (progress, duration) => {
		playProgress.value = progress;
		if (duration) {
			playDuration.value = duration;
		}
	};

	const setPlayingState = (playing) => {
		isPlaying.value = playing;
	};

	const fetchVideoDetail = async (
		keyword,
		page,
		siteId,
		vodId,
		forceRefresh = false
	) => {
		try {
			// 检查是否已有数据且不强制刷新
			if (
				!forceRefresh &&
				currentVideo.value &&
				currentVideo.value.id === vodId
			) {
				console.log("使用缓存的视频详情数据");
				return { success: true, video: currentVideo.value };
			}

			setLoading(true);
			clearError();

			const response = await getVideoDetail(keyword, page, siteId, vodId);

			if (response.success && response.video) {
				setCurrentVideo(response.video);
				console.log("视频详情获取成功:", response.video);
				return response;
			} else {
				throw new Error(response.message || "获取视频详情失败");
			}
		} catch (err) {
			console.error("获取视频详情失败:", err);
			setError(err.message || "网络错误，请稍后重试");
			throw err;
		} finally {
			setLoading(false);
		}
	};

	const clearVideo = () => {
		currentVideo.value = null;
		selectedPlaySource.value = null;
		selectedEpisode.value = null;
		error.value = null;
		// 清理播放状态
		currentPlayUrl.value = "";
		playProgress.value = 0;
		playDuration.value = 0;
		isPlaying.value = false;
	};

	return {
		// 状态
		currentVideo,
		isLoading,
		error,
		selectedPlaySource,
		selectedEpisode,

		// 播放状态
		currentPlayUrl,
		playProgress,
		playDuration,
		isPlaying,

		// 计算属性
		hasVideo,
		hasPlaySources,
		availableFormats,
		currentEpisodes,

		// 动作
		setLoading,
		setError,
		clearError,
		setCurrentVideo,
		setSelectedPlaySource,
		setSelectedEpisode,
		fetchVideoDetail,
		clearVideo,

		// 播放动作
		setPlayProgress,
		setPlayingState,
	};
});
