<template>
  <div class="ai-recommendations-container">
    <div class="header">
      <h1>AI 맞춤 금융상품 추천</h1>
      <p class="subtitle">
        AI가 고객님의 재정 상황과 선호도에 맞는 최적의 금융상품을 추천해드립니다.
      </p>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label for="period">투자/대출 기간 (개월)</label>
        <input type="number" id="period" v-model="period" min="1" max="60" class="form-control" />
      </div>

      <div class="filter-group">
        <label for="productType">상품 유형</label>
        <select id="productType" v-model="productType" class="form-select">
          <option value="all">전체</option>
          <option value="deposit">예금</option>
          <option value="saving">적금</option>
          <option value="loan">대출</option>
        </select>
      </div>

      <button @click="getRecommendations" class="btn btn-primary">
        <i class="bi bi-search"></i> 맞춤 추천 받기
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p>AI가 최적의 상품을 분석 중입니다...</p>
    </div>

    <div v-if="error" class="error-message alert alert-danger">
      {{ error }}
    </div>

    <div v-if="recommendations" class="recommendations-results">
      <div class="user-info card">
        <div class="card-body">
          <h5 class="card-title">고객 정보</h5>
          <div class="row">
            <div class="col-md-4">
              <div class="info-item">
                <span class="info-label">월 소득</span>
                <span class="info-value">{{
                  userInfo.salary ? formatCurrency(userInfo.salary) : '정보 없음'
                }}</span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="info-item">
                <span class="info-label">현재 자산</span>
                <span class="info-value">{{
                  userInfo.money ? formatCurrency(userInfo.money) : '정보 없음'
                }}</span>
              </div>
            </div>
            <div class="col-md-4">
              <div class="info-item">
                <span class="info-label">원하는 기간</span>
                <span class="info-value">{{ userInfo.period }}개월</span>
              </div>
            </div>
          </div>
          <div class="mt-2 update-profile" v-if="!userInfo.salary || !userInfo.money">
            <small class="text-warning">
              <i class="bi bi-exclamation-triangle"></i>
              더 정확한 추천을 위해 <router-link to="/profile">프로필</router-link>에서 소득과 자산
              정보를 입력하세요.
            </small>
          </div>
        </div>
      </div>

      <div class="ai-result card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0"><i class="bi bi-robot"></i> AI 추천 결과</h5>
          <span class="badge bg-info">분석한 상품 수: {{ productCount }}</span>
        </div>
        <div class="card-body">
          <div class="recommendations-content">
            <!-- <pre class="recommendations-text">{{ recommendations }}</pre> -->
            <pre class="recommendations-text" v-html="recommendations"></pre>
          </div>
        </div>
      </div>

      <div class="disclaimer alert alert-secondary mt-3">
        <p class="mb-0">
          <strong>참고사항:</strong> AI의 추천은 참고용이며, 실제 금융 결정은 전문가와 상담 후
          신중하게 결정하시기 바랍니다.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import productsService from '@/services/products'

export default {
  name: 'AIRecommendationsView',
  setup() {
    const userStore = useUserStore()
    const period = ref(12)
    const productType = ref('all')
    const recommendations = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const userInfo = ref({
      salary: 0,
      money: 0,
      period: 12,
    })
    const productCount = ref(0)

    // Get user info on component mount
    onMounted(() => {
      if (userStore.user) {
        userInfo.value.salary = userStore.user.salary || 0
        userInfo.value.money = userStore.user.money || 0
      }
    })

    const getRecommendations = async () => {
      loading.value = true
      error.value = null
      recommendations.value = null

      try {
        const response = await productsService.getAIRecommendations({
          period: period.value,
          type: productType.value,
        })

        if (response.data && response.data.status === 'success') {
          recommendations.value = response.data.recommendations
          userInfo.value = response.data.user_info
          productCount.value = response.data.product_count
        } else {
          error.value = '추천을 불러오는 데 실패했습니다.'
        }
      } catch (err) {
        console.error('AI 추천 오류:', err)
        error.value =
          err.response?.data?.message || '서버 오류가 발생했습니다. 잠시 후 다시 시도하세요.'
      } finally {
        loading.value = false
      }
    }

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        maximumFractionDigits: 0,
      }).format(value)
    }

    return {
      period,
      productType,
      recommendations,
      loading,
      error,
      userInfo,
      productCount,
      getRecommendations,
      formatCurrency,
    }
  },
}
</script>

<style scoped>
.ai-recommendations-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.header {
  margin-bottom: 2rem;
  text-align: center;
}

.subtitle {
  color: #6c757d;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  align-items: flex-end;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control,
.form-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.btn-primary {
  padding: 0.5rem 1.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
}

.recommendations-results {
  margin-top: 2rem;
}

.card {
  margin-bottom: 1.5rem;
  border: 1px solid var(--card-border);
  border-radius: var(--card-border-radius);
  background-color: var(--card-bg);
  box-shadow: var(--card-shadow);
}

.card-header {
  background-color: var(--background-secondary);
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--card-border);
  border-top-left-radius: var(--card-border-radius);
  border-top-right-radius: var(--card-border-radius);
}

.card-header h5 {
  color: var(--text-primary);
}

.card-body {
  padding: var(--spacing-md);
}

.user-info .info-item {
  margin-bottom: 1rem;
}

.user-info .info-label {
  display: block;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.user-info .info-value {
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.update-profile small a {
  color: var(--accent-color);
  text-decoration: none;
}
.update-profile small a:hover {
  text-decoration: underline;
}

.ai-result .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-result .card-header h5 {
  margin-bottom: 0;
}

.recommendations-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: var(--font-body);
  color: var(--text-primary);
  background-color: var(--card-bg);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color-light);
  line-height: 1.7;
  font-size: var(--font-size-md);
}

.disclaimer {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background-color: var(--background-secondary);
  border-color: var(--border-color);
}

.error-message {
  color: var(--button-danger-text);
  background-color: var(--button-danger-bg);
  border-color: var(--button-danger-hover-bg);
}
</style>
