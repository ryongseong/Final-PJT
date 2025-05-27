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
/* General Container */
.articles-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 1.5rem;
  font-family: var(--font-family-base, 'Pretendard Variable', Pretendard, sans-serif);
}

/* Header Section */
.articles-header {
  margin-bottom: 2.5rem;
  text-align: center;
}

.articles-header h2 {
  font-size: 2.8rem; /* Increased size */
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  font-weight: 700; /* Bold */
  font-family: 'Pretendard Variable', serif; /* Title font */
}

.articles-header .subtitle {
  font-size: 1.2rem; /* Increased size */
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

/* Search and Filter Bar */
.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem; /* Spacing */
  padding: 1rem;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
}

.search-box {
  display: flex;
  align-items: center;
  background-color: var(--background-primary);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  flex-grow: 1;
  margin-right: 1.5rem;
  border: 1px solid var(--border-color);
}

.search-box input {
  border: none;
  outline: none;
  background-color: transparent;
  flex-grow: 1;
  padding: 0.5rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.search-box .search-icon {
  color: var(--text-secondary);
  font-size: 1.2rem;
}

.filter-options button {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 0.7rem 1.2rem;
  margin-left: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition-speed);
  font-weight: 500;
}

.filter-options button:hover,
.filter-options button.active {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}

/* Loading Box */
.loading-box {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

/* Articles Content Area */
.articles-content {
  position: relative; /* For FAB positioning */
}

/* FAB Button */
.fab-button {
  position: fixed;
  bottom: 3rem;
  right: 3rem;
  background-color: var(--accent-color);
  color: var(--button-text);
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all var(--transition-speed);
  z-index: 900;
}

.fab-button:hover {
  background-color: var(--accent-hover);
  transform: scale(1.1);
}

.fab-button .plus-icon {
  line-height: 1;
}

.fab-tooltip {
  position: absolute;
  bottom: 100%;
  right: 50%;
  transform: translateX(50%) translateY(-0.5rem);
  background-color: var(--text-primary);
  color: var(--background-primary);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 0.85rem;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity var(--transition-speed), visibility var(--transition-speed);
}

.fab-button:hover .fab-tooltip {
  opacity: 1;
  visibility: visible;
}

/* Articles List */
.articles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); /* Responsive cards */
  gap: 2rem;
}

/* Article Card Styling */
.article-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 1.8rem; /* Increased padding */
  cursor: pointer;
  transition: all var(--transition-speed);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--card-border);
}

.article-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(var(--shadow-color), 0.15); /* Enhanced shadow */
}

.article-header {
  margin-bottom: 1rem;
}

.article-title {
  font-size: 1.5rem; /* Increased size */
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.6rem;
  line-height: 1.4;
  /* For multi-line ellipsis */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.4em * 2); /* Ensure consistent height */
}

.article-excerpt {
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  /* For multi-line ellipsis */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.6em * 3); /* Ensure consistent height */
  margin-bottom: 1rem;
}

.article-meta {
  margin-top: auto; /* Push to bottom */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.author-info {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  width: 36px; /* Slightly larger */
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 0.75rem;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-small {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 1rem;
  color: var(--accent-color);
  font-weight: 600;
}

.author-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
}

.article-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.article-stats .stat {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.article-stats .like-stat {
  cursor: pointer;
}

.article-stats .icon {
  font-size: 1.1rem;
}

.article-stats .liked {
  color: var(--accent-color); /* Or a specific like color e.g., red */
}

.no-articles {
  text-align: center;
  padding: 3rem 1rem;
  grid-column: 1 / -1; /* Span all columns if grid */
  color: var(--text-secondary);
}

.empty-icon {
  width: 100px;
  height: 100px;
  opacity: 0.6;
  margin-bottom: 1.5rem;
}

.reset-search-btn {
  margin-top: 1.5rem;
  padding: 0.7rem 1.5rem;
  background-color: var(--accent-color);
  color: var(--button-text);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color var(--transition-speed);
  font-weight: 500;
}

.reset-search-btn:hover {
  background-color: var(--accent-hover);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .articles-header h2 {
    font-size: 2.2rem;
  }
  .articles-header .subtitle {
    font-size: 1rem;
  }
  .search-filter-bar {
    flex-direction: column;
    gap: 1rem;
  }
  .search-box {
    margin-right: 0;
    width: 100%;
  }
  .filter-options {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .filter-options button {
    margin-left: 0;
  }
  .articles-list {
    grid-template-columns: 1fr; /* Single column on smaller screens */
  }
  .fab-button {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
    bottom: 1.5rem;
    right: 1.5rem;
  }
}
</style>
