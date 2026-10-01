import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
});

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  sources?: { title: string; url: string }[];
}

export interface Conversation {
  id: number;
  title: string;
  messages: Message[];
}

export const chatAPI = {
  getConversations: async () => {
    const response = await api.get('/chat/conversations');
    return response.data;
  },
  
  getConversation: async (id: number) => {
    const response = await api.get(`/chat/conversations/${id}`);
    return response.data;
  },
  
  sendMessage: async (message: string, conversationId?: number, fileId?: number) => {
    const response = await api.post('/chat', {
      message,
      conversation_id: conversationId,
      file_id: fileId
    });
    return response.data;
  },
  
  uploadDocument: async (file: File, conversationId?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    if (conversationId) {
      formData.append('conversation_id', conversationId.toString());
    }
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
};
