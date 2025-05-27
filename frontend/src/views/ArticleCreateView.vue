<!-- src/views/ArticleCreateView.vue -->
<template>
  <div class="article-form-container">
    <h2>{{ isEditing ? '게시글 수정' : '새 게시글 작성' }}</h2>

    <form @submit.prevent="handleSubmit" class="article-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="articleForm.title" 
          placeholder="게시글 제목을 입력하세요"
          required
        />
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="articleForm.content" 
          placeholder="게시글 내용을 입력하세요"
          rows="12"
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" @click="goBack" class="cancel-btn">취소</button>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '처리 중...' : (isEditing ? '수정하기' : '작성하기') }}
        </button>
      </div>
    </form>
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

const articleForm = ref({
  title: '',
  content: '',
})

const loading = ref(false)
const error = ref(null)

const isEditing = computed(() => route.path.includes('/edit'))
const articleId = computed(() => route.params.id)

const handleSubmit = async () => {
  if (!articleForm.value.title.trim() || !articleForm.value.content.trim()) {
    alert('제목과 내용을 모두 입력해주세요.')
    return
  }

  loading.value = true
  error.value = null

  try {
    if (isEditing.value) {
      await articlesService.updateArticle(articleId.value, articleForm.value)
      router.push(`/articles/${articleId.value}`)
    } else {
      const response = await articlesService.createArticle(articleForm.value)
      router.push(`/articles/${response.id}`)
    }
  } catch (err) {
    console.error('Error saving article:', err)
    error.value = isEditing.value 
      ? '게시글 수정에 실패했습니다.' 
      : '게시글 작성에 실패했습니다.'
    alert(error.value)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const fetchArticle = async () => {
  if (!isEditing.value) return

  loading.value = true
  try {
    const article = await articlesService.getArticle(articleId.value)
    
    // Check if the current user is the author
    if (article.writer.id !== userStore.user.id) {
      alert('자신이 작성한 게시글만 수정할 수 있습니다.')
      router.push(`/articles/${articleId.value}`)
      return
    }
    
    articleForm.value.title = article.title
    articleForm.value.content = article.content
  } catch (err) {
    console.error('Error fetching article for editing:', err)
    alert('게시글을 불러오는데 실패했습니다.')
    router.push('/articles')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Check if user is logged in
  if (!userStore.isLoggedIn) {
    alert('로그인이 필요한 서비스입니다.')
    router.push('/login?redirect=' + route.fullPath)
    return
  }
  
  if (isEditing.value) {
    fetchArticle()
  }
})
</script>

<style scoped>
.article-form-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1.5rem;
  font-family: var(--font-family-base, 'Pretendard Variable', Pretendard, sans-serif);
}

.article-form-container h2 {
  font-size: 2.2rem; /* Title size */
  color: var(--text-primary);
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 700;
  font-family: 'Pretendard Variable', serif;
}

.article-form {
  background-color: var(--card-bg);
  padding: 2rem 2.5rem; /* Increased padding */
  border-radius: 16px; /* More rounded */
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
}

.form-group {
  margin-bottom: 1.8rem; /* Spacing between form groups */
}

label {
  display: block;
  margin-bottom: 0.75rem; /* Spacing below label */
  font-weight: 600; /* Bolder label */
  color: var(--text-primary);
  font-size: 1rem;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 0.9rem 1.2rem; /* Increased padding */
  border: 1px solid var(--border-color);
  border-radius: 8px; /* More rounded inputs */
  font-size: 1rem;
  background-color: var(--background-primary); /* Input background */
  color: var(--text-primary);
  transition: border-color var(--transition-speed), box-shadow var(--transition-speed);
}

input[type="text"]:focus,
textarea:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb, 163, 184, 153), 0.2); /* Accent focus shadow */
}

textarea {
  resize: vertical;
  min-height: 250px; /* Increased min-height */
  line-height: 1.6; /* Improved readability */
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem; /* Spacing between buttons */
  margin-top: 2rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem; /* Consistent button padding */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all var(--transition-speed);
}

.cancel-btn {
  background-color: var(--background-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.cancel-btn:hover {
  background-color: var(--border-color);
  color: var(--text-primary);
}

.submit-btn {
  background-color: var(--accent-color);
  color: var(--button-text);
  border: 1px solid var(--accent-color);
}

.submit-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.submit-btn:disabled {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
  color: rgba(var(--button-text-rgb, 255, 255, 255), 0.7);
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
