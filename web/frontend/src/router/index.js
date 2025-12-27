import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/banks",
  },
  {
    path: "/banks",
    name: "Banks",
    component: () => import("@/views/BankView.vue"),
  },
  {
    path: "/banks/:id",
    name: "BankDetail",
    component: () => import("@/views/BankDetailView.vue"),
  },
  {
    path: "/papers",
    name: "Papers",
    component: () => import("@/views/PaperView.vue"),
  },
  {
    path: "/papers/create",
    name: "PaperCreate",
    component: () => import("@/views/PaperCreateView.vue"),
  },
  {
    path: "/exam",
    name: "ExamSelect",
    component: () => import("@/views/ExamSelectView.vue"),
  },
  {
    path: "/exam/:paperId",
    name: "Exam",
    component: () => import("@/views/ExamView.vue"),
  },
  {
    path: "/results",
    name: "Results",
    component: () => import("@/views/ResultView.vue"),
  },
  {
    path: "/results/:id",
    name: "ResultDetail",
    component: () => import("@/views/ResultDetailView.vue"),
  },
  {
    path: "/favorites",
    name: "Favorites",
    component: () => import("@/views/FavoriteView.vue"),
  },
  {
    path: "/ai-import",
    name: "AIImport",
    component: () => import("@/views/AIImportView.vue"),
  },
  {
    path: "/settings",
    name: "Settings",
    component: () => import("@/views/SettingsView.vue"),
  },
  {
    path: "/about",
    name: "About",
    component: () => import("@/views/AboutView.vue"),
  },
  {
    path: "/volcano-help",
    name: "VolcanoHelp",
    component: () => import("@/views/VolcanoHelpView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
