import axios from 'axios';

// 配置基础 URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8787/v1';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器，处理返回数据格式
apiClient.interceptors.response.use(
  (response) => {
    // 假设后端返回的数据格式为 { status, msg, data }
    if (response.data && typeof response.data === 'object') {
      if (response.data.status === 0) {
        return response.data.data;
      } else {
        return Promise.reject(new Error(response.data.msg || 'API request failed'));
      }
    }
    return response.data;
  },
  (error) => {
    // 处理网络错误或服务器错误
    return Promise.reject(error);
  }
);

export default apiClient;
