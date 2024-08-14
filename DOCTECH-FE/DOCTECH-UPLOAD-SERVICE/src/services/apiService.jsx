//src/services/apiService.jsx

import axios from 'axios';

const apiService = axios.create({
  baseURL: import.meta.env.VITE_REACT_APP_API_BASE_URL,
  headers: {
    'x-api-key': import.meta.env.VITE_REACT_APP_API_KEY,
  },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiService.post('/v1/text-extract', formData);
    return response.data;
  } catch (error) {
    throw new Error(error.response ? error.response.data : 'Upload failed');
  }
};
