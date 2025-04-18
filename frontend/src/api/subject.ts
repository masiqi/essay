import apiClient from './api';

export interface Subject {
  id: number;
  name: string;
  created_at: number;
  updated_at: number;
}

// 获取所有科目
export const getSubjects = async (): Promise<Subject[]> => {
  return apiClient.get('/subject');
};

// 获取单个科目
export const getSubject = async (id: number): Promise<Subject> => {
  return apiClient.get(`/subject/${id}`);
};

// 创建科目
export const createSubject = async (data: { name: string }): Promise<Subject> => {
  return apiClient.post('/subject', data);
};

// 更新科目
export const updateSubject = async (id: number, data: { name: string }): Promise<Subject> => {
  return apiClient.put(`/subject/${id}`, data);
};

// 删除科目
export const deleteSubject = async (id: number): Promise<void> => {
  return apiClient.delete(`/subject/${id}`);
};
