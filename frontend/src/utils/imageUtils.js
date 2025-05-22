// Image handling utility functions
const API_BASE_URL = 'http://localhost:8000'

/**
 * Convert a relative image URL to an absolute URL
 * @param {string} url - The image URL that might be relative
 * @param {boolean} forceCacheBusting - Whether to force cache busting even for non-profile images
 * @returns {string} The absolute URL with cache busting
 */
export function getAbsoluteImageUrl(url, forceCacheBusting = true) {
  if (!url) return null

  // If it's already an absolute URL (starts with http)
  if (url.startsWith('http')) {
    // For social avatars or already absolute URLs, we might still need cache busting
    if (forceCacheBusting) {
      const cacheBuster = `t=${new Date().getTime()}`
      const separator = url.includes('?') ? '&' : '?'
      return `${url}${separator}${cacheBuster}`
    }
    return url
  }

  // If it's a relative URL (starts with /media), make it absolute
  if (url.startsWith('/media')) {
    // Add cache busting
    const cacheBuster = `t=${new Date().getTime()}`
    const separator = url.includes('?') ? '&' : '?'
    return `${API_BASE_URL}${url}${separator}${cacheBuster}`
  }

  // Return the original URL if it doesn't match our patterns
  return url
}

/**
 * Process user data to ensure profile image URLs are absolute
 * @param {Object} userData - User data object that might contain profile_img
 * @returns {Object} User data with fixed profile image URL
 */
export function processUserWithImage(userData) {
  if (!userData) return userData

  const processedUser = { ...userData }

  if (processedUser.profile_img) {
    processedUser.profile_img = getAbsoluteImageUrl(processedUser.profile_img)
    console.log('Processed profile image URL:', processedUser.profile_img)
  } else if (processedUser.social_avatar) {
    // If there's a social avatar but no profile image, ensure it has cache busting too
    processedUser.social_avatar = getAbsoluteImageUrl(processedUser.social_avatar, false)
    console.log('Processed social avatar URL:', processedUser.social_avatar)
  }

  return processedUser
}

/**
 * Generate a fallback image if the original fails to load
 * @param {string} originalUrl - The original image URL that failed
 * @returns {string} A fallback URL to try
 */
export function generateFallbackImageUrl(originalUrl) {
  if (!originalUrl) return null

  // If it's a relative URL with cache busting, try without cache busting
  if (originalUrl.includes('/media') && originalUrl.includes('?')) {
    return originalUrl.split('?')[0]
  }

  // If it's a relative URL without the API base, add it directly
  if (originalUrl.startsWith('/media') && !originalUrl.startsWith('http')) {
    return `http://localhost:8000${originalUrl}`
  }

  return originalUrl
}

export default {
  getAbsoluteImageUrl,
  processUserWithImage,
  generateFallbackImageUrl,
}
