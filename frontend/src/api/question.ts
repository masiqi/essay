import apiClient from './api';

export interface Question {
  id: number;
  title: string;
  question: string;
  subjectId: number | null; // 添加 subjectId
  created_at: number;
  updated_at: number;
}

// 获取所有题目
export const getQuestions = async (): Promise<Question[]> => {
  const url = '/question';
  return apiClient.get(url);
};

// 获取单个题目
export const getQuestion = async (id: number): Promise<Question> => {
  return apiClient.get(`/question/${id}`);
};

// 创建题目
// 更新参数类型，添加 subjectId
export const createQuestion = async (data: { id: number, title: string; question: string; subjectId: number }): Promise<Question> => {
  return apiClient.post('/question', data);
};

// 更新题目
// 更新参数类型，添加 subjectId
export const updateQuestion = async (id: number, data: { title: string; question: string; subjectId: number }): Promise<Question> => {
  return apiClient.put(`/question/${id}`, data);
};

// 删除题目
export const deleteQuestion = async (id: number): Promise<void> => {
  return apiClient.delete(`/question/${id}`);
};
