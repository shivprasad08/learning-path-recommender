import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  createProfile: async (learnerId, data) => {
    const res = await axios.post(`${API_BASE}/profile/${learnerId}`, data);
    return res.data;
  },
  getPath: async (learnerId) => {
    const res = await axios.get(`${API_BASE}/path/${learnerId}`);
    return res.data;
  },
  explainStep: async (learnerId, skillId) => {
    const res = await axios.post(`${API_BASE}/path/${learnerId}/explain`, { learner_id: learnerId, skill_id: skillId });
    return res.data;
  },
  assessStep: async (learnerId, skillId, score) => {
    const res = await axios.post(`${API_BASE}/path/${learnerId}/assess`, { learner_id: learnerId, skill_id: skillId, score });
    return res.data;
  }
};
