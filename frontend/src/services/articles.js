// API service for articles related calls
import axios from 'axios'

const API_URL = 'http://localhost:8000/articles/'

// Create axios instance with auth header
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor to add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

export default {
  // Get all articles
  getArticles() {
    return apiClient.get('').then((response) => response.data)
  },

  // Get single article
  getArticle(id) {
    return apiClient.get(`${id}/`).then((response) => response.data)
  },

  // Create new article
  createArticle(article) {
    return apiClient.post('', article).then((response) => response.data)
  },

  // Update article
  updateArticle(id, article) {
    return apiClient.put(`${id}/`, article).then((response) => response.data)
  },

  // Delete article
  deleteArticle(id) {
    return apiClient.delete(`${id}/`).then((response) => response.data)
  },

  // Add comment to article
  addComment(articleId, comment) {
    return apiClient
      .post(`${articleId}/comments/`, { content: comment })
      .then((response) => response.data)
  },

  // Update comment
  updateComment(commentId, comment) {
    return apiClient
      .put(`comments/${commentId}/`, { content: comment })
      .then((response) => response.data)
  },

  // Delete comment
  deleteComment(commentId) {
    return apiClient.delete(`comments/${commentId}/`).then((response) => response.data)
  },

  // Like or unlike an article
  toggleLike(articleId) {
    return apiClient.post(`${articleId}/like/`).then((response) => response.data)
  },

  // Get articles sorted by likes
  getArticlesSortedByLikes() {
    return apiClient.get('sort_by_likes/').then((response) => response.data)
  },
}
