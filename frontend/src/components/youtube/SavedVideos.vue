<!-- Saved Videos Component -->
<template>
  <div class="saved-videos">
    <h2>나중에 볼 영상</h2>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>저장된 영상을 불러오는 중...</p>
    </div>

    <div v-else-if="savedVideos.length === 0" class="info-message">
      <p>저장된 주식 관련 영상이 없습니다.</p>
      <router-link to="/youtube/search" class="action-button primary-button">
        영상을 검색해보세요.
      </router-link>
    </div>

    <div v-else class="video-grid">
      <div v-for="savedVideo in savedVideos" :key="savedVideo.id" class="video-card">
        <div class="video-thumbnail">
          <img :src="savedVideo.video.thumbnail_url" :alt="savedVideo.video.title" />
        </div>
        <div class="video-content">
          <h3 class="video-title" :title="savedVideo.video.title">
            {{ savedVideo.video.title }}
          </h3>
          <p class="video-channel">{{ savedVideo.video.channel_title }}</p>
          <p class="video-date">저장된 일시: {{ formatDate(savedVideo.saved_at) }}</p>
          <div class="notes-container">
            <textarea
              class="notes-textarea"
              :id="'notes-' + savedVideo.id"
              v-model="savedVideo.notes"
              @blur="updateNotes(savedVideo)"
              placeholder="메모를 추가하세요..."
            ></textarea>
          </div>
        </div>
        <div class="video-actions">
          <a
            :href="'https://www.youtube.com/watch?v=' + savedVideo.video.youtube_id"
            target="_blank"
            class="action-button watch-button"
          >
            보기
          </a>
          <button @click="confirmDelete(savedVideo)" class="action-button delete-button">
            제거
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay" v-if="showDeleteModal" @click="cancelDelete">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3>제거 확인</h3>
          <button class="close-button" @click="cancelDelete">×</button>
        </div>
        <div class="modal-body">
          <p>이 영상을 저장 목록에서 제거하시겠습니까?</p>
        </div>
        <div class="modal-footer">
          <button class="action-button secondary-button" @click="cancelDelete">취소</button>
          <button @click="deleteVideo" class="action-button delete-button">제거</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toast-notification'
import youtubeApi from '@/services/youtube'

export default {
  name: 'SavedVideos',
  setup() {
    const savedVideos = ref([])
    const isLoading = ref(true)
    const error = ref('')
    const selectedVideo = ref(null)
    const showDeleteModal = ref(false)
    const $toast = useToast()

    const fetchSavedVideos = async () => {
      isLoading.value = true
      error.value = ''

      try {
        const response = await youtubeApi.getSavedVideos()
        savedVideos.value = response.data
      } catch (err) {
        console.error('Error fetching saved videos:', err)
        error.value = 'Failed to load your saved videos. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    const updateNotes = async (savedVideo) => {
      try {
        await youtubeApi.updateSavedVideo(savedVideo.id, { notes: savedVideo.notes })
        $toast.success('Notes updated successfully')
      } catch (err) {
        console.error('Error updating notes:', err)
        $toast.error('Failed to update notes. Please try again.')
      }
    }

    const confirmDelete = (video) => {
      selectedVideo.value = video
      showDeleteModal.value = true
    }

    const cancelDelete = () => {
      showDeleteModal.value = false
    }

    const deleteVideo = async () => {
      if (!selectedVideo.value) return

      try {
        await youtubeApi.deleteSavedVideo(selectedVideo.value.id)
        savedVideos.value = savedVideos.value.filter((v) => v.id !== selectedVideo.value.id)
        $toast.success('Video removed from your saved list')
      } catch (err) {
        console.error('Error deleting video:', err)
        $toast.error('Failed to remove video. Please try again.')
      } finally {
        selectedVideo.value = null
        showDeleteModal.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    onMounted(() => {
      fetchSavedVideos()
    })

    return {
      savedVideos,
      isLoading,
      error,
      showDeleteModal,
      updateNotes,
      confirmDelete,
      cancelDelete,
      deleteVideo,
      formatDate,
    }
  },
}
</script>

<style scoped>
.saved-videos {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
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
  margin-bottom: 12px;
}

.notes-container {
  margin-bottom: 16px;
}

.notes-textarea {
  width: 100%;
  min-height: 80px;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
}

.notes-textarea:focus {
  border-color: #4f46e5;
  outline: none;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
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
  border: 1px solid transparent;
}

.primary-button {
  background-color: #4f46e5;
  color: white;
}

.primary-button:hover {
  background-color: #4338ca;
}

.secondary-button {
  background-color: #f3f4f6;
  color: #4b5563;
  border-color: #d1d5db;
}

.secondary-button:hover {
  background-color: #e5e7eb;
}

.watch-button {
  color: #4f46e5;
  border: 1px solid #4f46e5;
  background-color: transparent;
}

.watch-button:hover {
  background-color: #f5f5ff;
}

.delete-button {
  color: #ef4444;
  border: 1px solid #ef4444;
  background-color: transparent;
}

.delete-button:hover {
  background-color: #fef2f2;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.modal-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #9ca3af;
}

.modal-body {
  padding: 16px;
}

.modal-footer {
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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
