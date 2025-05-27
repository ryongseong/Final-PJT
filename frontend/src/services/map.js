import axios from 'axios'

// This file can be used to implement backend API calls for map-related features
// For example, storing and retrieving locations from your backend

const mapService = {
  // Get all locations
  async getLocations() {
    try {
      const response = await axios.get('/api/locations/')
      return response.data
    } catch (error) {
      console.error('Error fetching locations:', error)
      throw error
    }
  },

  // Get a specific location by ID
  async getLocation(locationId) {
    try {
      const response = await axios.get(`/api/locations/${locationId}/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching location ${locationId}:`, error)
      throw error
    }
  },

  // Save a new location
  async saveLocation(locationData) {
    try {
      const response = await axios.post('/api/locations/', locationData)
      return response.data
    } catch (error) {
      console.error('Error saving location:', error)
      throw error
    }
  },

  // Update an existing location
  async updateLocation(locationId, locationData) {
    try {
      const response = await axios.put(`/api/locations/${locationId}/`, locationData)
      return response.data
    } catch (error) {
      console.error(`Error updating location ${locationId}:`, error)
      throw error
    }
  },

  // Delete a location
  async deleteLocation(locationId) {
    try {
      const response = await axios.delete(`/api/locations/${locationId}/`)
      return response.data
    } catch (error) {
      console.error(`Error deleting location ${locationId}:`, error)
      throw error
    }
  },

  // Search locations by query string (city, district, etc.)
  async searchLocations(query) {
    try {
      const response = await axios.get(`/api/locations/search/?q=${encodeURIComponent(query)}`)
      return response.data
    } catch (error) {
      console.error('Error searching locations:', error)
      throw error
    }
  },
}

export default mapService
