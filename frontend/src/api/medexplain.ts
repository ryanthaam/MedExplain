import axios from 'axios';
import { DrugResponse, DrugOverview } from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com' 
  : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for drug queries
});

export class MedExplainAPI {
  static async queryDrug(question: string): Promise<DrugResponse> {
    try {
      const response = await api.post('/query', {
        question,
        include_safety_check: true
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to query drug information');
      }
      throw error;
    }
  }

  static async getDrugOverview(drugName: string): Promise<DrugOverview> {
    try {
      const response = await api.get(`/drug/${encodeURIComponent(drugName)}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to get drug overview');
      }
      throw error;
    }
  }

  static async suggestDrugs(partialName: string, limit: number = 5): Promise<string[]> {
    try {
      const response = await api.get('/suggest', {
        params: { partial_name: partialName, limit }
      });
      return response.data.suggestions || [];
    } catch (error) {
      console.error('Failed to get drug suggestions:', error);
      return [];
    }
  }

  static async listAllDrugs(): Promise<string[]> {
    try {
      const response = await api.get('/drugs');
      return response.data.drugs || [];
    } catch (error) {
      console.error('Failed to list drugs:', error);
      return [];
    }
  }
}

export default MedExplainAPI;