import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: "/",
			name: "home",
			component: () => import("../views/Home.vue"),
		},
		{
			path: "/history",
			name: "history",
			component: () => import("../views/History.vue"),
		},
		{
			path: "/settings",
			name: "settings",
			component: () => import("../views/Settings.vue"),
		},
		{
			path: "/video/:siteId/:vodId",
			name: "videoDetail",
			component: () => import("../views/VideoDetail.vue"),
			props: (route) => ({
				siteId: route.params.siteId,
				vodId: route.params.vodId,
				keyword: route.query.keyword,
				page: route.query.page,
			}),
		},
		{
			path: "/video/:siteId/:vodId/play",
			name: "videoPlayer",
			component: () => import("../views/VideoPlayer.vue"),
			props: (route) => ({
				siteId: route.params.siteId,
				vodId: route.params.vodId,
				keyword: route.query.keyword,
				page: route.query.page,
			}),
		},
	],
});

export default router;
