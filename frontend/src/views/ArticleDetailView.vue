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
const fetchArticle = async () => {
  loading.value = true
  error.value = null

  try {
    article.value = await articlesService.getArticle(articleId.value)
    
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
  max-width: 850px;
  margin: 0 auto;
  padding: 30px 20px;
  color: #333;
}

/* Loading and error states */
.loading-box, .error-message {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.spinner {
  border: 4px solid rgba(79, 70, 229, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4f46e5;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #ef4444;
  border: 1px solid #fee2e2;
}

.error-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 15px;
}

.back-btn {
  margin-top: 15px;
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #e5e7eb;
}

/* Navigation bar */
.navigation-bar {
  margin-bottom: 24px;
}

.back-nav-btn {
  display: flex;
  align-items: center;
  background-color: transparent;
  border: 1px solid #e5e7eb;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.back-nav-btn:hover {
  background-color: #f9fafb;
  color: #4f46e5;
  border-color: #4f46e5;
}

.back-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* Article card */
.article-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid #f1f5f9;
  transition: box-shadow 0.3s ease;
}

.article-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

/* Article header */
.article-header {
  padding: 30px 30px 15px;
  border-bottom: 1px solid #f1f5f9;
}

.article-title {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px 0;
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: white;
  border: 2px solid #f1f5f9;
}

.avatar-placeholder.small {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
  margin-bottom: 4px;
}

.dates {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 14px;
  color: #64748b;
}

.date {
  display: flex;
  align-items: center;
}

.date-icon, .edit-icon {
  margin-right: 4px;
  font-size: 14px;
}

/* Action buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.edit-btn, .delete-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s;
}

.edit-btn {
  background-color: #4f46e5;
  color: white;
}

.edit-btn:hover {
  background-color: #4338ca;
}

.delete-btn {
  background-color: #ef4444;
  color: white;
}

.delete-btn:hover {
  background-color: #dc2626;
}

.btn-icon {
  margin-right: 8px;
}

/* Article body */
.article-body {
  padding: 30px;
  font-size: 16px;
  line-height: 1.8;
  color: #334155;
}

.content-container {
  max-width: 100%;
  overflow-x: auto;
}

.content-paragraph {
  margin-bottom: 20px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Comments section */
.comments-section {
  margin-top: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  padding: 30px;
  border: 1px solid #f1f5f9;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f1f5f9;
}

.comments-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
}

.comment-icon {
  margin-right: 10px;
  color: #4f46e5;
  font-size: 20px;
}

.comment-count {
  background-color: #f1f5f9;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 14px;
  color: #4f46e5;
  margin-left: 8px;
}

/* Comment form */
.comment-form {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8fafc;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.comment-form:focus-within {
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
}

.form-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.user-avatar {
  margin-right: 12px;
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
  color: #1e293b;
}

.comment-form textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  resize: vertical;
  font-size: 15px;
  line-height: 1.6;
  font-family: inherit;
  transition: all 0.2s;
}

.comment-form textarea:focus {
  outline: none;
}

.textarea-focused {
  border-color: #4f46e5 !important;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.cancel-comment-btn, .submit-comment-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s;
}

.cancel-comment-btn {
  background-color: #e2e8f0;
  color: #475569;
}

.cancel-comment-btn:hover {
  background-color: #cbd5e1;
}

.submit-comment-btn {
  background-color: #4f46e5;
  color: white;
  opacity: 0.7;
}

.submit-comment-btn.btn-active {
  opacity: 1;
}

.submit-comment-btn.btn-active:hover {
  background-color: #4338ca;
}

/* Login prompt */
.login-prompt {
  text-align: center;
  padding: 20px;
  background-color: #f8fafc;
  border-radius: 8px;
  margin-bottom: 30px;
}

.login-icon {
  font-size: 24px;
  color: #64748b;
  margin-right: 10px;
}

.login-prompt p {
  color: #475569;
  font-size: 15px;
}

.login-link {
  color: #4f46e5;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.login-link:hover {
  text-decoration: underline;
}

/* Comments list */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment {
  padding: 20px;
  border-radius: 8px;
  background-color: #f8fafc;
  transition: all 0.2s;
}

.comment:hover {
  background-color: #f1f5f9;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
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
  font-size: 13px;
  color: #94a3b8;
  margin-top: 2px;
}

.comment-content {
  font-size: 15px;
  line-height: 1.6;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s;
  padding: 2px;
  border-radius: 4px;
}

.action-btn:hover {
  background-color: #e2e8f0;
}

.edit {
  color: #4f46e5;
}

.delete {
  color: #ef4444;
}

.edit-comment-form {
  margin-bottom: 10px;
}

.edit-comment-form textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  resize: vertical;
  font-size: 15px;
  line-height: 1.6;
  font-family: inherit;
}

.edit-comment-form textarea:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.cancel-btn, .save-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.cancel-btn {
  background-color: #e2e8f0;
  color: #475569;
}

.cancel-btn:hover {
  background-color: #cbd5e1;
}

.save-btn {
  background-color: #4f46e5;
  color: white;
}

.save-btn:hover {
  background-color: #4338ca;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
