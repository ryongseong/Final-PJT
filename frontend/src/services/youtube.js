// YouTube API service

import axios from 'axios'

const baseURL = 'http://localhost:8000'

// Create a function to get the current token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('access_token')
}

const youtubeApi = {
  /**
   * Search for videos on YouTube using the Django backend
   * @param {string} query - Search query term
   * @returns {Promise} - Promise that resolves to array of videos
   */
  searchVideos(query) {
    return axios.get(`${baseURL}/youtube/videos/search/`, {
      params: { q: query },
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },
  /**
   * Get video details by YouTube ID
   * @param {string} youtubeId - YouTube video ID
   * @returns {Promise} - Promise that resolves to video object
   */
  getVideoByYoutubeId(youtubeId) {
    return axios.get(`${baseURL}/youtube/videos/get_by_youtube_id/`, {
      params: { id: youtubeId },
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },

  /**
   * Get related videos for a specific YouTube video
   * @param {string} youtubeId - YouTube video ID
   * @returns {Promise} - Promise that resolves to array of related videos
   */
  getRelatedVideos(youtubeId) {
    return axios.get(`${baseURL}/youtube/videos/related_videos/`, {
      params: { id: youtubeId },
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },

  /**
   * Get all videos saved by the current user
   * @returns {Promise} - Promise that resolves to array of saved videos
   */
  getSavedVideos() {
    return axios.get(`${baseURL}/youtube/saved/my_saved_videos/`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },

  /**
   * Save a video to watch later
   * @param {Object} videoData - Video data
   * @returns {Promise} - Promise that resolves to saved video object
   */
  saveVideo(videoData) {
    return axios.post(`${baseURL}/youtube/saved/`, videoData, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },

  /**
   * Delete a saved video
   * @param {number} id - Saved video ID
   * @returns {Promise} - Promise that resolves when video is deleted
   */
  deleteSavedVideo(id) {
    return axios.delete(`${baseURL}/youtube/saved/${id}/`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },

  /**
   * Update notes on a saved video
   * @param {number} id - Saved video ID
   * @param {Object} data - Data to update (notes)
   * @returns {Promise} - Promise that resolves to updated saved video
   */
  updateSavedVideo(id, data) {
    return axios.patch(`${baseURL}/youtube/saved/${id}/`, data, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
    })
  },
}

export default youtubeApi
