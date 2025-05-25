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
/* Container and general layout */
.article-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}

/* Loading and error states */
.loading-box,
.error-message {
  text-align: center;
  padding: 50px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
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

.error-message {
  color: #dc2626;
}

.error-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}

.back-btn {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background-color: #4338ca;
}

/* Navigation bar */
.navigation-bar {
  margin-bottom: 20px;
}

.back-nav-btn {
  background: none;
  border: none;
  display: flex;
  align-items: center;
  color: #4f46e5;
  font-size: 1rem;
  padding: 0;
  cursor: pointer;
  transition: color 0.2s;
}

.back-nav-btn:hover {
  color: #4338ca;
}

.back-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

/* Article card */
.article-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.article-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Article header */
.article-header {
  margin-bottom: 30px;
}

.article-title {
  font-size: 2rem;
  color: #1e293b;
  margin-top: 0;
  margin-bottom: 20px;
  font-weight: 700;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.author-info {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  margin-right: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f1f5f9;
}

.avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #4f46e5;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  font-weight: 500;
  border: 2px solid #f1f5f9;
}

.avatar-placeholder.small {
  width: 32px;
  height: 32px;
  font-size: 0.9rem;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.dates {
  display: flex;
  gap: 10px;
  font-size: 0.85rem;
  color: #64748b;
}

.date {
  display: flex;
  align-items: center;
}

.date-icon,
.edit-icon {
  margin-right: 5px;
}

/* Likes section */
.likes-section {
  display: flex;
  align-items: end;
  justify-content: flex-end;
}

.like-btn {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 6px 16px;
  display: flex;
  align-items: end;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.like-btn:hover {
  background-color: #f1f5f9;
  transform: translateY(-2px);
}

.like-btn.liked {
  border-color: #fecdd3;
  background-color: #fff1f2;
}

.like-btn.liked:hover {
  background-color: #fecdd3;
}

.like-icon {
  font-size: 1.2rem;
}

.like-count {
  font-weight: 600;
  color: #334155;
}

/* Action buttons */
.action-buttons {
  display: flex;
  gap: 10px;
}

.edit-btn,
.delete-btn {
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-btn {
  background-color: #f1f5f9;
  color: #334155;
}

.edit-btn:hover {
  background-color: #e2e8f0;
}

.delete-btn {
  background-color: #fee2e2;
  color: #b91c1c;
}

.delete-btn:hover {
  background-color: #fecaca;
}

.btn-icon {
  font-size: 1rem;
}

/* Article body */
.article-body {
  margin-bottom: 30px;
}

.content-container {
  line-height: 1.7;
  color: #334155;
  font-size: 1.05rem;
}

.content-paragraph {
  margin-bottom: 1.5rem;
}

/* Comments section */
.comments-section {
  border-top: 1px solid #e2e8f0;
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
  color: #1e293b;
  margin: 0;
}

.comment-icon {
  font-size: 1.3rem;
}

.comment-count {
  font-size: 1rem;
  color: #64748b;
  font-weight: 400;
}

/* Comment form */
.comment-form {
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 30px;
}

.comment-form:focus-within {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.user-avatar {
  position: relative;
}

.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: #334155;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 80px;
  margin-bottom: 10px;
  transition: border-color 0.2s;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #4f46e5;
}

.textarea-focused {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-comment-btn,
.submit-comment-btn {
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-comment-btn {
  background-color: #f1f5f9;
  color: #64748b;
}

.cancel-comment-btn:hover {
  background-color: #e2e8f0;
}

.submit-comment-btn {
  background-color: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
}

.submit-comment-btn.btn-active {
  background-color: #4f46e5;
  color: white;
  cursor: pointer;
}

.submit-comment-btn.btn-active:hover {
  background-color: #4338ca;
}

/* Login prompt */
.login-prompt {
  text-align: center;
  padding: 30px;
  background-color: #f8fafc;
  border-radius: 12px;
  margin-bottom: 30px;
}

.login-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.7;
}

.login-prompt p {
  color: #64748b;
  margin-bottom: 15px;
}

.login-link {
  display: inline-block;
  background-color: #4f46e5;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.login-link:hover {
  background-color: #4338ca;
}

/* Comments list */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment {
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 15px;
  transition: background-color 0.2s;
}

.comment:hover {
  background-color: #f1f5f9;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  display: flex;
  align-items: center;
}

.comment-author-details {
  display: flex;
  flex-direction: column;
  margin-left: 10px;
}

.comment-date {
  font-size: 0.8rem;
  color: #94a3b8;
}

.comment-content {
  color: #334155;
  line-height: 1.5;
}

.comment-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: none;
  border: none;
  font-size: 0.85rem;
  color: #64748b;
  cursor: pointer;
  transition: color 0.2s;
}

.action-btn:hover {
  color: #334155;
}

.edit {
  color: #4f46e5;
}

.delete {
  color: #ef4444;
}

.edit-comment-form {
  margin-top: 10px;
}

.edit-comment-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.95rem;
  resize: vertical;
  min-height: 60px;
  margin-bottom: 10px;
}

.edit-comment-form textarea:focus {
  outline: none;
  border-color: #4f46e5;
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
  background-color: #f1f5f9;
  color: #64748b;
}

.cancel-btn:hover {
  background-color: #e2e8f0;
}

.save-btn {
  background-color: #4f46e5;
  color: white;
}

.save-btn:hover {
  background-color: #4338ca;
}

.save-btn:disabled {
  background-color: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
}

.no-comments {
  text-align: center;
  padding: 30px 0;
  color: #64748b;
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
  .article-title {
    font-size: 1.6rem;
  }

  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .action-buttons {
    width: 100%;
    justify-content: flex-end;
  }

  .likes-section {
    margin-left: auto;
  }
}
</style>
