<template>
  <div class="product-detail-container">
    <!-- Loading and error states -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>상품 정보를 불러오는 중입니다...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>오류가 발생했습니다</h3>
      <p>{{ error }}</p>
      <button @click="loadProductDetails" class="retry-button">다시 시도</button>
    </div>

    <!-- Product details -->
    <template v-else-if="product">
      <!-- Header with navigation and actions -->
      <div class="page-header">
        <button @click="goBack" class="back-button">
          <i class="fas fa-arrow-left"></i>
          <span>상품 목록으로</span>
        </button>

        <div class="header-actions">
          <button @click="sharePage" class="share-button">
            <i class="fas fa-share-alt"></i>
          </button>
          <button
            @click="toggleFavorite"
            :class="['favorite-button', { 'is-favorite': isFavorite }]"
          >
            <i :class="isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
            <span>{{ isFavorite ? '즐겨찾기 해제' : '즐겨찾기 추가' }}</span>
          </button>
        </div>
      </div>

      <!-- Product header card -->
      <div class="product-header-card">
        <div class="product-bank-logo">
          <img :src="getBankLogo(product.kor_co_nm)" :alt="product.kor_co_nm + ' 로고'" />
        </div>

        <div class="product-main-info">
          <div class="product-badges">
            <span class="product-type-badge">{{ getProductTypeName(product.product_type) }}</span>
            <span v-if="isNew" class="new-badge">신규</span>
          </div>

          <h1 class="product-name">{{ product.fin_prdt_nm }}</h1>

          <div class="product-bank">
            <span>{{ product.kor_co_nm }}</span>
            <button @click="visitBankWebsite" class="visit-bank-button">
              홈페이지 방문 <i class="fas fa-external-link-alt"></i>
            </button>
          </div>

          <div class="product-join-methods">
            <JoinMethods :join_way="product.join_way" />
          </div>
        </div>

        <!-- Rate highlight section based on product type -->
        <div class="product-rate-highlight">
          <template v-if="product.product_type === 'deposit' || product.product_type === 'saving'">
            <RateDisplay
              :rate="product.max_rate"
              :type="product.product_type"
              rateType="max"
              :highlight="true"
            />
            <div class="rate-info">* 최고 우대금리 기준</div>
          </template>

          <template v-else-if="product.product_type === 'loan'">
            <RateDisplay :rate="product.min_rate" type="loan" rateType="min" :highlight="true" />
            <div class="rate-info">* 최저 금리 기준</div>
          </template>
        </div>
      </div>

      <!-- Product details tabs -->
      <div class="product-tabs">
        <button
          :class="['tab-button', { active: activeTab === 'details' }]"
          @click="activeTab = 'details'"
        >
          상품 정보
        </button>
        <button
          :class="['tab-button', { active: activeTab === 'rates' }]"
          @click="activeTab = 'rates'"
        >
          금리 정보
        </button>
        <button
          :class="['tab-button', { active: activeTab === 'conditions' }]"
          @click="activeTab = 'conditions'"
        >
          가입 조건
        </button>
      </div>

      <!-- Tab content -->
      <div class="tab-content">
        <!-- Details tab -->
        <div v-if="activeTab === 'details'" class="tab-panel">
          <div class="info-section">
            <h3 class="section-title">기본 정보</h3>

            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">상품 코드</div>
                <div class="info-value">{{ product.fin_prdt_cd }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">출시일</div>
                <div class="info-value">{{ formatDate(product.fin_prdt_launch_dt) }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">금융 회사</div>
                <div class="info-value">{{ product.kor_co_nm }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">가입 방법</div>
                <div class="info-value">
                  <JoinMethods :joinWay="product.join_way" :showLabel="false" />
                </div>
              </div>
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">상품 설명</h3>
            <div class="product-description">
              {{ product.etc_note || '상세 설명이 제공되지 않은 상품입니다.' }}
            </div>
          </div>

          <!-- Product type-specific information -->
          <div v-if="product.product_type === 'saving'" class="info-section">
            <h3 class="section-title">적금 정보</h3>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">적금 기간</div>
                <div class="info-value">
                  {{ product.save_trm ? product.save_trm + '개월' : '자유 적금' }}
                </div>
              </div>

              <div class="info-item">
                <div class="info-label">적립 유형</div>
                <div class="info-value">{{ getSavingType(product) }}</div>
              </div>
            </div>
          </div>

          <div v-if="product.product_type === 'loan'" class="info-section">
            <h3 class="section-title">대출 정보</h3>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">대출 유형</div>
                <div class="info-value">{{ getLoanTypeName(product) }}</div>
              </div>

              <div v-if="product.loan_lmt" class="info-item">
                <div class="info-label">대출 한도</div>
                <div class="info-value">{{ formatCurrency(product.loan_lmt) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Rates tab -->
        <div v-if="activeTab === 'rates'" class="tab-panel">
          <template v-if="product.product_type === 'deposit' || product.product_type === 'saving'">
            <div class="info-section">
              <h3 class="section-title">금리 정보</h3>

              <div class="rates-grid">
                <div class="rate-card">
                  <div class="rate-card-title">기본금리</div>
                  <RateDisplay
                    :rate="product.base_rate"
                    :type="product.product_type"
                    rateType="base"
                  />
                </div>

                <div class="rate-card">
                  <div class="rate-card-title">최고금리</div>
                  <RateDisplay
                    :rate="product.max_rate"
                    :type="product.product_type"
                    rateType="max"
                    :highlight="true"
                  />
                </div>
              </div>

              <div class="info-item wide">
                <div class="info-label">이자 지급 방식</div>
                <div class="info-value">
                  {{ getInterestPaymentMethod(product.intr_rate_type_nm) }}
                </div>
              </div>

              <div class="disclaimer">
                * 실제 적용금리는 고객의 신용도, 대출기간, 대출금액 등에 따라 달라질 수 있습니다. *
                금리 우대조건은 은행 홈페이지에서 확인하시기 바랍니다.
              </div>
            </div>
          </template>

          <template v-else-if="product.product_type === 'loan'">
            <div class="info-section">
              <h3 class="section-title">대출 금리 정보</h3>

              <div class="rates-grid">
                <div class="rate-card">
                  <div class="rate-card-title">최저금리</div>
                  <RateDisplay
                    :rate="product.min_rate"
                    type="loan"
                    rateType="min"
                    :highlight="true"
                  />
                </div>

                <div class="rate-card">
                  <div class="rate-card-title">최고금리</div>
                  <RateDisplay :rate="product.max_rate" type="loan" rateType="max" />
                </div>
              </div>

              <div class="info-item wide">
                <div class="info-label">금리 유형</div>
                <div class="info-value">{{ getLoanRateType(product.lend_rate_type) }}</div>
              </div>

              <div class="disclaimer">
                * 실제 적용금리는 고객의 신용도, 대출기간, 대출금액 등에 따라 달라질 수 있습니다. *
                대출금리 우대조건은 은행 홈페이지에서 확인하시기 바랍니다.
              </div>
            </div>
          </template>
        </div>

        <!-- Conditions tab -->
        <div v-if="activeTab === 'conditions'" class="tab-panel">
          <div class="info-section">
            <h3 class="section-title">가입 조건</h3>

            <div class="conditions-list">
              <div class="condition-item">
                <i class="fas fa-check-circle"></i>
                <span>가입 가능 연령: 만 19세 이상</span>
              </div>

              <div class="condition-item">
                <i class="fas fa-check-circle"></i>
                <span>실명의 개인 (법인 및 임의단체 제외)</span>
              </div>

              <div
                v-if="product.product_type === 'deposit' || product.product_type === 'saving'"
                class="condition-item"
              >
                <i class="fas fa-check-circle"></i>
                <span
                  >가입 기간:
                  {{ product.save_trm ? product.save_trm + '개월' : '자유 입출금식' }}</span
                >
              </div>

              <div v-if="product.product_type === 'loan'" class="condition-item">
                <i class="fas fa-check-circle"></i>
                <span>대출 유형: {{ getLoanTypeName(product) }}</span>
              </div>
            </div>

            <div class="requirement-note">
              * 자세한 가입 요건은 해당 금융회사에 문의하시기 바랍니다.
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">가입 방법</h3>

            <div class="join-methods-detailed">
              <template v-if="hasJoinWay('영업점')">
                <div class="join-method-item">
                  <div class="join-method-icon">
                    <i class="fas fa-building"></i>
                  </div>
                  <div class="join-method-content">
                    <h4>영업점 방문</h4>
                    <p>가까운 {{ product.kor_co_nm }} 지점을 방문하여 가입하실 수 있습니다.</p>
                  </div>
                </div>
              </template>

              <template v-if="hasJoinWay('인터넷')">
                <div class="join-method-item">
                  <div class="join-method-icon">
                    <i class="fas fa-laptop"></i>
                  </div>
                  <div class="join-method-content">
                    <h4>인터넷뱅킹</h4>
                    <p>
                      {{ product.kor_co_nm }} 인터넷뱅킹을 통해 온라인으로 가입하실 수 있습니다.
                    </p>
                  </div>
                </div>
              </template>

              <template v-if="hasJoinWay('스마트폰')">
                <div class="join-method-item">
                  <div class="join-method-icon">
                    <i class="fas fa-phone"></i>
                  </div>
                  <div class="join-method-content">
                    <h4>전화뱅킹</h4>
                    <p>{{ product.kor_co_nm }} 고객센터에 전화하여 가입하실 수 있습니다.</p>
                  </div>
                </div>
              </template>

              <template v-if="hasJoinWay('전화(텔레뱅킹)')">
                <div class="join-method-item">
                  <div class="join-method-icon">
                    <i class="fas fa-mobile-alt"></i>
                  </div>
                  <div class="join-method-content">
                    <h4>모바일뱅킹</h4>
                    <p>{{ product.kor_co_nm }} 모바일 앱을 통해 편리하게 가입하실 수 있습니다.</p>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA section -->
      <div class="cta-section">
        <button @click="visitBankWebsite" class="cta-button primary">
          <i class="fas fa-external-link-alt"></i> {{ product.kor_co_nm }} 바로가기
        </button>
        <button @click="toggleFavorite" class="cta-button secondary">
          <i :class="isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
          {{ isFavorite ? '즐겨찾기 해제' : '즐겨찾기 추가' }}
        </button>
      </div>

      <!-- Related products section (if available) -->
      <div v-if="relatedProducts.length > 0" class="related-products">
        <h3 class="section-title">관련 상품</h3>
        <div class="related-products-grid">
          <ProductCard
            v-for="relatedProduct in relatedProducts"
            :key="relatedProduct.id"
            :product="relatedProduct"
            :isFavorite="isProductInFavorites(relatedProduct.id)"
            @favorite-toggle="toggleRelatedFavorite"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import productsService from '@/services/products'
import RateDisplay from '@/components/products/RateDisplay.vue'
import JoinMethods from '@/components/products/JoinMethods.vue'
import ProductCard from '@/components/products/ProductCard.vue'

export default {
  name: 'ProductDetailView',
  components: {
    RateDisplay,
    JoinMethods,
    ProductCard,
  },
  setup() {
    // Router and route
    const route = useRoute()
    const router = useRouter()

    // Route params
    const productId = computed(() => route.params.id)
    const productType = computed(() => route.query.type || 'all')

    // State
    const product = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const isFavorite = ref(false)
    const activeTab = ref('details')
    const relatedProducts = ref([])
    const favorites = ref([])

    // Computed props
    const isNew = computed(() => {
      if (!product.value || !product.value.fin_prdt_launch_dt) return false

      const launchDate = new Date(
        product.value.fin_prdt_launch_dt.substring(0, 4),
        product.value.fin_prdt_launch_dt.substring(4, 6) - 1,
        product.value.fin_prdt_launch_dt.substring(6, 8),
      )

      const threeMonthsAgo = new Date()
      threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3)

      return launchDate >= threeMonthsAgo
    })

    // Load product details
    const loadProductDetails = async () => {
      loading.value = true
      error.value = null

      try {
        // Load product based on type
        switch (productType.value) {
          case 'deposit':
            product.value = await productsService.getDepositProduct(productId.value)
            break
          case 'saving':
            product.value = await productsService.getSavingProduct(productId.value)
            break
          case 'loan':
            product.value = await productsService.getLoanProduct(productId.value)
            break
          default:
            product.value = await productsService.getFinancialProduct(productId.value)
            break
        }

        // Check if product is in favorites
        checkIfFavorite()

        // Load related products
        loadRelatedProducts()
      } catch (err) {
        console.error('Error loading product details:', err)
        error.value = '상품 정보를 불러오는데 실패했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
      }
    }

    // Load related products
    const loadRelatedProducts = async () => {
      if (!product.value) return

      try {
        // Load products from same bank and same type
        let products = []

        switch (product.value.product_type) {
          case 'deposit':
            products = await productsService.getDepositProducts({
              bank: product.value.kor_co_nm,
            })
            break
          case 'saving':
            products = await productsService.getSavingProducts({
              bank: product.value.kor_co_nm,
            })
            break
          case 'loan':
            products = await productsService.getLoanProducts({
              bank: product.value.kor_co_nm,
            })
            break
        }

        // Filter out current product and limit to 3
        relatedProducts.value = products
          .filter((p) => p.id !== parseInt(productId.value))
          .slice(0, 3)
      } catch (err) {
        console.error('Error loading related products:', err)
      }
    }

    // Check if product is in user's favorites
    const checkIfFavorite = async () => {
      try {
        favorites.value = await productsService.getUserFavorites()
        isFavorite.value = favorites.value.some((fav) => {
          return fav.product === productId.value
        })
      } catch (err) {
        console.error('Error checking favorites:', err)
      }
    }

    // Check if a product is in favorites
    const isProductInFavorites = (id) => {
      return favorites.value.some((fav) => fav.product_id === id)
    }

    // Toggle favorite status
    const toggleFavorite = async () => {
      try {
        if (isFavorite.value) {
          await productsService.removeFromFavorites(productId.value)
        } else {
          await productsService.addToFavorites(productId.value)
        }
        isFavorite.value = !isFavorite.value
      } catch (err) {
        console.error('Error toggling favorite:', err)
      }
    }

    // Toggle favorite for related product
    const toggleRelatedFavorite = async (productId) => {
      try {
        if (isProductInFavorites(productId)) {
          await productsService.removeFromFavorites(productId)
        } else {
          await productsService.addToFavorites(productId)
        }

        // Refresh favorites
        await checkIfFavorite()
      } catch (err) {
        console.error('Error toggling related favorite:', err)
      }
    }

    // Format interest rate for display
    const formatRate = (rate) => {
      if (!rate) return '0.00'
      return parseFloat(rate).toFixed(2)
    }

    // Format date (YYYYMMDD to YYYY-MM-DD)
    const formatDate = (dateStr) => {
      if (!dateStr || dateStr.length !== 8) return '정보 없음'

      // Create Korean format date: YYYY년 MM월 DD일
      return `${dateStr.substring(0, 4)}년 ${dateStr.substring(4, 6)}월 ${dateStr.substring(6, 8)}일`
    }

    // Format currency amount
    const formatCurrency = (amount) => {
      if (!amount) return '한도 변동'
      return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        maximumFractionDigits: 0,
      }).format(amount)
    }

    // Check if product has specific join way
    const hasJoinWay = (code) => {
      console.log(product.value)
      if (!product.value || !product.value.join_way) return false
      return product.value.join_way.includes(code)
    }
    
    // Get product type name for display
    const getProductTypeName = (type) => {
      const types = {
        deposit: '예금 상품',
        saving: '적금 상품',
        loan: '대출 상품',
      }
      return types[type] || '금융 상품'
    }

    // Get interest payment method name
    const getInterestPaymentMethod = (method) => {
      if (!method) return '명시되지 않음'

      if (method.includes('단리')) return '단리'
      if (method.includes('복리')) return '복리'

      return method
    }

    // Get saving type name
    const getSavingType = (saving) => {
      console.log(saving)
      // Implementation would depend on what data is available
      // This is a placeholder
      return '정기적금'
    }

    // Get loan rate type name
    const getLoanRateType = (type) => {
      const types = {
        1: '고정금리',
        2: '변동금리',
        3: '혼합금리',
      }
      return types[type] || '명시되지 않음'
    }

    // Get loan type name
    const getLoanTypeName = (loan) => {
      if (loan.is_mortgage) return '주택담보대출'
      if (loan.is_credit) return '신용대출'
      return '일반대출'
    }

    // Go back to products list
    const goBack = () => {
      router.push({ name: 'Products' })
    }

    // Share the current page
    const sharePage = () => {
      if (navigator.share) {
        navigator
          .share({
            title: product.value ? product.value.fin_prdt_nm : '금융 상품 정보',
            text: `${product.value ? product.value.kor_co_nm + '의 ' + product.value.fin_prdt_nm : '금융 상품'} 정보를 확인해보세요!`,
            url: window.location.href,
          })
          .catch((err) => console.error('Error sharing:', err))
      } else {
        // Fallback - copy URL to clipboard
        navigator.clipboard
          .writeText(window.location.href)
          .then(() => alert('URL이 클립보드에 복사되었습니다.'))
          .catch((err) => console.error('Error copying URL:', err))
      }
    }

    // Get bank logo
    const getBankLogo = (bankName) => {
      // This would be replaced with actual bank logo logic
      // For now, return a placeholder
      return `https://via.placeholder.com/50?text=${encodeURIComponent(bankName.charAt(0))}`
    }

    // Visit bank website
    const visitBankWebsite = () => {
      if (!product.value || !product.value.kor_co_nm) return

      // Simple mapping of bank names to websites
      const bankWebsites = {
        국민은행: 'https://www.kbstar.com',
        신한은행: 'https://www.shinhan.com',
        우리은행: 'https://www.wooribank.com',
        하나은행: 'https://www.kebhana.com',
        농협은행: 'https://www.nonghyup.com',
        기업은행: 'https://www.ibk.co.kr',
        산업은행: 'https://www.kdb.co.kr',
        새마을금고: 'https://www.kfcc.co.kr',
        수협은행: 'https://www.suhyup-bank.com',
        카카오뱅크: 'https://www.kakaobank.com',
        토스뱅크: 'https://www.tossbank.com',
        케이뱅크: 'https://www.kbanknow.com',
      }

      // Find exact or partial match
      const bankName = product.value.kor_co_nm
      let website = null

      // Try exact match first
      if (bankWebsites[bankName]) {
        website = bankWebsites[bankName]
      } else {
        // Try partial match
        for (const [bank, url] of Object.entries(bankWebsites)) {
          if (bankName.includes(bank)) {
            website = url
            break
          }
        }
      }

      // Open website or search
      if (website) {
        window.open(website, '_blank')
      } else {
        // If no match, search on Naver
        const searchQuery = encodeURIComponent(`${bankName} 공식 홈페이지`)
        window.open(`https://search.naver.com/search.naver?query=${searchQuery}`, '_blank')
      }
    }

    // Load data on component mount
    onMounted(() => {
      loadProductDetails()
    })

    return {
      product,
      loading,
      error,
      isFavorite,
      activeTab,
      relatedProducts,
      isNew,
      toggleFavorite,
      formatRate,
      formatDate,
      formatCurrency,
      hasJoinWay,
      getProductTypeName,
      getInterestPaymentMethod,
      getSavingType,
      getLoanRateType,
      getLoanTypeName,
      goBack,
      sharePage,
      visitBankWebsite,
      getBankLogo,
      isProductInFavorites,
      toggleRelatedFavorite,
      loadProductDetails,
    }
  },
}
</script>

<style scoped>
.product-detail-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  font-family: var(--font-body);
  color: var(--color-text);
  background: linear-gradient(135deg, var(--color-background-start) 0%, var(--color-background-end) 100%);
  min-height: calc(100vh - 160px);
}

/* Loading animation */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  color: var(--color-text);
}

.loading-spinner {
  display: inline-block;
  width: 60px;
  height: 60px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error container */
.error-container {
  text-align: center;
  padding: 4rem 2.5rem;
  background: rgba(214, 48, 49, 0.05);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  color: var(--color-error);
  margin: 2rem auto;
  max-width: 600px;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
}

.retry-button {
  margin-top: 2rem;
  padding: 0.75rem 2rem;
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.retry-button::before {
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

.retry-button:hover {
  background: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.retry-button:hover::before {
  left: 100%;
}

.retry-button:active {
  transform: translateY(-1px);
}

/* Header navigation */
.page-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  align-items: center;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--color-text);
  background: var(--color-white);
  border: 1px solid var(--color-secondary);
  padding: 0.6rem 1.2rem;
  border-radius: 50px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.back-button:hover {
  background: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.share-button,
.favorite-button {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: var(--color-white);
  border: 1px solid var(--color-secondary);
  border-radius: 50px;
  padding: 0.6rem 1.2rem;
  font-size: var(--font-size-sm);
  font-weight: 500;
  font-family: var(--font-body);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.share-button:hover,
.favorite-button:hover {
  background: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.favorite-button.is-favorite {
  background: rgba(var(--color-primary-rgb), 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.favorite-button.is-favorite:hover {
  background: rgba(var(--color-primary-rgb), 0.15);
}

/* Product header card */
.product-header-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 2.5rem;
  padding: 2.5rem;
  background: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  margin-bottom: 2.5rem;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.product-header-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
}

.product-bank-logo {
  width: 75px;
  height: 75px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-white);
  border-radius: 50%;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-secondary);
  padding: 0.5rem;
}

.product-bank-logo img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.product-main-info {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.product-badges {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.product-type-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  font-size: var(--font-size-xs);
  border-radius: 50px;
  background: var(--color-secondary);
  color: var(--color-text);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.new-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  font-size: var(--font-size-xs);
  border-radius: 50px;
  background: rgba(var(--color-accent-rgb), 0.1);
  color: var(--color-accent);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.product-name {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-accent);
  font-family: var(--font-heading);
}

.product-bank {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.visit-bank-button {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  font-size: var(--font-size-xs);
  color: var(--color-text);
  background: var(--color-secondary);
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.visit-bank-button:hover {
  background: var(--color-secondary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.product-join-methods {
  margin-top: 0.75rem;
}

.product-rate-highlight {
  text-align: center;
  padding: 1.5rem;
  background: rgba(var(--color-primary-rgb), 0.05);
  border-radius: 12px;
  border-left: 4px solid var(--color-primary);
  min-width: 180px;
}

.rate-info {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  margin-top: 0.75rem;
}

/* Tabs */
.product-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid var(--color-secondary);
  margin-bottom: 2.5rem;
}

.tab-button {
  padding: 1rem 1.75rem;
  border: none;
  background: none;
  font-size: var(--font-size-base);
  font-family: var(--font-body);
  font-weight: 500;
  color: var(--color-text-light);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-normal);
  margin-bottom: -2px;
}

.tab-button:hover {
  color: var(--color-text);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

/* Tab content styles */
.tab-panel {
  margin-bottom: 2.5rem;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.info-section {
  margin-bottom: 2.5rem;
  background: var(--color-white);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: var(--shadow-md);
}

.section-title {
  margin: 0 0 1.5rem 0;
  font-size: var(--font-size-lg);
  color: var(--color-accent);
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-secondary);
  font-family: var(--font-heading);
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 60px;
  height: 3px;
  background: var(--color-primary);
  border-radius: 3px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.75rem;
}

.info-item {
  margin-bottom: 1.2rem;
}

.info-item.wide {
  grid-column: 1 / -1;
}

.info-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  margin-bottom: 0.4rem;
}

.info-value {
  font-size: var(--font-size-base);
  color: var(--color-text);
  font-weight: 500;
}

.product-description {
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-line;
  font-size: var(--font-size-base);
}

.disclaimer {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  margin-top: 1.75rem;
  padding: 1.2rem;
  background: var(--color-secondary);
  border-radius: 8px;
  line-height: 1.6;
  white-space: pre-line;
}

/* Rates tab styles */
.rates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.75rem;
  margin-bottom: 1.75rem;
}

.rate-card {
  padding: 1.75rem;
  background: var(--color-white);
  border-radius: 12px;
  text-align: center;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
  border: 1px solid var(--color-secondary);
}

.rate-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.rate-card-title {
  margin-bottom: 0.75rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  font-weight: 500;
}

/* Conditions tab styles */
.join-methods-detailed {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.75rem;
}

.join-method-item {
  display: flex;
  gap: 1.25rem;
  padding: 1.75rem;
  background: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  align-items: center;
  transition: all var(--transition-normal);
  border: 1px solid var(--color-secondary);
}

.join-method-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.join-method-icon {
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-secondary);
  border-radius: 50%;
  color: var(--color-text);
  font-size: 1.35rem;
  transition: all var(--transition-normal);
}

.join-method-item:hover .join-method-icon {
  background: var(--color-primary);
  color: var(--color-white);
  transform: scale(1.1);
}

.join-method-content h4 {
  margin: 0 0 0.6rem 0;
  color: var(--color-accent);
  font-family: var(--font-heading);
}

.join-method-content p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  line-height: 1.5;
}

/* Conditions tab styles */
.conditions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.condition-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--color-secondary);
  border-radius: 8px;
  transition: all var(--transition-normal);
}

.condition-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  background: var(--color-white);
}

.condition-item i {
  color: var(--color-primary);
  font-size: 1.2rem;
}

.requirement-note {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  margin-top: 1.25rem;
  font-style: italic;
}

/* CTA section */
.cta-section {
  display: flex;
  gap: 1.5rem;
  margin: 3.5rem 0;
}

.cta-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.2rem 1.5rem;
  border-radius: 12px;
  font-size: var(--font-size-base);
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.cta-button::before {
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

.cta-button.primary {
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  box-shadow: var(--shadow-md);
}

.cta-button.primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.cta-button:hover::before {
  left: 100%;
}

.cta-button.secondary {
  background: var(--color-white);
  color: var(--color-text);
  border: 1px solid var(--color-secondary);
  box-shadow: var(--shadow-sm);
}

.cta-button.secondary:hover {
  background: var(--color-secondary);
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

/* Related products */
.related-products {
  margin-top: 3.5rem;
  padding: 2.5rem;
  background: var(--color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
}

.related-products .section-title {
  text-align: center;
  margin-bottom: 2rem;
}

.related-products .section-title::after {
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
}

.related-products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

/* Dark mode styles */
:global(.dark-mode) .product-header-card,
:global(.dark-mode) .info-section,
:global(.dark-mode) .rate-card,
:global(.dark-mode) .join-method-item,
:global(.dark-mode) .related-products {
  background-color: #2D2D2D;
}

:global(.dark-mode) .back-button,
:global(.dark-mode) .share-button,
:global(.dark-mode) .favorite-button,
:global(.dark-mode) .cta-button.secondary {
  background-color: #333333;
  border-color: #444444;
}

:global(.dark-mode) .back-button:hover,
:global(.dark-mode) .share-button:hover,
:global(.dark-mode) .favorite-button:hover,
:global(.dark-mode) .cta-button.secondary:hover {
  background-color: #3D3D3D;
}

:global(.dark-mode) .product-bank-logo,
:global(.dark-mode) .condition-item:hover {
  background-color: #333333;
}

:global(.dark-mode) .condition-item,
:global(.dark-mode) .join-method-icon,
:global(.dark-mode) .disclaimer {
  background-color: #333333;
}

/* Responsive styles */
@media (max-width: 1024px) {
  .product-header-card {
    grid-template-columns: auto 1fr;
    gap: 2rem;
  }
  
  .product-rate-highlight {
    grid-column: span 2;
    margin-top: 1.5rem;
  }
}

@media (max-width: 768px) {
  .product-detail-container {
    padding: 1.5rem 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .product-header-card {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .product-bank-logo {
    margin: 0 auto;
  }

  .product-main-info {
    text-align: center;
  }

  .product-bank {
    flex-direction: column;
    gap: 0.75rem;
    align-items: center;
  }

  .product-rate-highlight {
    justify-self: center;
    width: 100%;
  }

  .product-tabs {
    overflow-x: auto;
    padding-bottom: 5px;
  }
  
  .tab-button {
    padding: 0.75rem 1.25rem;
    white-space: nowrap;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .rates-grid {
    grid-template-columns: 1fr;
  }

  .cta-section {
    flex-direction: column;
  }

  .join-methods-detailed {
    grid-template-columns: 1fr;
  }
  
  .related-products {
    padding: 1.5rem;
  }
  
  .related-products-grid {
    grid-template-columns: 1fr;
  }
}
</style>
