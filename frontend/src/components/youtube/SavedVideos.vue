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
            <i class="bi bi-play-circle"></i> {{ $t('youtube.watch') }}
          </a>
          <button @click="confirmDelete(savedVideo)" class="action-btn delete-btn-global">
            <i class="bi bi-trash"></i> {{ $t('youtube.remove') }}
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
          <button @click="deleteVideo" class="action-btn delete-btn-global">{{ $t('youtube.remove') }}</button>
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

/* 전역 에러 메시지 */
.error-message-global {
  background-color: var(--background-error, #fee2e2);
  color: var(--text-error, #b91c1c);
  padding: var(--alert-padding-y, 1rem) var(--alert-padding-x, 1.5rem);
  border-radius: var(--alert-border-radius, 8px);
  margin-bottom: var(--spacing-lg, 1.5rem);
  border: 1px solid var(--border-error, #fecaca);
  text-align: center;
}

/* 전역 로딩 */
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
  background-color: var(--background-secondary-accent, var(--background-secondary));
  border-radius: var(--card-border-radius-lg, 16px);
  text-align: center;
  color: var(--text-secondary);
  border: 1px dashed var(--border-color-light);
}

.empty-state-icon {
  font-size: 4rem;
  color: var(--text-placeholder, var(--text-secondary-light));
  margin-bottom: var(--spacing-lg, 1.5rem);
}

.empty-state-text {
  font-size: var(--font-size-lg, 1.2rem);
  margin-bottom: var(--spacing-xl, 2rem);
  color: var(--text-primary);
}

/* 비디오 그리드 */
.video-grid-global {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-xl, 2rem);
}

/* 비디오 카드 - ProductCard.vue 스타일 참조하여 대폭 수정 */
.video-card-global {
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--border-radius-lg); /* ProductCard와 동일한 변수 사용 가정 */
  padding: 1.5rem; /* ProductCard와 동일 */
  transition: all var(--transition-speed);
  display: flex;
  flex-direction: column;
  height: 100%;
  box-shadow: var(--card-shadow-sm); /* ProductCard와 동일 */
}

.video-card-global:hover {
  transform: translateY(-4px); /* ProductCard와 동일 */
  box-shadow: var(--card-shadow); /* ProductCard와 동일 */
  /* border-color: rgba(var(--accent-color-rgb), 0.5); ProductCard와 동일하게 하려면 이 부분도 추가 */
}

.video-thumbnail-global img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-bottom: 1px solid var(--card-border); /* ProductCard에는 없으나, 썸네일 구분을 위해 유지 또는 조정 */
  border-radius: var(--border-radius-md); /* 썸네일에 약간의 둥근 모서리 추가 */
  margin-bottom: 1rem; /* 컨텐츠와의 간격 */
}

.video-content-global {
  /* padding: var(--card-padding-lg, 1.5rem); 카드 전체 패딩으로 이동 */
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.video-title-global {
  font-size: 1.25rem; /* ProductCard 이름과 유사하게 */
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-heading);
  margin: 0 0 var(--spacing-sm, 0.5rem) 0; /* 간격 조정 */
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.25rem * 1.4 * 2); 
}

.video-channel-global,
.video-date-global {
  font-size: 0.9rem; /* ProductCard 은행명과 유사하게 */
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs, 0.25rem); /* 간격 조정 */
  line-height: 1.5;
}
.video-date-global {
  margin-bottom: var(--spacing-md, 1rem); /* 메모 입력창과의 간격 */
}

.notes-input-area {
  margin-top: auto; /* 제목, 채널, 날짜 밑으로 밀기 & 버튼 위로 */
  margin-bottom: var(--spacing-md, 1rem); /* 버튼과의 간격 */
  flex-grow: 0; /* ProductCard 처럼 내용만큼만 차지하도록 변경, 이전엔 flex-grow:1 이었음 */
}

.notes-textarea-custom {
  min-height: 80px;
  resize: vertical;
  font-size: var(--font-size-sm, 0.9rem);
  width: 100%;
  padding: var(--input-padding-y) var(--input-padding-x);
  border: 1px solid var(--input-border);
  border-radius: var(--input-border-radius);
  background-color: var(--input-bg);
  color: var(--input-text);
}
.notes-textarea-custom::placeholder {
  color: var(--input-placeholder);
}


.video-actions-global {
  /* padding: var(--spacing-md, 1rem) var(--card-padding-lg, 1.5rem); 카드 전체 패딩으로 대체 */
  /* border-top: 1px solid var(--card-border-light, var(--border-color-light)); ProductCard 스타일 따름 */
  margin-top: auto; /* Push actions to the bottom */
  padding-top: 1rem; /* Space above buttons, ProductCard와 유사하게 */
  border-top: 1px solid var(--border-color); /* ProductCard와 유사하게 */
  display: flex;
  align-items: center; /* 버튼들을 세로 중앙 정렬 */
  gap: var(--spacing-md, 1rem);
  /* background-color: var(--background-secondary-ultralight, rgba(0,0,0,0.02)); ProductCard에는 없는 부분이므로 제거 또는 조정 */
}

/* 버튼 스타일은 전역 스타일(action-btn 등)을 따르도록 variables.css에 정의된 것을 사용합니다. */
/* SavedVideos.vue의 .watch-btn-global, .delete-btn-global은 이미 전역 클래스명을 따르고 있을 수 있습니다. */
/* ProductCard의 .details-btn 스타일을 참고하여, 전역 버튼 스타일이 없다면 여기에 유사하게 정의합니다. */

/* .action-btn i { 이미 전역일 수 있음
  margin-right: var(--spacing-xs, 0.4rem);
} */


/* 모달 스타일 (기존 유지) */
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
  /* 기본적으로 secondary-btn-global 스타일을 따르도록 variables.css 또는 App.vue에서 정의 권장 */
}

.delete-btn-global {
  /* 제거 버튼 고유 스타일 (필요시) */
  /* 기본적으로 delete-btn-global 스타일을 따르도록 variables.css 또는 App.vue에서 정의 권장 */
  margin-left: auto; /* "제거하기" 버튼을 오른쪽으로 정렬 */
}

/* Dark mode specific styles for this component */
/* 카드 자체의 다크모드는 variables.css의 --card-bg, --card-border 등이 처리 */

.dark .notes-textarea-custom,
.dark ::v-deep .notes-textarea-custom {
  background-color: var(--input-bg);
  color: var(--input-text);
  border-color: var(--input-border);
}

.dark .notes-textarea-custom::placeholder,
.dark ::v-deep .notes-textarea-custom::placeholder {
  color: var(--input-placeholder);
}

/* 버튼 다크모드는 variables.css의 버튼 변수들이 처리해야 함 */
/* SavedVideos.vue의 이전 다크모드 버튼 스타일은 variables.css 의존으로 변경 */
/*
.dark .watch-btn-global,
.dark ::v-deep .watch-btn-global {
  background-color: var(--button-secondary-bg);
  color: var(--button-secondary-text);
  border: 1px solid var(--button-secondary-border);
}

.dark .watch-btn-global:hover,
.dark ::v-deep .watch-btn-global:hover {
  background-color: var(--button-secondary-hover-bg);
  color: var(--text-primary); 
  border-color: var(--button-secondary-hover-bg);
}

.dark .delete-btn-global,
.dark ::v-deep .delete-btn-global {
  background-color: var(--button-danger-bg); 
  color: var(--button-danger-text);
  border: 1px solid var(--button-danger-bg);
}

.dark .delete-btn-global:hover,
.dark ::v-deep .delete-btn-global:hover {
  background-color: var(--button-danger-hover-bg);
  border-color: var(--button-danger-hover-bg);
}
*/

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
  /* 카드 내부 폰트 등 반응형 조정 필요시 추가 */
}

@media (max-width: 480px) {
  .video-grid-global {
    grid-template-columns: 1fr;
  }
   .modal-container-global {
    margin: 1rem;
    padding: 1.5rem;
  }
  .video-card-global {
    padding: 1rem; /* 모바일에서 카드 패딩 약간 줄임 */
  }
  .video-title-global {
    font-size: 1.1rem; /* 모바일에서 제목 약간 줄임 */
  }
}
</style>
