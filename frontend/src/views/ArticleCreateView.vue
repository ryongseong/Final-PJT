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
  margin: 0 auto;
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
}

.article-form {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

input, textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

textarea {
  resize: vertical;
  min-height: 200px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn, .submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.cancel-btn {
  background-color: #e5e7eb;
}

.submit-btn {
  background-color: #4f46e5;
  color: white;
}

.submit-btn:disabled {
  background-color: #a5a3d8;
  cursor: not-allowed;
}
</style>
