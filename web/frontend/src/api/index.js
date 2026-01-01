import axios from "axios";
import { ElMessage } from "element-plus";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 对收藏相关的API请求静默处理错误（不显示错误提示）
    const url = error.config?.url || "";
    if (url.includes("/favorites")) {
      return Promise.reject(error);
    }
    const message = error.response?.data?.detail || error.message || "请求失败";
    ElMessage.error(message);
    return Promise.reject(error);
  }
);

// ============ 题库 API ============
export const bankApi = {
  getAll: () => api.get("/banks"),
  get: (id) => api.get(`/banks/${id}`),
  create: (data) => api.post("/banks", data),
  update: (id, data) => api.put(`/banks/${id}`, data),
  delete: (id) => api.delete(`/banks/${id}`),

  // 章节相关
  getChapters: (bankId) => api.get(`/banks/${bankId}/chapters`),
  addChapter: (bankId, chapter) =>
    api.post(`/banks/${bankId}/chapters`, { chapter }),
  deleteChapter: (bankId, chapter) =>
    api.delete(`/banks/${bankId}/chapters/${encodeURIComponent(chapter)}`),

  // 题目相关
  getQuestions: (bankId) => api.get(`/banks/${bankId}/questions`),
  addQuestion: (bankId, data) => api.post(`/banks/${bankId}/questions`, data),
  updateQuestion: (bankId, questionId, data) =>
    api.put(`/banks/${bankId}/questions/${questionId}`, data),
  deleteQuestion: (bankId, questionId) =>
    api.delete(`/banks/${bankId}/questions/${questionId}`),
  batchAddQuestions: (bankId, questions) =>
    api.post(`/banks/${bankId}/questions/batch`, { questions }),
};

// ============ 试卷 API ============
export const paperApi = {
  getAll: () => api.get("/papers"),
  get: (id) => api.get(`/papers/${id}`),
  getQuestions: (id) => api.get(`/papers/${id}/questions`),
  generate: (config) => api.post("/papers/generate", config),
  delete: (id) => api.delete(`/papers/${id}`),
};

// ============ 考试 API ============
export const examApi = {
  start: (paperId) => api.post(`/exam/start/${paperId}`),
  submitAnswer: (examId, data) => api.post(`/exam/${examId}/answer`, data),
  finish: (examId) => api.post(`/exam/${examId}/submit`),
  getInProgress: () => api.get("/exam/in-progress"),
};

// ============ 结果 API ============
export const resultApi = {
  getAll: () => api.get("/results"),
  get: (id) => api.get(`/results/${id}`),
  delete: (id) => api.delete(`/results/${id}`),
};

// ============ AI API ============
export const aiApi = {
  parse: (content) => api.post("/ai/parse", { content }),
  parseFile: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/ai/parse-file", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000, // 文件解析可能需要更长时间
    });
  },
  getSupportedTypes: () => api.get("/ai/supported-types"),
  generate: (data) => api.post("/ai/generate", data),
  checkConnection: (params) => api.get("/ai/check", { params }),
};

// ============ 配置 API ============
export const configApi = {
  getAI: () => api.get("/config/ai"),
  updateAI: (data) => api.put("/config/ai", data),
  getPaths: () => api.get("/config/paths"),
  updatePaths: (data) => api.put("/config/paths", data),
};

// ============ 数据导入导出 API ============
export const dataApi = {
  export: (data) => api.post("/data/export", data),
  scanImport: (path) => api.get("/data/scan-import", { params: { path } }),
  import: (data) => api.post("/data/import", data),
};

// ============ 收藏 API ============
export const favoriteApi = {
  getAll: () => api.get("/favorites"),
  getStatistics: () => api.get("/favorites/statistics"),
  getBanks: () => api.get("/favorites/banks"),
  add: (bankId, questionId) => api.post(`/favorites/${bankId}/${questionId}`),
  remove: (questionId) => api.delete(`/favorites/${questionId}`),
  check: (questionId) => api.get(`/favorites/check/${questionId}`),
  updateNote: (questionId, note) =>
    api.put(`/favorites/${questionId}/note`, { note }),
  clearAll: () => api.delete("/favorites"),
};

// ============ 系统 API ============
export const systemApi = {
  getVersion: () => api.get("/system/version"),
  checkUpdate: () => api.get("/system/check-update"),
  selectFolder: () => api.get("/system/select-folder"),
  selectFile: (params) => api.get("/system/select-file", { params }),
};

// ============ 题库商城 API (云端) ============
// 配置云端服务器地址，生产环境应改为实际服务器地址
const MARKET_BASE_URL =
  import.meta.env.VITE_MARKET_API_URL || "https://your-server.com/api/market";

const marketInstance = axios.create({
  baseURL: MARKET_BASE_URL,
  timeout: 30000,
});

export const marketApi = {
  // 获取商城题库列表
  getBanks: (params) =>
    marketInstance.get("/banks", { params }).then((r) => r.data),

  // 获取单个题库详情
  getBank: (id) => marketInstance.get(`/banks/${id}`).then((r) => r.data),

  // 预览题库 (部分题目)
  previewBank: (id, limit = 5) =>
    marketInstance
      .get(`/banks/${id}/preview`, { params: { limit } })
      .then((r) => r.data),

  // 下载题库文件
  downloadBank: async (id) => {
    const response = await marketInstance.get(`/banks/${id}/download`, {
      responseType: "blob",
    });
    return response.data;
  },

  // 搜索题库
  search: (q, params = {}) =>
    marketInstance
      .get("/search", { params: { q, ...params } })
      .then((r) => r.data),

  // 获取分类列表
  getCategories: () => marketInstance.get("/categories").then((r) => r.data),

  // 获取科目列表
  getSubjects: () => marketInstance.get("/subjects").then((r) => r.data),

  // 上传题库 (如有权限)
  uploadBank: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return marketInstance
      .post("/banks", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};

export default api;
