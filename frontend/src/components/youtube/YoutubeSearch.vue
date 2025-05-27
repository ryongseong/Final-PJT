<!-- YouTube Search Component -->
<template>
  <div class="youtube-search-container">
    <h2>주식 관련 영상 검색</h2>
    <div class="search-box-wrapper">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          @keyup.enter="searchVideos"
          class="search-input-field"
          placeholder="주식 관련 영상을 검색해보세요!!"
        />
        <i class="search-icon">🔍</i>
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
/* 유튜브 검색 컨테이너 및 기본 요소 - 전역 스타일 변수 적용 */
.youtube-search-container {
  padding: var(--page-padding, 2rem 1.5rem);
  text-align: center;
  background-color: var(--background-secondary, #f4f4f4);
  border-radius: var(--card-border-radius, 12px);
  box-shadow: var(--shadow-lg, 0 8px 16px rgba(0, 0, 0, 0.1));
  max-width: 1200px;
  margin: 2rem auto;
  font-family: var(--font-body, 'Noto Sans KR', sans-serif);
}

h2 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-xl, 2rem);
  font-size: var(--font-size-xxxl, 2.5rem);
  font-family: var(--font-heading, 'Playfair Display', serif);
  font-weight: 700;
}

.search-box-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: var(--spacing-xl, 2rem);
  padding: var(--spacing-md, 1rem);
  background-color: var(--card-bg);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.search-box {
  display: flex;
  align-items: center;
  background-color: var(--background-primary);
  border-radius: var(--input-border-radius, 8px);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  flex-grow: 1;
  border: 1px solid var(--border-color);
}

.search-input-field {
  border: none;
  outline: none;
  background-color: transparent;
  flex-grow: 1;
  padding: var(--spacing-sm, 0.5rem);
  font-size: var(--font-size-md, 1rem);
  color: var(--text-primary);
  font-family: var(--font-body);
}

.search-input-field:focus {
  /* 포커스 스타일은 ArticlesView에 없었으므로, 필요시 추가 또는 전역 스타일 따름 */
  /* box-shadow: 0 0 0 3px var(--accent-color-opacity-20, rgba(0,123,255,0.2)); */ /* 기존 스타일 유지 시 */
}

.search-icon {
  color: var(--text-secondary);
  font-size: 1.2rem;
  /* 기존 search-button 대신 사용되므로, 필요시 cursor: pointer 추가 가능 */
}

/* 메시지 및 로딩 스타일 - 전역 변수 적용 */
.error-message, .info-message {
  padding: var(--alert-padding-y, 1rem) var(--alert-padding-x, 1.5rem);
  border-radius: var(--alert-border-radius, 8px);
  margin-bottom: var(--spacing-lg, 1.5rem);
  font-size: var(--font-size-md, 1rem);
}

.error-message {
  background-color: var(--background-error, #fee2e2);
  color: var(--text-error, #b91c1c);
  border: 1px solid var(--border-error, #fecaca);
}

.info-message {
  background-color: var(--background-info, #e0f2fe);
  color: var(--text-info, #075985);
  border: 1px solid var(--border-info, #bae6fd);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl, 3rem) 0;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 48px; /* 크기 증가 */
  height: 48px;
  border: 5px solid var(--border-color-light, #e0e0e0);
  border-top: 5px solid var(--accent-color, #4f46e5);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md, 1rem);
}

/* 비디오 카드 그리드 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* 반응형 그리드 */
  gap: var(--spacing-lg, 1.5rem);
  margin-top: var(--spacing-xl, 2rem);
}

/* 비디오 카드 스타일 개선 - HomeView 카드 스타일 참조 */
.video-card {
  background: var(--card-bg, white);
  border: 1px solid var(--card-border, #e0e0e0);
  border-radius: var(--card-border-radius, 12px);
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0,0,0,0.1));
  overflow: hidden; /* 썸네일 경계 처리 */
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg, 0 8px 12px rgba(0,0,0,0.15));
}

.video-thumbnail {
  width: 100%;
  aspect-ratio: 16 / 9; /* 16:9 비율 유지 */
  background-color: var(--background-light-gray, #f0f0f0); /* 로딩 중 배경색 */
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 이미지가 영역을 꽉 채우도록 */
}

.video-content {
  padding: var(--card-padding-lg, 1.5rem);
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.video-title {
  font-size: var(--font-size-xl, 1.35rem);
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-heading, 'Noto Sans KR', sans-serif);
  margin: 0 0 var(--spacing-md, 0.75rem) 0;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.35rem * 1.45 * 2);
}

.video-channel, .video-date {
  font-size: var(--font-size-md, 0.95rem);
  color: var(--text-secondary);
  font-family: var(--font-body, 'Noto Sans KR', sans-serif);
  margin-bottom: var(--spacing-sm, 0.5rem);
  line-height: 1.5;
}

.video-description {
  font-size: var(--font-size-md, 0.95rem);
  color: var(--text-secondary);
  font-family: var(--font-body, 'Noto Sans KR', sans-serif);
  line-height: 1.6;
  margin-top: var(--spacing-sm, 0.5rem);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

.video-actions {
  padding: var(--spacing-md, 0.75rem) var(--card-padding, 1.25rem);
  border-top: 1px solid var(--border-color-light, #eee);
  display: flex;
  gap: var(--spacing-sm, 0.5rem);
  margin-top: auto; /* 버튼들을 카드 하단에 고정 */
}

/* 버튼 스타일 - 전역 .action-btn 스타일 활용 */
.action-button {
  flex: 1;
  padding: var(--button-padding-y, 0.75rem) var(--button-padding-x, 1.25rem);
  border-radius: var(--button-border-radius, 8px);
  font-weight: 600;
  font-size: var(--font-size-md, 1rem);
  font-family: var(--font-body, 'Noto Sans KR', sans-serif);
  text-align: center;
  cursor: pointer;
  transition: background-color var(--transition-speed), border-color var(--transition-speed), color var(--transition-speed);
  text-decoration: none;
}

.watch-button {
  background-color: var(--button-bg, #007bff);
  color: var(--button-text, white);
  border: 1px solid var(--button-bg, #007bff);
}

.watch-button:hover {
  background-color: var(--button-hover, #0056b3);
  border-color: var(--button-hover, #0056b3);
}

.save-button {
  background-color: var(--button-bg-secondary, transparent);
  color: var(--button-text-secondary, var(--accent-color));
  border: 1px solid var(--button-border-color-secondary, var(--accent-color));
}

.save-button:hover {
  background-color: var(--button-hover-bg-secondary, var(--accent-color-opacity-10));
  color: var(--accent-hover, var(--accent-color-dark));
  border-color: var(--accent-hover, var(--accent-color-dark));
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 반응형 조정 */
@media (max-width: 768px) {
  .youtube-search-container {
    margin: 1rem auto;
    padding: 1.5rem;
  }
  h2 {
    font-size: var(--font-size-xl, 1.8rem);
  }
  .search-box-wrapper {
    flex-direction: column;
    gap: var(--spacing-md, 1rem);
  }
  .search-input-field {
    width: 100%;
    border-radius: var(--input-border-radius, 8px); /* 모바일에서 전체 둥글게 */
  }
  .search-input-field {
    border-right: 1px solid var(--border-color, #ccc); /* 모바일에서 오른쪽 테두리 복원 */
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-md, 1rem);
  }
  .video-title {
    font-size: var(--font-size-md, 1.1rem);
     min-height: calc(1.1rem * 1.4 * 2);
  }
}

@media (max-width: 480px) {
  .video-grid {
    grid-template-columns: 1fr; /* 매우 작은 화면에서는 한 줄로 */
  }
  .video-card {
    margin-bottom: var(--spacing-lg, 1rem);
  }
   .video-title {
    font-size: var(--font-size-md, 1rem);
     min-height: calc(1rem * 1.4 * 2);
  }
  .video-actions {
    flex-direction: column;
  }
}
</style>
