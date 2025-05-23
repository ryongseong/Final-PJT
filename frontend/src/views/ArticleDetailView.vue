<!-- src/views/ArticleDetailView.vue -->
<template>
  <div class="article-detail-container">
    <!-- Loading state -->
    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p>게시글 로딩 중...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      <i class="error-icon">⚠️</i>
      <p>{{ error }}</p>
      <button @click="goBack" class="back-btn">뒤로 가기</button>
    </div>

    <!-- Content state -->
    <div v-else class="article-content">
      <!-- Page navigation -->
      <div class="navigation-bar">
        <button @click="goBack" class="back-nav-btn">
          <i class="back-icon">←</i>
          <span>게시판으로 돌아가기</span>
        </button>
      </div>

      <!-- Main article card -->
      <div class="article-card">
        <!-- Article header with metadata -->
        <div class="article-header">
          <h1 class="article-title">{{ article.title }}</h1>
          
          <div class="article-actions">
            <button @click="toggleLike" class="like-button" :class="{ 'liked': isLiked }">
              <i class="like-icon">{{ isLiked ? '❤️' : '🤍' }}</i>
              <span class="like-count">{{ likesCount }}</span>
            </button>
          </div>
          
          <div class="article-meta">
            <div class="author-info">
              <div class="avatar-wrapper">
                <img 
                  v-if="article.writer.profile_img" 
                  :src="article.writer.profile_img" 
                  alt="Avatar" 
                  class="avatar"
                  @error="handleAvatarError"
                />
                <div v-else class="avatar-placeholder">
                  {{ getInitials(article.writer.nickname) }}
                </div>
              </div>
              <div class="author-details">
                <span class="author-name">{{ article.writer.nickname }}</span>
                <div class="dates">
                  <span class="date">
                    <i class="date-icon">📅</i> {{ formatDate(article.created_at) }}
                  </span>
                  <span v-if="article.created_at !== article.updated_at" class="date edit-date">
                    <i class="edit-icon">✏️</i> {{ formatDate(article.updated_at) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Action buttons for author -->
            <div class="action-buttons" v-if="isAuthor">
              <button @click="editArticle" class="edit-btn">
                <i class="btn-icon">✏️</i> 수정
              </button>
              <button @click="confirmDelete" class="delete-btn">
                <i class="btn-icon">🗑️</i> 삭제
              </button>
            </div>
          </div>
        </div>

        <!-- Article content -->
        <div class="article-body">
          <div class="content-container">
            <p v-for="(paragraph, index) in contentParagraphs" 
              :key="index" 
              class="content-paragraph"
            >
              {{ paragraph }}
            </p>
          </div>
        </div>
      </div>

      <!-- Comments section -->
      <div class="comments-section">
        <div class="comments-header">
          <h3>
            <i class="comment-icon">💬</i> 
            댓글 <span class="comment-count">{{ article.comments.length }}</span>
          </h3>
        </div>
        
        <!-- Comment form for logged in users -->
        <div v-if="userStore.isLoggedIn" class="comment-form">
          <div class="form-header">
            <div class="user-avatar">
              <img 
                v-if="userStore.user.profile_img" 
                :src="userStore.user.profile_img" 
                alt="Your Avatar" 
                class="avatar-small"
                @error="handleAvatarError"
              />
              <div v-else class="avatar-placeholder small">
                {{ getInitials(userStore.user.nickname || userStore.user.username) }}
              </div>
            </div>
            <span class="user-name">{{ userStore.user.nickname || userStore.user.username }}</span>
          </div>
          <textarea
            v-model="newComment"
            placeholder="의견을 남겨보세요..."
            rows="3"
            @focus="commentFocused = true"
            @blur="commentFocused = newComment.trim() !== ''"
            :class="{ 'textarea-focused': commentFocused }"
          ></textarea>
          <div class="form-actions" v-show="commentFocused">
            <button @click="cancelComment" class="cancel-comment-btn">취소</button>
            <button 
              @click="addComment" 
              :disabled="!newComment.trim()" 
              :class="['submit-comment-btn', {'btn-active': newComment.trim()}]"
            >
              댓글 작성
            </button>
          </div>
        </div>
        
        <!-- Login prompt for guests -->
        <div v-else class="login-prompt">
          <i class="login-icon">🔒</i>
          <p>댓글을 작성하려면 <router-link to="/login" class="login-link">로그인</router-link>이 필요합니다.</p>
        </div>

        <!-- Comments list -->
        <div class="comments-list">
          <div v-if="article.comments.length === 0" class="no-comments">
            <i class="empty-icon">💭</i>
            <p>아직 댓글이 없습니다. 첫 댓글을 남겨보세요!</p>
          </div>

          <div v-for="comment in sortedComments" :key="comment.id" class="comment">
            <div class="comment-header">
              <div class="comment-author">
                <div class="avatar-wrapper small">
                  <img 
                    v-if="comment.writer.profile_img" 
                    :src="comment.writer.profile_img" 
                    alt="Avatar" 
                    class="avatar-small"
                    @error="handleAvatarError"
                  />
                  <div v-else class="avatar-placeholder small">
                    {{ getInitials(comment.writer.nickname) }}
                  </div>
                </div>
                <div class="comment-author-details">
                  <span class="author-name">{{ comment.writer.nickname }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                </div>
              </div>
              
              <div v-if="isCommentAuthor(comment) && editingCommentId === null" class="comment-actions">
                <button @click="editComment(comment)" class="action-btn edit">
                  <i class="icon">✏️</i>
                </button>
                <button @click="deleteComment(comment.id)" class="action-btn delete">
                  <i class="icon">🗑️</i>
                </button>
              </div>
            </div>

            <div class="comment-content">
              <div v-if="editingCommentId === comment.id" class="edit-comment-form">
                <textarea
                  v-model="editCommentContent"
                  rows="2"
                  ref="editTextarea"
                ></textarea>
                <div class="edit-actions">
                  <button @click="cancelEditing" class="cancel-btn">취소</button>
                  <button @click="saveEditedComment(comment.id)" class="save-btn" :disabled="!editCommentContent.trim()">저장</button>
                </div>
              </div>
              <p v-else>{{ comment.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import articlesService from '@/services/articles'
import { useUserStore } from '@/stores/user'
import { getAbsoluteImageUrl } from '@/utils/imageUtils'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// State management
const article = ref({})
const loading = ref(true)
const error = ref(null)
const newComment = ref('')
const editingCommentId = ref(null)
const editCommentContent = ref('')
const commentFocused = ref(false)
const isLiked = ref(false)
const likesCount = ref(0)

// Computed properties
const articleId = computed(() => route.params.id)

const isAuthor = computed(() => {
  return userStore.isLoggedIn && article.value.writer && 
         article.value.writer.id === userStore.user.id
})

const contentParagraphs = computed(() => {
  if (!article.value || !article.value.content) return []
  return article.value.content.split('\n').filter(para => para.trim() !== '')
})

const sortedComments = computed(() => {
  if (!article.value.comments) return []
  return [...article.value.comments].sort((a, b) => 
    new Date(b.created_at) - new Date(a.created_at)
  )
})

// Methods for article
// 좋아요 토글 기능
const toggleLike = async () => {
  if (!userStore.isLoggedIn) {
    alert('로그인이 필요한 기능입니다.')
    router.push('/login')
    return
  }
  
  try {
    const response = await articlesService.toggleLike(articleId.value)
    isLiked.value = response.liked
    likesCount.value = response.likes_count
  } catch (err) {
    console.error('좋아요 처리 중 오류:', err)
  }
}

const fetchArticle = async () => {
  loading.value = true
  error.value = null

  try {
    article.value = await articlesService.getArticle(articleId.value)
    
    // 좋아요 상태 초기화
    if (article.value.likes) {
      likesCount.value = article.value.likes.length
      isLiked.value = userStore.isLoggedIn && article.value.likes.some(user => user.id === userStore.user.id)
    } else {
      likesCount.value = 0
      isLiked.value = false
    }
    
    // Process profile images for article author and comments
    if (article.value.writer && article.value.writer.profile_img) {
      article.value.writer.profile_img = getAbsoluteImageUrl(article.value.writer.profile_img)
    }
    
    if (article.value.comments && article.value.comments.length > 0) {
      article.value.comments.forEach(comment => {
        if (comment.writer && comment.writer.profile_img) {
          comment.writer.profile_img = getAbsoluteImageUrl(comment.writer.profile_img)
        }
      })
    }
  } catch (err) {
    console.error('Error fetching article:', err)
    error.value = '게시글을 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

const handleAvatarError = (e) => {
  // Replace broken image with placeholder
  console.log('Error loading avatar:', e.target.src)
  e.target.style.display = 'none'
  e.target.parentNode.classList.add('show-placeholder')
}

const editArticle = () => {
  router.push(`/articles/${articleId.value}/edit`)
}

const confirmDelete = async () => {
  if (!confirm('정말로 이 게시글을 삭제하시겠습니까?')) return

  try {
    await articlesService.deleteArticle(articleId.value)
    router.push('/articles')
  } catch (err) {
    console.error('Error deleting article:', err)
    alert('게시글 삭제에 실패했습니다.')
  }
}

const goBack = () => {
  router.go(-1)
}

// Methods for comments
const addComment = async () => {
  if (!newComment.value.trim()) return

  try {
    await articlesService.addComment(articleId.value, newComment.value)
    newComment.value = ''
    commentFocused.value = false
    await fetchArticle() // Refresh article to show new comment
  } catch (err) {
    console.error('Error adding comment:', err)
    alert('댓글 작성에 실패했습니다.')
  }
}

const cancelComment = () => {
  newComment.value = ''
  commentFocused.value = false
}

const isCommentAuthor = (comment) => {
  return userStore.isLoggedIn && comment.writer && 
         comment.writer.id === userStore.user.id
}

const editComment = (comment) => {
  editingCommentId.value = comment.id
  editCommentContent.value = comment.content
}

const saveEditedComment = async (commentId) => {
  if (!editCommentContent.value.trim()) return

  try {
    await articlesService.updateComment(commentId, editCommentContent.value)
    editingCommentId.value = null
    await fetchArticle() // Refresh article to show updated comment
  } catch (err) {
    console.error('Error updating comment:', err)
    alert('댓글 수정에 실패했습니다.')
  }
}

const cancelEditing = () => {
  editingCommentId.value = null
  editCommentContent.value = ''
}

const deleteComment = async (commentId) => {
  if (!confirm('정말로 이 댓글을 삭제하시겠습니까?')) return

  try {
    await articlesService.deleteComment(commentId)
    await fetchArticle() // Refresh article to remove deleted comment
  } catch (err) {
    console.error('Error deleting comment:', err)
    alert('댓글 삭제에 실패했습니다.')
  }
}

// Lifecycle hooks
onMounted(() => {
  fetchArticle()
})
</script>

<style scoped>
/* Container and general layout */
.article-detail-container {
  max-width: 950px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  color: var(--color-text);
  background: linear-gradient(135deg, var(--color-background-start) 0%, var(--color-background-end) 100%);
  min-height: calc(100vh - 160px);
}

/* Loading and error states */
.loading-box, .error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.loading-box::before, .error-message::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
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

.error-message {
  color: var(--color-accent);
  border: 1px solid var(--color-secondary);
}

.error-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 1.5rem;
  animation: shake 0.82s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.back-btn {
  margin-top: 1.5rem;
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.back-btn::before {
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

.back-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.back-btn:hover::before {
  left: 100%;
}

.back-btn:active {
  transform: translateY(-1px);
}

/* Navigation bar */
.navigation-bar {
  margin-bottom: 2rem;
}

.back-nav-btn {
  display: flex;
  align-items: center;
  background-color: var(--color-white);
  border: 1px solid var(--color-secondary);
  padding: 0.75rem 1.25rem;
  border-radius: 50px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  font-family: var(--font-body);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.back-nav-btn:hover {
  background-color: var(--color-secondary);
  color: var(--color-primary);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.back-icon {
  margin-right: 0.75rem;
  font-size: 1.1rem;
  transition: transform 0.2s ease;
}

.back-nav-btn:hover .back-icon {
  transform: translateX(-3px);
}

/* Article card */
.article-card {
  background-color: var(--color-white);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
  border: 1px solid var(--color-secondary);
  transition: all var(--transition-normal);
  position: relative;
}

.article-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
}

.article-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-5px);
}

/* Article header */
.article-header {
  padding: 2.5rem 2.5rem 1.5rem;
  border-bottom: 1px solid var(--color-secondary);
  position: relative;
}

.article-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-accent);
  margin: 0 0 1.5rem 0;
  line-height: 1.3;
  font-family: var(--font-heading);
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.25rem;
}

.author-info {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  margin-right: 1rem;
  border-radius: 50%;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal);
}

.article-card:hover .avatar-wrapper {
  transform: scale(1.05);
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-secondary);
  transition: border-color var(--transition-fast);
}

.article-card:hover .avatar {
  border-color: var(--color-primary);
}

.avatar-placeholder {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-white);
  border: 2px solid var(--color-secondary);
  font-family: var(--font-heading);
}

.avatar-placeholder.small {
  width: 38px;
  height: 38px;
  font-size: 1rem;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--font-size-md);
  margin-bottom: 0.5rem;
  font-family: var(--font-body);
  transition: color var(--transition-fast);
}

.article-card:hover .author-name {
  color: var(--color-primary);
}

.dates {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.date {
  display: flex;
  align-items: center;
  background: var(--color-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: 50px;
  transition: all var(--transition-fast);
}

.article-card:hover .date {
  background: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

.date-icon, .edit-icon {
  margin-right: 0.4rem;
  font-size: 1rem;
}

/* Action buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.edit-btn, .delete-btn {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  font-size: var(--font-size-sm);
  font-family: var(--font-body);
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.edit-btn::before, .delete-btn::before {
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

.edit-btn {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.edit-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.edit-btn:hover::before {
  left: 100%;
}

.edit-btn:active {
  transform: translateY(-1px);
}

.delete-btn {
  background-color: var(--color-accent);
  color: var(--color-white);
}

.delete-btn:hover {
  background-color: #d32f2f; /* Darker red */
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.delete-btn:hover::before {
  left: 100%;
}

.delete-btn:active {
  transform: translateY(-1px);
}

.btn-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

/* Article body */
.article-body {
  padding: 2.5rem;
  font-size: var(--font-size-base);
  line-height: 1.8;
  color: var(--color-text);
  font-family: var(--font-body);
}

.content-container {
  max-width: 100%;
  overflow-x: auto;
}

.content-paragraph {
  margin-bottom: 1.5rem;
  white-space: pre-wrap;
  word-break: break-word;
  letter-spacing: 0.01em;
  transition: color var(--transition-fast);
}

.article-card:hover .content-paragraph {
  color: var(--color-text-dark);
}

/* Comments section */
.comments-section {
  margin-top: 2.5rem;
  background-color: var(--color-white);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  padding: 2.5rem;
  border: 1px solid var(--color-secondary);
  position: relative;
}

.comments-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--color-secondary);
  position: relative;
}

.comments-header h3 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-accent);
  margin: 0;
  display: flex;
  align-items: center;
  font-family: var(--font-heading);
}

.comment-icon {
  margin-right: 1rem;
  color: var(--color-primary);
  font-size: 1.4rem;
  transition: transform 0.3s ease;
}

.comments-header:hover .comment-icon {
  transform: scale(1.2);
}

.comment-count {
  background-color: var(--color-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: 50px;
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  margin-left: 0.75rem;
  font-weight: 600;
  font-family: var(--font-body);
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.comments-header:hover .comment-count {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  transform: translateX(3px);
}

/* Comment form */
.comment-form {
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  background-color: var(--color-secondary);
  border-radius: 12px;
  transition: all var(--transition-normal);
  border: 1px solid transparent;
}

.comment-form:focus-within {
  box-shadow: var(--shadow-md);
  border-color: rgba(var(--color-primary-rgb), 0.2);
  background-color: var(--color-white);
  transform: translateY(-3px);
}

.form-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.25rem;
}

.user-avatar {
  margin-right: 1rem;
  position: relative;
  transition: transform var(--transition-normal);
}

.comment-form:focus-within .user-avatar {
  transform: scale(1.1);
}

.avatar-small {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-secondary);
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.comment-form:focus-within .avatar-small {
  border-color: var(--color-primary);
}

.user-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--font-size-sm);
  font-family: var(--font-body);
  transition: color var(--transition-fast);
}

.comment-form:focus-within .user-name {
  color: var(--color-primary);
}

.comment-form textarea {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 1px solid var(--color-secondary);
  border-radius: 12px;
  resize: vertical;
  font-size: var(--font-size-base);
  line-height: 1.6;
  font-family: var(--font-body);
  color: var(--color-text);
  background-color: var(--color-white);
  transition: all var(--transition-fast);
  min-height: 100px;
}

.comment-form textarea:focus {
  outline: none;
}

.textarea-focused {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15);
  transform: scale(1.01);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.cancel-comment-btn, .submit-comment-btn {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  font-size: var(--font-size-sm);
  font-family: var(--font-body);
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.cancel-comment-btn::before, .submit-comment-btn::before {
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

.cancel-comment-btn {
  background-color: var(--color-secondary);
  color: var(--color-text);
}

.cancel-comment-btn:hover {
  background-color: var(--color-secondary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.cancel-comment-btn:hover::before {
  left: 100%;
}

.cancel-comment-btn:active {
  transform: translateY(-1px);
}

.submit-comment-btn {
  background-color: var(--color-primary);
  color: var(--color-white);
  opacity: 0.7;
}

.submit-comment-btn.btn-active {
  opacity: 1;
}

.submit-comment-btn.btn-active:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.submit-comment-btn:hover::before {
  left: 100%;
}

.submit-comment-btn:active {
  transform: translateY(-1px);
}

/* Login prompt */
.login-prompt {
  text-align: center;
  padding: 2rem;
  background-color: var(--color-secondary);
  border-radius: 12px;
  margin-bottom: 2.5rem;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
  transition: all var(--transition-normal);
}

.login-prompt:hover {
  border-color: rgba(var(--color-primary-rgb), 0.2);
  background-color: var(--color-white);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.login-prompt::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.login-prompt:hover::before {
  opacity: 1;
}

.login-icon {
  font-size: 1.75rem;
  color: var(--color-primary);
  margin-right: 0.75rem;
  transition: transform 0.3s ease;
  display: inline-block;
}

.login-prompt:hover .login-icon {
  transform: scale(1.2);
}

.login-prompt p {
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-family: var(--font-body);
  margin-top: 0.75rem;
}

.login-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  padding: 0 0.15rem;
}

.login-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--color-primary);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.3s ease;
}

.login-link:hover {
  color: var(--color-primary-dark);
}

/* 좋아요 버튼 스타일 */
.article-actions {
  display: flex;
  justify-content: flex-end;
  margin: 1rem 0;
}

.like-button {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: var(--color-white);
  border: 1px solid var(--color-secondary);
  border-radius: 50px;
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.like-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.like-button.liked {
  background-color: rgba(255, 0, 0, 0.05);
  border-color: rgba(255, 0, 0, 0.3);
}

.like-icon {
  margin-right: 0.5rem;
  font-style: normal;
}

.like-count {
  font-weight: 600;
}

.login-link:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}

/* Comments list */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment {
  padding: 1.5rem;
  border-radius: 12px;
  background-color: var(--color-secondary);
  transition: all var(--transition-normal);
  border: 1px solid transparent;
  position: relative;
  overflow: hidden;
}

.comment::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 0;
  background: linear-gradient(to bottom, var(--color-primary), var(--color-primary-dark));
  transition: height 0.3s ease;
}

.comment:hover {
  background-color: var(--color-white);
  border-color: rgba(var(--color-primary-rgb), 0.1);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.comment:hover::before {
  height: 100%;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.comment-author {
  display: flex;
  align-items: center;
  transition: transform var(--transition-fast);
}

.comment:hover .comment-author {
  transform: translateX(5px);
}

.comment-author-details {
  display: flex;
  flex-direction: column;
}

.comment-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  margin-top: 0.25rem;
  font-family: var(--font-body);
  background: var(--color-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 50px;
  display: inline-block;
  transition: all var(--transition-fast);
  width: fit-content;
}

.comment:hover .comment-date {
  background: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

.comment-content {
  font-size: var(--font-size-base);
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-body);
  transition: color var(--transition-fast);
}

.comment:hover .comment-content {
  color: var(--color-text-dark);
}

.comment-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  background-color: var(--color-secondary);
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  padding: 0.5rem;
  border-radius: 50%;
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.action-btn .icon {
  font-size: 1rem;
  transition: transform 0.3s ease;
}

.action-btn:hover .icon {
  transform: scale(1.2);
}

.edit {
  color: var(--color-primary);
}

.action-btn.edit:hover {
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.delete {
  color: var(--color-accent);
}

.action-btn.delete:hover {
  background-color: rgba(var(--color-accent-rgb), 0.1);
}

.edit-comment-form {
  margin-bottom: 1rem;
}

.edit-comment-form textarea {
  width: 100%;
  padding: 0.85rem 1rem;
  border: 1px solid var(--color-secondary);
  border-radius: 12px;
  resize: vertical;
  font-size: var(--font-size-base);
  line-height: 1.6;
  font-family: var(--font-body);
  color: var(--color-text);
  background-color: var(--color-white);
  transition: all var(--transition-fast);
}

.edit-comment-form textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15);
  transform: scale(1.01);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.cancel-btn, .save-btn {
  padding: 0.65rem 1.25rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 600;
  font-family: var(--font-body);
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.cancel-btn::before, .save-btn::before {
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

.cancel-btn {
  background-color: var(--color-secondary);
  color: var(--color-text);
}

.cancel-btn:hover {
  background-color: var(--color-secondary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.cancel-btn:hover::before {
  left: 100%;
}

.cancel-btn:active {
  transform: translateY(-1px);
}

.save-btn {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.save-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.save-btn:hover::before {
  left: 100%;
}

.save-btn:active {
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow-md);
}

/* 댓글 없음 상태 */
.no-comments {
  text-align: center;
  padding: 2.5rem 2rem;
  border-radius: 12px;
  background-color: var(--color-secondary);
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}

.no-comments::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
  opacity: 0.5;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: inline-block;
  opacity: 0.7;
  animation: pulse 2s infinite;
}

.no-comments p {
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-family: var(--font-body);
}

/* 다크 모드 지원 */
:global(.dark-mode) .article-detail-container {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

:global(.dark-mode) .article-card,
:global(.dark-mode) .comments-section,
:global(.dark-mode) .comment-form,
:global(.dark-mode) .login-prompt,
:global(.dark-mode) .edit-comment-form textarea,
:global(.dark-mode) .loading-box,
:global(.dark-mode) .error-message {
  background-color: #2D2D2D;
  border-color: #444444;
}

:global(.dark-mode) .comment {
  background-color: #333333;
}

:global(.dark-mode) .comment:hover {
  background-color: #2D2D2D;
  border-color: rgba(var(--color-primary-rgb), 0.2);
}

:global(.dark-mode) .comment-date,
:global(.dark-mode) .action-btn {
  background-color: #444444;
}

:global(.dark-mode) .comment:hover .comment-date {
  background-color: rgba(var(--color-primary-rgb), 0.2);
}

:global(.dark-mode) .form-actions button,
:global(.dark-mode) .edit-actions button {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

:global(.dark-mode) .cancel-btn {
  background-color: #444444;
  color: #e0e0e0;
}

:global(.dark-mode) .back-nav-btn {
  background-color: #333333;
  border-color: #444444;
  color: #e0e0e0;
}

:global(.dark-mode) .date {
  background-color: #333333;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .article-detail-container {
    padding: 1.5rem 1rem;
  }
  
  .article-title {
    font-size: var(--font-size-2xl);
  }
  
  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .action-buttons {
    margin-top: 0.5rem;
    align-self: flex-end;
  }
  
  .comments-header h3 {
    font-size: var(--font-size-lg);
  }
  
  .comment-author-details {
    font-size: var(--font-size-sm);
  }
}

.no-comments {
  text-align: center;
  padding: 30px 0;
  color: #64748b;
}

.empty-icon {
  font-size: 32px;
  color: #94a3b8;
  margin-bottom: 15px;
  display: block;
}

/* Show placeholder when image fails to load */
.show-placeholder .avatar-placeholder {
  display: flex !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .article-detail-container {
    padding: 20px 15px;
  }
  
  .article-header {
    padding: 20px 20px 10px;
  }
  
  .article-title {
    font-size: 24px;
  }
  
  .article-meta {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .action-buttons {
    margin-top: 10px;
    align-self: flex-end;
  }
  
  .article-body {
    padding: 20px;
  }
  
  .comments-section {
    padding: 20px;
  }
}
</style>
