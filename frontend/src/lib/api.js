/**
 * API client for TG-Otvet backend
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || window.location.origin;

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
});

// ============== Projects API ==============
export const projectsAPI = {
    getAll: () => api.get('/api/projects'),
    getById: (id) => api.get(`/api/projects/${id}`),
    create: (data) => api.post('/api/projects', data),
    delete: (id) => api.delete(`/api/projects/${id}`)
};

// ============== Users API ==============
export const usersAPI = {
    getByProject: (projectId) => api.get('/api/users', { params: { project_id: projectId } }),
    getById: (id) => api.get(`/api/users/${id}`),
    updateStatus: (id, status) => api.put(`/api/users/${id}/status`, { status }),
    delete: (id) => api.delete(`/api/users/${id}`)
};

// ============== Funnel API ==============
export const funnelAPI = {
    getSteps: (projectId) => api.get('/api/funnel/steps', { params: { project_id: projectId } }),
    createStep: (data) => api.post('/api/funnel/steps', data),
    updateStep: (stepId, data) => api.put(`/api/funnel/steps/${stepId}`, data),
    deleteStep: (stepId, projectId) => api.delete(`/api/funnel/steps/${stepId}`, { params: { project_id: projectId } })
};

// ============== Media API ==============
export const mediaAPI = {
    getByProject: (projectId) => api.get('/api/media', { params: { project_id: projectId } }),
    upload: (projectId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', projectId);
        return api.post('/api/media/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    delete: (id) => api.delete(`/api/media/${id}`),
    getFileUrl: (projectId, filename) => `/media/${projectId}/${filename}`
};

// ============== Broadcasts API ==============
export const broadcastsAPI = {
    getByProject: (projectId) => api.get('/api/broadcasts', { params: { project_id: projectId } }),
    create: (data) => api.post('/api/broadcasts', data),
    update: (id, data) => api.put(`/api/broadcasts/${id}`, data),
    start: (id) => api.post(`/api/broadcasts/${id}/start`),
    delete: (id) => api.delete(`/api/broadcasts/${id}`)
};

export default api;
