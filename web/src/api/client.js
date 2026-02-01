import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' }
});

export const getProviders = () => api.get('/providers');
export const updateProvider = (id, data) => api.put(`/providers/${id}`, data);
export const createRequest = (data) => api.post('/requests', data);
export const getRequest = (id) => api.get(`/requests/${id}`);
export const getRequests = (params) => api.get('/requests', { params });
export const getConsumerRequests = (consumerId) => api.get(`/consumers/${consumerId}/requests`);
export const getOffersForRequest = (requestId) => api.get(`/requests/${requestId}/offers`);
export const submitOffer = (data) => api.post('/offers', data);
export const acceptOffer = (offerId, data) => api.put(`/offers/${offerId}/accept`, data);
export const getBooking = (id) => api.get(`/bookings/${id}`);
export const getProviderOffers = (providerId) => api.get('/offers', { params: { provider_id: providerId } });
export const markLeadViewed = (requestId, providerId) => api.put(`/requests/${requestId}/view`, null, { params: { provider_id: providerId } });
export const sendChatMessage = (data) => api.post('/chat/', data);
export const getServiceCatalog = () => api.get('/services/catalog/full');
export const getCategoryDetails = (id) => api.get(`/services/catalog/${id}`);
export const startEnrollment = () => api.post('/enrollment/start');
export const getEnrollment = (id) => api.get(`/enrollment/${id}`);
export const updateEnrollment = (id, data) => api.patch(`/enrollment/${id}`, data);
export const submitEnrollment = (id) => api.post(`/enrollment/${id}/submit`);

// Sprint 10
export const cancelRequest = (id) => api.post(`/requests/${id}/cancel`);
export const getProviderProfile = (id) => api.get(`/providers/${id}/profile`);
export const updateProviderProfile = (id, data) => api.patch(`/providers/${id}/profile`, data);
export const getProviderPortfolio = (id) => api.get(`/providers/${id}/portfolio`);
export const addPortfolioPhoto = (providerId, data) => api.post(`/providers/${providerId}/portfolio`, data);
export const deletePortfolioPhoto = (providerId, photoId) => api.delete(`/providers/${providerId}/portfolio/${photoId}`);
export const addProviderService = (providerId, data) => api.post(`/providers/${providerId}/services`, data);
export const updateProviderService = (providerId, serviceId, data) => api.patch(`/providers/${providerId}/services/${serviceId}`, data);
export const deleteProviderService = (providerId, serviceId) => api.delete(`/providers/${providerId}/services/${serviceId}`);

export default api;
