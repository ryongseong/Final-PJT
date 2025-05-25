<!-- src/views/ArticlesView.vue -->
<template>
  <div class="articles-container">
    <div class="articles-header">
      <h2>커뮤니티 게시판</h2>
      <p class="subtitle">금융 정보와 팁을 공유하는 공간입니다</p>

      <!-- Search and filter bar -->
      <div class="search-filter-bar">
        <div class="search-box">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="게시글 검색..."
            @input="filterArticles"
          />
          <i class="search-icon">🔍</i>
        </div>
        <div class="filter-options">
          <button @click="sortArticles('latest')" :class="{ active: currentSort === 'latest' }">
            최신순
          </button>
          <button @click="sortArticles('comments')" :class="{ active: currentSort === 'comments' }">
            댓글순
          </button>
          <button @click="sortArticles('likes')" :class="{ active: currentSort === 'likes' }">
            좋아요순
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p>게시글 로딩 중...</p>
    </div>

    <div v-else class="articles-content">
      <!-- Create Article Button - Float Action Button style -->
      <button @click="navigateToCreate" class="fab-button">
        <span class="plus-icon">+</span>
        <span class="fab-tooltip">새 게시글 작성</span>
      </button>

      <!-- Articles List -->
      <div class="articles-list">
        <div v-if="filteredArticles.length === 0" class="no-articles">
          <img
            src="https://cdn-icons-png.flaticon.com/512/6598/6598519.png"
            alt="No articles"
            class="empty-icon"
          />
          <p>검색 결과가 없습니다</p>
          <button @click="resetSearch" class="reset-search-btn">전체 게시글 보기</button>
        </div>

        <div
          v-for="article in filteredArticles"
          :key="article.id"
          class="article-card"
          @click="navigateToDetail(article.id)"
        >
          <div class="article-header">
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-excerpt">{{ getExcerpt(article.content || '') }}</p>
          </div>

          <div class="article-meta">
            <div class="author-info">
              <div class="avatar-wrapper">
                <img
                  v-if="article.writer.profile_img"
                  :src="article.writer.profile_img"
                  alt="Avatar"
                  class="avatar-small"
                  @error="handleAvatarError"
                />
                <div v-else class="avatar-placeholder">
                  {{ getInitials(article.writer.nickname) }}
                </div>
              </div>
              <span class="author-name">{{ article.writer.nickname }}</span>
            </div>

            <div class="article-stats">
              <span class="stat like-stat" @click.stop="toggleLike(article)">
                <i class="icon" :class="{ liked: article.is_liked }">{{
                  article.is_liked ? '❤️' : '🤍'
                }}</i>
                {{ article.likes_count || 0 }}
              </span>
              <span class="stat">
                <i class="icon">💬</i>
                {{ article.comment_count }}
              </span>
              <span class="date">{{ formatDate(article.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import articlesService from '@/services/articles'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const articles = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const currentSort = ref('latest') // 'latest', 'comments', or 'likes'

const fetchArticles = async () => {
  loading.value = true
  error.value = null

  try {
    if (currentSort.value === 'likes') {
      articles.value = await articlesService.getArticlesSortedByLikes()
    } else {
      const data = await articlesService.getArticles()
      articles.value = data

      // Fetch full article content for excerpts if needed
      // This is optional and depends on your API - only if content isn't included in list view
      if (data.length > 0 && !data[0].content) {
        for (let i = 0; i < data.length; i++) {
          try {
            const fullArticle = await articlesService.getArticle(data[i].id)
            articles.value[i].content = fullArticle.content
          } catch (err) {
            console.error(`Error fetching content for article ${data[i].id}:`, err)
            articles.value[i].content = '' // Default to empty string
          }
        }
      }

      // Apply default sorting
      if (currentSort.value === 'comments') {
        sortArticles('comments', false)
      }
    }
  } catch (err) {
    console.error('Error fetching articles:', err)
    error.value = '게시글을 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

const navigateToDetail = (articleId) => {
  router.push(`/articles/${articleId}`)
}

const navigateToCreate = () => {
  if (!userStore.isLoggedIn) {
    router.push('/login?redirect=/articles/create')
    return
  }
  router.push('/articles/create')
}

// Format date in a more human-readable way
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()

  // Calculate difference in milliseconds
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    // Today: show hours and minutes
    return `오늘 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  } else if (diffDays === 1) {
    return '어제'
  } else if (diffDays < 7) {
    return `${diffDays}일 전`
  } else {
    // Default format for older dates
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }
}

// Get initials for avatar placeholder
const getInitials = (name) => {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

// Get excerpt of article content (first few words)
const getExcerpt = (content) => {
  if (!content) return ''
  const words = content.split(' ')
  const excerpt = words.slice(0, 15).join(' ')
  return words.length > 15 ? `${excerpt}...` : excerpt
}

// Handle avatar loading errors
const handleAvatarError = (e) => {
  // Replace broken image with placeholder
  e.target.style.display = 'none'
  e.target.parentNode.classList.add('show-placeholder')
}

// Filter articles based on search query
const filterArticles = () => {
  // No need to do anything here since we're using a computed property
}

const resetSearch = () => {
  searchQuery.value = ''
}

// Sort articles by latest or most comments
const sortArticles = (sortBy, updateState = true) => {
  if (updateState) {
    currentSort.value = sortBy
    fetchArticles()
    return
  }

  if (sortBy === 'latest') {
    articles.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } else if (sortBy === 'comments') {
    articles.value.sort((a, b) => b.comment_count - a.comment_count)
  } else if (sortBy === 'likes') {
    articles.value.sort((a, b) => b.likes_count - a.likes_count)
  }
}

// Toggle like for an article
const toggleLike = async (article) => {
  if (!userStore.isLoggedIn) {
    router.push('/login?redirect=/articles')
    return
  }

  try {
    const response = await articlesService.toggleLike(article.id)
    // Update the article's like status locally
    if (response.status === 'liked') {
      article.is_liked = true
      article.likes_count = (article.likes_count || 0) + 1
    } else {
      article.is_liked = false
      article.likes_count = Math.max(0, (article.likes_count || 1) - 1)
    }
  } catch (err) {
    console.error('Error toggling like:', err)
  }
}

// Computed property for filtered articles
const filteredArticles = computed(() => {
  if (!searchQuery.value.trim()) {
    return articles.value
  }

  const query = searchQuery.value.toLowerCase()
  return articles.value.filter(
    (article) =>
      article.title.toLowerCase().includes(query) ||
      (article.content && article.content.toLowerCase().includes(query)) ||
      article.writer.nickname.toLowerCase().includes(query),
  )
})

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.articles-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}

.articles-header {
  text-align: center;
  margin-bottom: 40px;
}

h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1e293b;
  background: linear-gradient(45deg, #4f46e5, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #64748b;
  font-size: 1.1rem;
  margin-top: 0;
  margin-bottom: 30px;
}

.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  border-radius: 12px;
  padding: 12px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 12px;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-box input {
  width: 100%;
  padding: 10px 16px 10px 38px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: #94a3b8;
}

.filter-options {
  display: flex;
  gap: 8px;
}

.filter-options button {
  background-color: #f1f5f9;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-options button:hover {
  background-color: #e2e8f0;
}

.filter-options button.active {
  background-color: #4f46e5;
  color: white;
}

.loading-box {
  text-align: center;
  padding: 50px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.spinner {
  border: 4px solid rgba(79, 70, 229, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4f46e5;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.articles-content {
  position: relative;
}

.fab-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #4f46e5;
  color: white;
  border: none;
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    transform 0.3s,
    background-color 0.3s;
  z-index: 100;
}

.fab-button:hover {
  transform: translateY(-5px);
  background-color: #4338ca;
}

.fab-button:active {
  transform: translateY(0);
}

.plus-icon {
  font-size: 2rem;
  font-weight: 300;
}

.fab-tooltip {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #1e293b;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0.3s,
    visibility 0.3s;
}

.fab-button:hover .fab-tooltip {
  opacity: 1;
  visibility: visible;
}

.articles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.article-card {
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

.article-header {
  flex-grow: 1;
  margin-bottom: 16px;
}

.article-title {
  margin: 0 0 10px;
  font-size: 1.25rem;
  color: #1e293b;
  line-height: 1.3;
  font-weight: 600;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-excerpt {
  color: #64748b;
  font-size: 0.95rem;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
  margin-top: auto;
}

.author-info {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f1f5f9;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #4f46e5;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1rem;
  font-weight: 500;
  border: 2px solid #f1f5f9;
}

.author-name {
  font-size: 0.9rem;
  color: #334155;
  font-weight: 500;
}

.article-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #64748b;
}

.icon {
  margin-right: 4px;
  font-size: 1rem;
}

.date {
  font-size: 0.85rem;
  color: #94a3b8;
}

.no-articles {
  grid-column: 1 / -1;
  background-color: white;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
  opacity: 0.7;
}

.no-articles p {
  color: #64748b;
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.reset-search-btn {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reset-search-btn:hover {
  background-color: #4338ca;
}

.category-tag {
  position: absolute;
  top: 0;
  right: 0;
  padding: 6px 12px;
  border-bottom-left-radius: 8px;
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
}

.new-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: #ef4444;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 5px rgba(239, 68, 68, 0.3);
}

.like-stat {
  cursor: pointer;
  transition: transform 0.15s ease;
}

.like-stat:hover {
  transform: scale(1.15);
}

.like-stat .icon.liked {
  color: #ef4444;
}

.like-stat:hover .icon:not(.liked) {
  opacity: 0.8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .articles-list {
    grid-template-columns: 1fr;
  }

  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    margin-bottom: 10px;
  }

  .filter-options {
    justify-content: center;
  }

  h2 {
    font-size: 2rem;
  }
}
</style>
