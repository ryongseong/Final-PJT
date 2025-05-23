<!-- YouTube Search Component -->
<template>
  <div class="youtube-search">
    <h2>주식 관련 영상 검색</h2>

    <div class="search-form">
      <div class="search-input-group">
        <input
          v-model="searchQuery"
          @keyup.enter="searchVideos"
          type="text"
          class="search-input"
          placeholder="주식 관련 영상을 검색해보세요!!"
        />
        <button @click="searchVideos" class="search-button" :disabled="isLoading">
          {{ isLoading ? '검색중...' : '검색' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>주식 관련 영상을 검색중입니다...</p>
    </div>

    <div v-else-if="videos.length === 0 && !isLoading && searchPerformed" class="info-message">
      "{{ lastSearchQuery }}"에 대한 영상을 찾을 수 없습니다. 다른 검색어를 시도해보세요.
    </div>

    <div v-else class="video-grid">
      <div v-for="video in videos" :key="video.id" class="video-card">
        <div class="video-thumbnail">
          <img :src="video.thumbnail_url" :alt="video.title" />
        </div>
        <div class="video-content">
          <h3 class="video-title" :title="video.title">
            {{ video.title }}
          </h3>
          <p class="video-channel">{{ video.channel_title }}</p>
          <p class="video-date">
            {{ formatDate(video.published_at) }}
          </p>
          <p class="video-description" :title="video.description">
            {{ video.description || 'No description available' }}
          </p>
        </div>
        <div class="video-actions">
          <a
            :href="'https://www.youtube.com/watch?v=' + video.youtube_id"
            target="_blank"
            class="action-button watch-button"
          >
            시청
          </a>
          <button @click="saveVideo(video)" class="action-button save-button">저장</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toast-notification'
import youtubeApi from '@/services/youtube'

export default {
  name: 'YoutubeSearch',
  setup() {
    const searchQuery = ref('')
    const lastSearchQuery = ref('')
    const videos = ref([])
    const isLoading = ref(false)
    const error = ref('')
    const searchPerformed = ref(false)
    const $toast = useToast()

    const searchVideos = async () => {
      if (!searchQuery.value.trim()) {
        error.value = '검색어를 입력해 주세요.'
        return
      }
      error.value = ''
      isLoading.value = true
      lastSearchQuery.value = searchQuery.value
      searchPerformed.value = true

      try {
        const response = await youtubeApi.searchVideos(searchQuery.value)
        videos.value = response.data
      } catch (err) {
        console.error('Error searching videos:', err)
        error.value = err.response?.data?.error || '영상을 검색하는 중 오류가 발생했습니다.'
      } finally {
        isLoading.value = false
      }
    }

    const saveVideo = async (video) => {
      try {
        const response = await youtubeApi.saveVideo({ video: video.id })
        // If response status is 200, the video was already saved
        if (response.status === 200) {
          $toast.info('이 영상은 이미 저장 목록에 있습니다.')
        } else {
          $toast.success('나중에 볼 영상에 추가')
        }
      } catch (err) {
        console.error('Error saving video:', err)
        if (
          err.response?.status === 400 &&
          err.response?.data?.non_field_errors?.[0]?.includes('unique')
        ) {
          $toast.info('이 영상은 이미 저장 목록에 있습니다.')
        } else {
          $toast.error('영상을 저장하는 중 오류가 발생했습니다.')
        }
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    }

    return {
      searchQuery,
      lastSearchQuery,
      videos,
      isLoading,
      error,
      searchPerformed,
      searchVideos,
      saveVideo,
      formatDate,
    }
  },
}
</script>

<style scoped>
.youtube-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-form {
  max-width: 600px;
  margin: 0 auto 30px;
}

.search-input-group {
  display: flex;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-right: none;
  font-size: 16px;
  outline: none;
}

.search-button {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 0 20px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.search-button:hover {
  background-color: #4338ca;
}

.search-button:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.info-message {
  background-color: #e0f2fe;
  color: #075985;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.video-card {
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.video-card:hover {
  transform: translateY(-5px);
}

.video-thumbnail img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.video-content {
  padding: 16px;
}

.video-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  height: 48px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.video-channel {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.video-date {
  color: #888;
  font-size: 12px;
  margin-bottom: 8px;
}

.video-description {
  font-size: 14px;
  color: #444;
  margin-bottom: 16px;
  height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
}

.video-actions {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid #eee;
}

.action-button {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}

.watch-button {
  color: #4f46e5;
  border: 1px solid #4f46e5;
  background-color: transparent;
}

.watch-button:hover {
  background-color: #f5f5ff;
}

.save-button {
  color: #4b5563;
  border: 1px solid #d1d5db;
  background-color: transparent;
}

.save-button:hover {
  background-color: #f8f9fa;
}

@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 480px) {
  .video-grid {
    grid-template-columns: 1fr;
  }
}
</style>
