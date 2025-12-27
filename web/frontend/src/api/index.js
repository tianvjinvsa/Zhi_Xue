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

export default api;
