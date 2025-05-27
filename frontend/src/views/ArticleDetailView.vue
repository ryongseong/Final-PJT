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

          <div class="article-meta">
            <div class="author-info">
              <div class="avatar-wrapper">
                <img
                  v-if="article.writer && article.writer.profile_img"
                  :src="article.writer.profile_img"
                  alt="Author avatar"
                  class="avatar"
                  @error="handleAvatarError"
                />
                <div v-else class="avatar-placeholder">
                  {{ getInitials(article.writer ? article.writer.nickname : '?') }}
                </div>
              </div>
              <div class="author-details">
                <span class="author-name">{{
                  article.writer ? article.writer.nickname : '익명'
                }}</span>
                <div class="dates">
                  <span class="date">
                    <span class="date-icon">📆</span>
                    {{ formatDate(article.created_at) }}
                  </span>
                  <span v-if="article.updated_at !== article.created_at" class="date">
                    <span class="edit-icon">✏️</span>
                    수정됨
                  </span>
                </div>
              </div>
            </div>

            <!-- Action buttons for author -->
            <div v-if="isAuthor" class="action-buttons">
              <button @click="editArticle" class="edit-btn">
                <span class="btn-icon">✏️</span>
                수정
              </button>
              <button @click="confirmDelete" class="delete-btn">
                <span class="btn-icon">🗑️</span>
                삭제
              </button>
            </div>
          </div>
        </div>

        <!-- Likes section -->
        <div class="likes-section">
          <button @click="toggleLike" class="like-btn" :class="{ liked: article.is_liked }">
            <span class="like-icon">{{ article.is_liked ? '❤️' : '🤍' }}</span>
            <span class="like-count">{{ article.likes_count || 0 }}</span>
          </button>
        </div>

        <!-- Article content -->
        <div class="article-body">
          <div class="content-container">
            <p
              v-for="(paragraph, index) in contentParagraphs"
              :key="index"
              class="content-paragraph"
            >
              {{ paragraph }}
            </p>
          </div>
        </div>

        <!-- Comments section -->
        <div class="comments-section">
          <div class="comments-header">
            <h3>
              <span class="comment-icon">💬</span>
              댓글
              <span class="comment-count">{{
                article.comments ? article.comments.length : 0
              }}</span>
            </h3>
          </div>

          <!-- Comment form for logged in users -->
          <div
            v-if="userStore.isLoggedIn"
            class="comment-form"
            :class="{ 'textarea-focused': commentFocused }"
          >
            <div class="form-header">
              <div class="user-avatar">
                <img
                  v-if="userStore.user.profile_img"
                  :src="userStore.user.profile_img"
                  alt="User avatar"
                  class="avatar-small"
                  @error="handleAvatarError"
                />
                <div v-else class="avatar-placeholder small">
                  {{ getInitials(userStore.user.nickname) }}
                </div>
              </div>
              <span class="user-name">{{ userStore.user.nickname }}</span>
            </div>

            <textarea
              v-model="newComment"
              placeholder="댓글을 입력하세요..."
              @focus="commentFocused = true"
            ></textarea>

            <div v-if="commentFocused" class="form-actions">
              <button class="cancel-comment-btn" @click="cancelComment">취소</button>
              <button
                class="submit-comment-btn"
                :class="{ 'btn-active': newComment.trim().length > 0 }"
                @click="addComment"
              >
                등록
              </button>
            </div>
          </div>

          <!-- Login prompt for guests -->
          <div v-else class="login-prompt">
            <span class="login-icon">🔒</span>
            <p>댓글을 작성하려면 로그인이 필요합니다.</p>
            <router-link to="/login?redirect=/articles" class="login-link">
              로그인하기
            </router-link>
          </div>

          <!-- Comments list -->
          <div class="comments-list">
            <div v-if="!article.comments || article.comments.length === 0" class="no-comments">
              <span class="empty-icon">💭</span>
              <p>아직 댓글이 없습니다. 첫 댓글을 작성해보세요!</p>
            </div>

            <div v-for="comment in sortedComments" :key="comment.id" class="comment">
              <div class="comment-header">
                <div class="comment-author">
                  <div class="avatar-wrapper">
                    <img
                      v-if="comment.writer && comment.writer.profile_img"
                      :src="comment.writer.profile_img"
                      alt="Commenter avatar"
                      class="avatar-small"
                      @error="handleAvatarError"
                    />
                    <div v-else class="avatar-placeholder small">
                      {{ getInitials(comment.writer ? comment.writer.nickname : '?') }}
                    </div>
                  </div>
                  <div class="comment-author-details">
                    <span class="author-name">{{
                      comment.writer ? comment.writer.nickname : '익명'
                    }}</span>
                    <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                  </div>
                </div>

                <div v-if="isCommentAuthor(comment)" class="comment-actions">
                  <button class="action-btn edit" @click="editComment(comment)">수정</button>
                  <button class="action-btn delete" @click="deleteComment(comment.id)">삭제</button>
                </div>
              </div>

              <div v-if="editingCommentId !== comment.id" class="comment-content">
                {{ comment.content }}
              </div>

              <div v-else class="edit-comment-form">
                <textarea v-model="editCommentContent" :placeholder="comment.content"></textarea>
                <div class="edit-actions">
                  <button class="cancel-btn" @click="cancelEditing">취소</button>
                  <button
                    class="save-btn"
                    :disabled="!editCommentContent.trim()"
                    @click="saveEditedComment(comment.id)"
                  >
                    저장
                  </button>
                </div>
              </div>
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

// Computed properties
const articleId = computed(() => route.params.id)

const isAuthor = computed(() => {
  return (
    userStore.isLoggedIn && article.value.writer && article.value.writer.id === userStore.user.id
  )
})

const contentParagraphs = computed(() => {
  if (!article.value || !article.value.content) return []
  return article.value.content.split('\n').filter((para) => para.trim() !== '')
})

const sortedComments = computed(() => {
  if (!article.value.comments) return []
  return [...article.value.comments].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

// Methods for article
const fetchArticle = async () => {
  loading.value = true
  error.value = null

  try {
    article.value = await articlesService.getArticle(articleId.value)
    console.log('Article loaded:', article.value)
  } catch (err) {
    console.error('Error loading article:', err)
    error.value = '게시글을 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// Toggle like for the current article
const toggleLike = async () => {
  if (!userStore.isLoggedIn) {
    router.push(`/login?redirect=/articles/${articleId.value}`)
    return
  }

  try {
    const response = await articlesService.toggleLike(articleId.value)
    if (response.status === 'liked') {
      article.value.is_liked = true
      article.value.likes_count = (article.value.likes_count || 0) + 1
    } else {
      article.value.is_liked = false
      article.value.likes_count = Math.max(0, (article.value.likes_count || 1) - 1)
    }
  } catch (err) {
    console.error('Error toggling like:', err)
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
      minute: '2-digit',
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
  return userStore.isLoggedIn && comment.writer && comment.writer.id === userStore.user.id
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
/* General container */
.article-detail-container {
  max-width: 900px; /* 중앙 콘텐츠 영역 너비 조정 */
  margin: 2rem auto;
  padding: 1.5rem;
  font-family: var(--font-family-base, 'Pretendard Variable', Pretendard, sans-serif);
}

/* Loading and Error States */
.loading-box,
.error-message {
  text-align: center;
  padding: 3rem;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  color: var(--text-secondary);
  border: 1px solid var(--card-border);
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

.error-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: block;
}

.back-btn {
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

.back-btn:hover {
  background-color: var(--accent-hover);
}

/* Navigation Bar */
.navigation-bar {
  margin-bottom: 1.5rem;
}

.back-nav-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.6rem 1.2rem;
  background-color: transparent; 
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition-speed);
  font-size: 0.95rem;
  font-weight: 500;
}

.back-nav-btn:hover {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}

.back-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

/* Main Article Card */
.article-card {
  background-color: var(--card-bg);
  border-radius: 16px; /* More rounded */
  box-shadow: var(--card-shadow);
  padding: 2rem 2.5rem; /* Increased padding */
  border: 1px solid var(--card-border);
}

/* Article Header */
.article-header {
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.article-title {
  font-size: 2.5rem; /* Prominent title */
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  line-height: 1.3;
  font-family: 'Pretendard Variable', serif;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* Align items to top */
}

.author-info {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  border-radius: 50%;
  overflow: hidden;
  margin-right: 1rem;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.article-meta .avatar-wrapper {
  width: 48px;
  height: 48px;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 1.5rem;
  color: var(--accent-color);
  font-weight: 600;
}

.comments-list .comment-author .avatar-wrapper {
  width: 36px;
  height: 36px;
  margin-right: 0.75rem;
}

.avatar-small {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder.small {
  font-size: 1rem;
  color: var(--accent-color);
  font-weight: 600;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: 1.1rem; /* Slightly larger */
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.dates {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.date {
  display: inline-flex; /* Align icon and text */
  align-items: center;
  margin-right: 0.8rem;
}

.date-icon,
.edit-icon {
  margin-right: 0.3rem;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.action-buttons .edit-btn,
.action-buttons .delete-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  display: inline-flex;
  align-items: center;
  font-size: 0.9rem;
}

.action-buttons .edit-btn {
  background-color: transparent;
  color: var(--accent-color);
  border: 1px solid var(--accent-color);
}

.action-buttons .edit-btn:hover {
  background-color: var(--accent-color);
  color: var(--button-text);
}

.action-buttons .delete-btn {
  background-color: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.action-buttons .delete-btn:hover {
  background-color: #ef4444;
  color: white;
}

.btn-icon {
  margin-right: 0.4rem;
}

/* Likes Section */
.likes-section {
  margin-bottom: 2rem;
  display: flex;
  justify-content: flex-start; /* Align to left */
}

.like-btn {
  padding: 0.6rem 1.2rem;
  border-radius: 20px; /* Pill shape */
  background-color: var(--background-primary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-speed);
  display: inline-flex;
  align-items: center;
  font-size: 0.95rem;
}

.like-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.like-btn.liked {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}

.like-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem; /* Larger icon */
}

/* Article Body */
.article-body {
  font-size: 1.1rem; /* Comfortable reading size */
  line-height: 1.8; /* Increased line height */
  color: var(--text-primary);
  padding-bottom: 2rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.content-container {
  line-height: 1.7;
  color: var(--text-primary);
  font-size: 1.05rem;
}

.content-paragraph {
  margin-bottom: 1.5rem;
}

/* Comments Section */
.comments-section {
  border-top: 1px solid var(--border-color);
  padding-top: 30px;
}

.comments-header {
  margin-bottom: 20px;
}

.comments-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.comment-icon {
  font-size: 1.3rem;
}

.comment-count {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 400;
}

/* Comment Form */
.comment-form {
  background-color: var(--background-primary);
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 1px solid var(--border-color);
}

.comment-form .form-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.comment-form .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 0.75rem;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.comment-form .avatar-small {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.comment-form .user-name {
  font-weight: 600;
  color: var(--text-primary);
}

.comment-form textarea {
  width: 100%;
  min-height: 100px;
  padding: 1rem;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  background-color: var(--input-bg);
  color: var(--input-text);
  transition: border-color var(--transition-speed), box-shadow var(--transition-speed);
}

.comment-form textarea:focus {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb, 163, 184, 153), 0.2);
}

.comment-form .form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  gap: 0.75rem;
}

.comment-form .cancel-comment-btn,
.comment-form .submit-comment-btn {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  font-size: 0.9rem;
}

.comment-form .cancel-comment-btn {
  background-color: var(--button-secondary-bg);
  color: var(--button-secondary-text);
  border: 1px solid var(--button-secondary-border);
}

.comment-form .cancel-comment-btn:hover {
  background-color: var(--button-secondary-hover-bg);
  color: var(--text-primary);
}

.comment-form .submit-comment-btn {
  background-color: var(--accent-color);
  color: var(--button-text);
  border: 1px solid var(--accent-color);
  opacity: 0.7;
}

.comment-form .submit-comment-btn.btn-active {
  opacity: 1;
}

.comment-form .submit-comment-btn:hover:not(.btn-active) {
  opacity: 0.9;
}

.comment-form .submit-comment-btn.btn-active:hover {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

/* Login Prompt */
.login-prompt {
  text-align: center;
  padding: 2rem;
  background-color: var(--background-primary);
  border-radius: 12px;
  margin-bottom: 2rem;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.login-icon {
  font-size: 1.8rem;
  margin-bottom: 0.75rem;
  display: block;
}

.login-link {
  margin-top: 1rem;
  display: inline-block;
  padding: 0.7rem 1.5rem;
  background-color: var(--accent-color);
  color: var(--button-text);
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color var(--transition-speed);
}

.login-link:hover {
  background-color: var(--accent-hover);
}

/* Comments List */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment {
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 15px;
  transition: background-color 0.2s;
  border: 1px solid var(--border-color-light);
}

.comment:hover {
  background-color: var(--background-secondary);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.comment-author {
  display: flex;
  align-items: center;
}

.comment-author-details {
  display: flex;
  flex-direction: column;
}

.comment-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.15rem;
}

.comment-content {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-primary);
  padding-left: calc(32px + 0.75rem); /* Avatar width + margin */
}

.comment-actions {
  display: flex;
  gap: 0.5rem;
}

.comment-actions .action-btn {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
}

.comment-actions .action-btn.edit {
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}
.comment-actions .action-btn.edit:hover {
  background-color: var(--border-color);
  color: var(--text-primary);
}

.comment-actions .action-btn.delete {
  color: var(--button-danger-text-alt, #ef4444);
  border: 1px solid var(--button-danger-border-alt, #ef4444);
}
.comment-actions .action-btn.delete:hover {
  background-color: var(--button-danger-bg);
  color: var(--button-danger-text);
  border-color: var(--button-danger-bg);
}

.edit-comment-form {
  margin-top: 10px;
}

.edit-comment-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--input-border);
  border-radius: 6px;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 60px;
  margin-bottom: 10px;
  background-color: var(--input-bg);
  color: var(--input-text);
}

.edit-comment-form textarea:focus {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb, 163, 184, 153), 0.2);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn,
.save-btn {
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn {
  background-color: var(--button-secondary-bg);
  color: var(--button-secondary-text);
  border: 1px solid var(--button-secondary-border);
}

.cancel-btn:hover {
  background-color: var(--button-secondary-hover-bg);
  color: var(--text-primary);
}

.save-btn {
  background-color: var(--accent-color);
  color: var(--button-text);
  border: 1px solid var(--accent-color);
}

.save-btn:hover {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.save-btn:disabled {
  background-color: var(--button-disabled-bg);
  color: var(--button-disabled-text);
  border: 1px solid var(--button-disabled-bg);
  cursor: not-allowed;
}

.no-comments {
  text-align: center;
  padding: 30px 0;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.7;
}

/* Show placeholder when image fails to load */
.show-placeholder .avatar-placeholder {
  display: flex !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .article-detail-container {
    margin: 1rem auto;
    padding: 1rem;
  }
  .article-card {
    padding: 1.5rem;
  }
  .article-title {
    font-size: 2rem;
  }
  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }
  .article-body {
    font-size: 1rem;
  }
  .comments-section h3 {
    font-size: 1.4rem;
  }
  .comment-content {
    padding-left: 0; /* Adjust for smaller screens */
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
