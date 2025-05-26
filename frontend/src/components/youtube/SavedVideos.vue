<!-- Saved Videos Component -->
<template>
  <div class="saved-videos-container">
    <h2 class="page-title">{{ $t('common.savedVideos') }}</h2>

    <div v-if="error" class="error-message-global">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-container-global">
      <div class="loading-spinner-global"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <div v-else-if="savedVideos.length === 0" class="empty-state-container">
      <i class="bi bi-camera-video-off empty-state-icon"></i>
      <p class="empty-state-text">{{ $t('youtube.noSavedVideos') }}</p>
      <router-link to="/youtube/search" class="action-btn primary-btn">
        <i class="bi bi-search"></i> {{ $t('youtube.searchVideosLink') }}
      </router-link>
    </div>

    <div v-else class="video-grid-global">
      <div v-for="savedVideo in savedVideos" :key="savedVideo.id" class="video-card-global">
        <div class="video-thumbnail-global">
          <img :src="savedVideo.video.thumbnail_url" :alt="savedVideo.video.title" />
        </div>
        <div class="video-content-global">
          <h3 class="video-title-global" :title="savedVideo.video.title">
            {{ savedVideo.video.title }}
          </h3>
          <p class="video-channel-global">{{ savedVideo.video.channel_title }}</p>
          <p class="video-date-global">{{ $t('youtube.savedAt') }}: {{ formatDate(savedVideo.saved_at) }}</p>
          <div class="notes-input-area">
            <textarea
              class="form-control-global notes-textarea-custom"
              :id="'notes-' + savedVideo.id"
              v-model="savedVideo.notes"
              @blur="updateNotes(savedVideo)"
              :placeholder="$t('youtube.addNotesPlaceholder')"
            ></textarea>
          </div>
        </div>
        <div class="video-actions-global">
          <a
            :href="'https://www.youtube.com/watch?v=' + savedVideo.video.youtube_id"
            target="_blank"
            class="action-btn watch-btn-global"
          >
            <i class="bi bi-play-circle"></i> {{ $t('common.watch') }}
          </a>
          <button @click="confirmDelete(savedVideo)" class="action-btn delete-btn-global">
            <i class="bi bi-trash"></i> {{ $t('common.remove') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay-global" v-if="showDeleteModal" @click="cancelDelete">
      <div class="modal-container-global" @click.stop>
        <div class="modal-header-global">
          <h3>{{ $t('youtube.confirmRemoveTitle') }}</h3>
          <button class="close-button-global" @click="cancelDelete">&times;</button>
        </div>
        <div class="modal-body-global">
          <p>{{ $t('youtube.confirmRemoveMessage') }}</p>
        </div>
        <div class="modal-footer-global">
          <button class="action-btn secondary-btn-global" @click="cancelDelete">{{ $t('common.cancel') }}</button>
          <button @click="deleteVideo" class="action-btn delete-btn-global">{{ $t('common.remove') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toast-notification'
import youtubeApi from '@/services/youtube'
import { useI18n } from 'vue-i18n'

export default {
  name: 'SavedVideos',
  setup() {
    const { t } = useI18n()
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
        error.value = t('youtube.errorLoad')
      } finally {
        isLoading.value = false
      }
    }

    const updateNotes = async (savedVideo) => {
      try {
        await youtubeApi.updateSavedVideo(savedVideo.id, { notes: savedVideo.notes })
        $toast.success(t('youtube.notesUpdated'))
      } catch (err) {
        console.error('Error updating notes:', err)
        $toast.error(t('youtube.errorUpdateNotes'))
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
        $toast.success(t('youtube.videoRemoved'))
      } catch (err) {
        console.error('Error deleting video:', err)
        $toast.error(t('youtube.errorRemoveVideo'))
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
      t
    }
  },
}
</script>

<style scoped>
/* 기존 스타일은 모두 제거하고 전역 스타일 및 페이지 특화 스타일을 새로 작성합니다. */

/* 페이지 컨테이너 */
.saved-videos-container {
  padding: var(--page-padding, 2rem 1.5rem);
  max-width: var(--container-max-width, 1200px);
  margin: 0 auto;
  font-family: var(--font-body);
}

/* 페이지 제목 */
.page-title {
  font-size: var(--font-size-xxxl, 2.5rem);
  color: var(--text-primary);
  margin-bottom: var(--spacing-xl, 2rem);
  font-family: var(--font-heading);
  font-weight: 700;
  text-align: center;
}

/* 전역 에러 메시지 (기존 스타일이 이미 전역적일 수 있으므로 확인 필요) */
.error-message-global {
  background-color: var(--background-error, #fee2e2);
  color: var(--text-error, #b91c1c);
  padding: var(--alert-padding-y, 1rem) var(--alert-padding-x, 1.5rem);
  border-radius: var(--alert-border-radius, 8px);
  margin-bottom: var(--spacing-lg, 1.5rem);
  border: 1px solid var(--border-error, #fecaca);
  text-align: center;
}

/* 전역 로딩 (기존 스타일이 이미 전역적일 수 있으므로 확인 필요) */
.loading-container-global {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl, 3rem) 0;
  color: var(--text-secondary);
}
.loading-spinner-global {
  width: 48px;
  height: 48px;
  border: 5px solid var(--border-color-light, #e0e0e0);
  border-top: 5px solid var(--accent-color, #4f46e5);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md, 1rem);
}

/* 빈 상태 컨테이너 */
.empty-state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl, 4rem) var(--spacing-lg, 2rem);
  background-color: var(--background-secondary-accent, var(--background-secondary)); /* 약간 다른 배경 */
  border-radius: var(--card-border-radius-lg, 16px);
  text-align: center;
  color: var(--text-secondary);
  border: 1px dashed var(--border-color-light);
}

.empty-state-icon {
  font-size: 4rem; /* 아이콘 크기 키움 */
  color: var(--text-placeholder, var(--text-secondary-light));
  margin-bottom: var(--spacing-lg, 1.5rem);
}

.empty-state-text {
  font-size: var(--font-size-lg, 1.2rem);
  margin-bottom: var(--spacing-xl, 2rem);
  color: var(--text-primary);
}

/* 비디오 그리드 (YoutubeSearch.vue 와 유사하게) */
.video-grid-global {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); /* 카드 최소 너비 조정 */
  gap: var(--spacing-xl, 2rem); /* 카드 간 간격 조정 */
}

/* 비디오 카드 (YoutubeSearch.vue 와 유사하게) */
.video-card-global {
  background: var(--card-bg, white);
  border: 1px solid var(--card-border, #e0e0e0);
  border-radius: var(--card-border-radius-lg, 16px); /* 더 둥근 모서리 */
  box-shadow: var(--shadow-lg, 0 8px 16px rgba(0,0,0,0.1)); /* 좀 더 부드러운 그림자 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-fast, 0.2s), box-shadow var(--transition-fast, 0.2s);
}

.video-card-global:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-xl, 0 12px 24px rgba(0,0,0,0.15));
}

.video-thumbnail-global img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-bottom: 1px solid var(--card-border);
}

.video-content-global {
  padding: var(--card-padding-lg, 1.5rem);
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.video-title-global {
  font-size: var(--font-size-xl, 1.3rem);
  font-weight: 700;
  color: var(--text-heading, var(--text-primary));
  font-family: var(--font-heading);
  margin: 0 0 var(--spacing-md, 0.75rem) 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.3rem * 1.4 * 2); /* 2줄 높이 확보 */
}

.video-channel-global,
.video-date-global {
  font-size: var(--font-size-sm, 0.9rem);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm, 0.5rem);
  line-height: 1.5;
}

.notes-input-area {
  margin-top: var(--spacing-md, 1rem);
  flex-grow: 1; /* 남은 공간 채우도록 */
  display: flex; /* 내부 textarea 높이 100%를 위해 */
}

.notes-textarea-custom {
  /* .form-control-global 스타일 상속 + 추가 */
  min-height: 80px; /* 최소 높이 */
  resize: vertical; /* 수직 리사이즈만 허용 */
  font-size: var(--font-size-sm, 0.9rem);
  width: 100%;
}

.video-actions-global {
  padding: var(--spacing-md, 1rem) var(--card-padding-lg, 1.5rem);
  border-top: 1px solid var(--card-border-light, var(--border-color-light));
  display: flex;
  gap: var(--spacing-md, 1rem);
  background-color: var(--background-secondary-ultralight, rgba(0,0,0,0.02)); /* 액션 영역 배경 구분 */
}

/* 모달 스타일 (App.vue 또는 전역 모달 스타일 참조) */
.modal-overlay-global {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--modal-overlay-bg, rgba(0, 0, 0, 0.6));
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-modal-overlay, 1000);
}

.modal-container-global {
  background-color: var(--modal-bg, var(--card-bg));
  padding: var(--modal-padding, 2rem);
  border-radius: var(--modal-border-radius, 12px);
  box-shadow: var(--modal-shadow, 0 5px 15px rgba(0,0,0,0.3));
  width: 100%;
  max-width: var(--modal-max-width, 500px);
  animation: modal-fade-in var(--transition-normal) ease-out;
}

.modal-header-global {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-md, 1rem);
  margin-bottom: var(--spacing-lg, 1.5rem);
  border-bottom: 1px solid var(--border-color);
}

.modal-header-global h3 {
  margin: 0;
  font-size: var(--font-size-xl, 1.5rem);
  color: var(--text-heading, var(--text-primary));
  font-family: var(--font-heading);
}

.close-button-global {
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.close-button-global:hover {
  color: var(--text-primary);
}

.modal-body-global p {
  font-size: var(--font-size-md, 1rem);
  color: var(--text-primary);
  line-height: 1.6;
  margin-bottom: 0; /* 푸터와의 간격은 푸터에서 처리 */
}

.modal-footer-global {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md, 1rem);
  padding-top: var(--spacing-lg, 1.5rem);
  margin-top: var(--spacing-lg, 1.5rem);
  border-top: 1px solid var(--border-color-light);
}

/* 전역 버튼 스타일 (.action-btn 등은 variables.css 또는 App.vue에 정의되어 있어야 함) */
/* .action-btn, .primary-btn, .secondary-btn, .delete-btn-global, .watch-btn-global 등은 */
/* 이미 전역적으로 스타일이 정의되어 있다고 가정하고, 필요한 경우 여기서 오버라이드 또는 추가 */

.action-btn i {
  margin-right: var(--spacing-xs, 0.4rem);
}

/* 특정 버튼에 대한 추가 스타일 (필요시) */
.watch-btn-global {
  /* 시청 버튼 고유 스타일 (필요시) */
}

.delete-btn-global {
  /* 제거 버튼 고유 스타일 (필요시) */
  /* 예: background-color: var(--button-danger-bg); color: var(--button-danger-text); */
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 반응형 스타일 (기존 스타일 참조 및 전역 기준 적용) */
@media (max-width: 768px) {
  .video-grid-global {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  .page-title {
    font-size: var(--font-size-xxl, 2rem);
  }
}

@media (max-width: 480px) {
  .video-grid-global {
    grid-template-columns: 1fr;
  }
   .modal-container-global {
    margin: 1rem;
    padding: 1.5rem;
  }
}
</style>
