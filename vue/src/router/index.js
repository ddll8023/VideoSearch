import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		// 用户端路由
		{
			path: "/",
			name: "home",
			component: () => import("../views/user/Home.vue"),
		},
		{
			path: "/history",
			name: "history",
			component: () => import("../views/user/History.vue"),
		},
		{
			path: "/settings",
			name: "settings",
			component: () => import("../views/user/Settings.vue"),
		},
		{
			path: "/video/:siteId/:vodId",
			name: "videoDetail",
			component: () => import("../views/user/VideoDetail.vue"),
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
			component: () => import("../views/user/VideoPlayer.vue"),
			props: (route) => ({
				siteId: route.params.siteId,
				vodId: route.params.vodId,
				keyword: route.query.keyword,
				page: route.query.page,
			}),
		},
		// 管理端路由
		{
			path: "/admin",
			name: "adminDashboard",
			component: () => import("../views/admin/Dashboard.vue"),
		},
	],
});

export default router;
