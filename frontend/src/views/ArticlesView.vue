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
          <button 
            @click="sortArticles('latest')" 
            :class="{ active: currentSort === 'latest' }"
          >
            최신순
          </button>
          <button 
            @click="sortArticles('comments')" 
            :class="{ active: currentSort === 'comments' }"
          >
            댓글순
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
          <img src="https://cdn-icons-png.flaticon.com/512/6598/6598519.png" alt="No articles" class="empty-icon">
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
              <span class="stat">
                <i class="icon">💬</i>
                {{ article.comment_count }}
              </span>
              <span class="stat">
                <i class="icon">❤️</i>
                {{ article.likes_count || 0 }}
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
const currentSort = ref('latest') // 'latest' or 'comments'

const fetchArticles = async () => {
  loading.value = true
  error.value = null

  try {
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
    sortArticles(currentSort.value, false)
    
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
      day: 'numeric'
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
  }
  
  if (sortBy === 'latest') {
    articles.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } else if (sortBy === 'comments') {
    articles.value.sort((a, b) => b.comment_count - a.comment_count)
  }
}

// Computed property for filtered articles
const filteredArticles = computed(() => {
  if (!searchQuery.value.trim()) {
    return articles.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return articles.value.filter(article => 
    article.title.toLowerCase().includes(query) || 
    (article.content && article.content.toLowerCase().includes(query)) ||
    article.writer.nickname.toLowerCase().includes(query)
  )
})

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.articles-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  background: linear-gradient(135deg, var(--color-background-start) 0%, var(--color-background-end) 100%);
  min-height: calc(100vh - 160px);
}

.articles-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

h2 {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--color-accent);
  font-family: var(--font-heading);
  position: relative;
  display: inline-block;
}

h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
  border-radius: 3px;
}

.subtitle {
  color: var(--color-text-light);
  font-size: var(--font-size-lg);
  font-family: var(--font-body);
  margin-top: 1.5rem;
  margin-bottom: 2rem;
}

.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-white);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-md);
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
  position: relative;
  overflow: hidden;
}

.search-filter-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-box input {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.5rem;
  border: 1px solid var(--color-secondary);
  border-radius: 50px;
  font-size: var(--font-size-base);
  font-family: var(--font-body);
  color: var(--color-text);
  background-color: var(--color-white);
  transition: all var(--transition-fast);
}

.search-box input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15);
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.1rem;
  color: var(--color-text-light);
}

.filter-options {
  display: flex;
  gap: 0.75rem;
}

.filter-options button {
  background-color: var(--color-secondary);
  border: 1px solid transparent;
  padding: 0.75rem 1.25rem;
  border-radius: 50px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  font-family: var(--font-body);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.filter-options button:hover {
  background-color: var(--color-secondary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.filter-options button.active {
  background-color: var(--color-primary);
  color: var(--color-white);
  box-shadow: var(--shadow-md);
}

.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem;
  background-color: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  text-align: center;
  color: var(--color-text);
  max-width: 600px;
  margin: 0 auto;
}

.spinner {
  display: inline-block;
  width: 60px;
  height: 60px;
  border: 3px solid rgba(var(--color-primary-rgb), 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.articles-content {
  position: relative;
}

.fab-button {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 65px;
  height: 65px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  z-index: 100;
  overflow: hidden;
}

.fab-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: left 0.6s;
}

.fab-button:hover {
  transform: translateY(-5px) rotate(90deg);
  background-color: var(--color-primary-dark);
  box-shadow: 0 10px 20px rgba(var(--color-primary-rgb), 0.4);
}

.fab-button:hover::before {
  left: 100%;
}

.fab-button:active {
  transform: translateY(-2px) rotate(90deg);
}

.plus-icon {
  font-size: 2.2rem;
  font-weight: 300;
}

.fab-tooltip {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--color-accent);
  color: var(--color-white);
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-family: var(--font-body);
  font-size: var(--font-size-sm);
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-md);
}

.fab-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: var(--color-accent) transparent transparent transparent;
}

.fab-button:hover .fab-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(-5px);
}

.articles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.article-card {
  position: relative;
  background: var(--color-white);
  border-radius: 12px;
  padding: 1.75rem;
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid var(--color-secondary);
  overflow: hidden;
}

.article-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 0;
  background: linear-gradient(to bottom, var(--color-primary), var(--color-primary-dark));
  transition: height 0.3s ease;
}

.article-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.article-card:hover::before {
  height: 100%;
}

.article-header {
  flex-grow: 1;
  margin-bottom: 1.5rem;
}

.article-title {
  margin: 0 0 0.75rem;
  font-size: var(--font-size-lg);
  color: var(--color-accent);
  line-height: 1.4;
  font-weight: 600;
  font-family: var(--font-heading);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color var(--transition-fast);
}

.article-card:hover .article-title {
  color: var(--color-primary);
}

.article-excerpt {
  color: var(--color-text-light);
  font-size: var(--font-size-base);
  margin: 0;
  line-height: 1.6;
  font-family: var(--font-body);
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
  border-top: 1px solid var(--color-secondary);
  padding-top: 1.25rem;
  margin-top: auto;
}

.author-info {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  width: 38px;
  height: 38px;
  margin-right: 12px;
  border-radius: 50%;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal);
}

.article-card:hover .avatar-wrapper {
  transform: scale(1.1);
}

.avatar-small {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-secondary);
  transition: border-color var(--transition-fast);
}

.article-card:hover .avatar-small {
  border-color: var(--color-primary);
}

.avatar-placeholder {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: var(--color-white);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid var(--color-secondary);
  font-family: var(--font-heading);
}

.author-name {
  font-size: var(--font-size-sm);
  color: var(--color-text);
  font-weight: 600;
  transition: color var(--transition-fast);
}

.article-card:hover .author-name {
  color: var(--color-primary);
}

.article-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  background: var(--color-secondary);
  padding: 0.35rem 0.65rem;
  border-radius: 50px;
  transition: all var(--transition-fast);
}

.article-card:hover .stat {
  background: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

.icon {
  margin-right: 0.35rem;
  font-size: 1rem;
}

.date {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  font-family: var(--font-body);
  transition: color var(--transition-fast);
}

.no-articles {
  grid-column: 1 / -1;
  background-color: var(--color-white);
  border-radius: 12px;
  padding: 4rem 2.5rem;
  text-align: center;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-secondary);
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.no-articles::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
}

.empty-icon {
  width: 90px;
  height: 90px;
  margin-bottom: 1.5rem;
  opacity: 0.8;
  filter: var(--color-filter);
  transition: transform 0.5s ease;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.no-articles p {
  color: var(--color-text);
  font-size: var(--font-size-lg);
  font-family: var(--font-body);
  margin-bottom: 1.5rem;
}

.reset-search-btn {
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-size: var(--font-size-base);
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.reset-search-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: left 0.6s;
}

.reset-search-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.reset-search-btn:hover::before {
  left: 100%;
}

.reset-search-btn:active {
  transform: translateY(-1px);
}

.category-tag {
  position: absolute;
  top: 0;
  right: 0;
  padding: 0.5rem 1rem;
  border-bottom-left-radius: 12px;
  color: var(--color-white);
  font-size: var(--font-size-xs);
  font-weight: 600;
  font-family: var(--font-body);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  box-shadow: var(--shadow-sm);
}

.new-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background-color: var(--color-accent);
  color: var(--color-white);
  padding: 0.35rem 0.75rem;
  border-radius: 50px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  font-family: var(--font-body);
  letter-spacing: 0.5px;
  box-shadow: var(--shadow-md);
  z-index: 2;
  transform: translateZ(0);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* 다크 모드 스타일 */
:global(.dark-mode) .articles-container {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

:global(.dark-mode) .search-filter-bar,
:global(.dark-mode) .loading-box,
:global(.dark-mode) .article-card,
:global(.dark-mode) .no-articles {
  background-color: #2D2D2D;
}

:global(.dark-mode) .search-box input {
  background-color: #333333;
  border-color: #444444;
  color: #e0e0e0;
}

:global(.dark-mode) .filter-options button:not(.active) {
  background-color: #333333;
  color: #e0e0e0;
}

:global(.dark-mode) .avatar-small {
  border-color: #444444;
}

:global(.dark-mode) .stat {
  background-color: #333333;
}

:global(.dark-mode) .article-card:hover .stat {
  background-color: rgba(var(--color-primary-rgb), 0.2);
}

/* 반응형 스타일 */
@media (max-width: 1024px) {
  .articles-list {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .articles-container {
    padding: 2rem 1rem;
  }
  
  h2 {
    font-size: var(--font-size-2xl);
  }
  
  .subtitle {
    font-size: var(--font-size-base);
  }
  
  .articles-list {
    grid-template-columns: 1fr;
  }
  
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }
  
  .search-box {
    margin-bottom: 1rem;
  }
  
  .filter-options {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .fab-button {
    bottom: 20px;
    right: 20px;
    width: 55px;
    height: 55px;
  }
}
</style>
