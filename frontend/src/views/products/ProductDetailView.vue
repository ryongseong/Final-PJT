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
          <button @click="sharePage" class="share-button">공유하기</button>
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
            <p>가입 방법: {{ product.join_way.join(', ') }}</p>
          </div>
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
                  <div class="join-badges">
                    <span v-for="way in product.join_way" :key="way" class="join-badge">
                      {{ way }}
                    </span>
                  </div>
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
          <!-- Rate Information Section -->
          <div class="product-info-section">
            <h3>금리 정보</h3>

            <!-- Max/Standard Rate Display -->
            <div class="rate-display">
              <!-- Max Rate (for savings) or Standard Rate (for loans) -->
              <div
                v-if="
                  product.product_type === 'SAVINGS' ||
                  product.product_type === 'DEPOSIT' ||
                  product.product_type === 'saving' ||
                  product.product_type === 'deposit' ||
                  determineProductType(product) === 'deposit' ||
                  determineProductType(product) === 'saving'
                "
              >
                <div
                  :class="[
                    'rate-value',
                    getRateClass(product.product_type || determineProductType(product), true),
                  ]"
                >
                  {{ formatRate(product.max_rate || product.intr_rate2 || product.intr_rate) }}%
                </div>
                <div class="rate-label">최고 우대금리</div>
              </div>
              <div v-else>
                <div
                  :class="[
                    'rate-value',
                    getRateClass(product.product_type || determineProductType(product), true),
                  ]"
                >
                  {{ formatRate(product.intr_rate || product.intr_rate2) }}%
                </div>
                <div class="rate-label">기준금리</div>
              </div>

              <!-- Base Rate (for savings) -->
              <div
                v-if="
                  (['SAVINGS', 'DEPOSIT', 'saving', 'deposit'].includes(product.product_type) ||
                    determineProductType(product) === 'deposit' ||
                    determineProductType(product) === 'saving') &&
                  (product.intr_rate || product.intr_rate2)
                "
              >
                <div
                  :class="[
                    'rate-value',
                    getRateClass(product.product_type || determineProductType(product)),
                  ]"
                >
                  {{ formatRate(product.intr_rate || product.intr_rate2) }}%
                </div>
                <div class="rate-label">기본금리</div>
              </div>

              <!-- Min Rate (for loans) -->
              <div v-if="['LOAN', 'loan'].includes(product.product_type) && product.min_rate">
                <div :class="['rate-value', getRateClass(product.product_type)]">
                  {{ formatRate(product.min_rate) }}%
                </div>
                <div class="rate-label">최저금리</div>
              </div>
            </div>

            <!-- Interest Rate Chart for deposit and saving products -->
            <div
              v-if="
                (product.product_type &&
                  ['deposit', 'saving', 'DEPOSIT', 'SAVINGS'].includes(
                    product.product_type.toLowerCase(),
                  )) ||
                product.intr_rate_type_nm ||
                product.save_trm ||
                (product.interest && !product.loan_rate) ||
                product.rsrv_type ||
                product.rsrv_type_nm
              "
              class="interest-rate-chart-section"
            >
              <h3 class="section-subtitle">기간별 금리 정보</h3>

              <div v-if="requirementOptions.length > 0">
                <InterestRateChart
                  :requirements="requirementOptions"
                  :productType="product.product_type || determineProductType(product)"
                />
              </div>

              <div v-else class="no-chart-data">
                <p>현재 기간별 금리 데이터를 불러올 수 없습니다.</p>
                <button @click="fetchRequirementOptions" class="refresh-button">
                  금리 데이터 불러오기
                </button>
                <!-- Create emergency fallback data -->
                <button
                  v-if="requirementOptions.length === 0"
                  @click="createFallbackData"
                  class="fallback-button"
                >
                  예시 데이터로 보기
                </button>
              </div>
            </div>

            <!-- Rate Details -->
            <div class="rate-details">
              <div v-if="product.intr_rate_type_nm" class="detail-item">
                <span class="detail-label">금리유형:</span>
                <span class="detail-value">{{ product.intr_rate_type_nm }}</span>
              </div>
              <div v-if="product.rsrv_type_nm" class="detail-item">
                <span class="detail-label">적립유형:</span>
                <span class="detail-value">{{
                  product.rsrv_type_nm || getSavingType(product)
                }}</span>
              </div>
              <div v-if="['SAVINGS', 'saving'].includes(product.product_type)" class="detail-item">
                <span class="detail-label">저축방식:</span>
                <span class="detail-value">{{ getSavingType(product) }}</span>
              </div>
            </div>
          </div>
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
              자세한 가입 요건은 해당 금융회사에 문의하시기 바랍니다.
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

              <template v-if="hasJoinWay('전화(텔레뱅킹)')">
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

              <template v-if="hasJoinWay('스마트폰')">
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
import ProductCard from '@/components/products/ProductCard.vue'
import InterestRateChart from '@/components/products/InterestRateChart.vue'

export default {
  name: 'ProductDetailView',
  components: {
    ProductCard,
    InterestRateChart,
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
    const requirementOptions = ref([])

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

    // Process requirements data from response
    const processRequirements = async (productData, type) => {
      if (!productData) return

      try {
        // Check if requirements data is already included in the response
        if (productData.requirements) {
          console.log('Requirements found in initial product response:', productData.requirements)
          requirementOptions.value = Array.isArray(productData.requirements)
            ? productData.requirements
            : [productData.requirements]
          return
        }

        // If not, try to fetch it separately for deposit and savings products
        if (['deposit', 'saving', 'DEPOSIT', 'SAVINGS'].includes(type)) {
          const normalizedType = type.toLowerCase()
          const detailedData = await productsService.getProductByTypeAndId(
            normalizedType,
            productId.value,
          )

          if (detailedData && detailedData.requirements) {
            requirementOptions.value = Array.isArray(detailedData.requirements)
              ? detailedData.requirements
              : [detailedData.requirements]
            console.log('Requirement options loaded from direct call:', requirementOptions.value)
          }
        }
      } catch (reqError) {
        console.warn('Could not fetch requirement options:', reqError)
      }
    }

    // Load product details
    const loadProductDetails = async () => {
      loading.value = true
      error.value = null
      requirementOptions.value = [] // Clear previous requirements data

      try {
        let productData = null

        // Load product based on type
        switch (productType.value) {
          case 'deposit':
            productData = await productsService.getDepositProduct(productId.value)
            break
          case 'saving':
            productData = await productsService.getSavingProduct(productId.value)
            break
          case 'loan':
            productData = await productsService.getLoanProduct(productId.value)
            break
          default:
            productData = await productsService.getFinancialProduct(productId.value)
            break
        }

        // Set product data
        product.value = productData

        // Process requirements data
        await processRequirements(productData, productType.value)

        // Check if product is in favorites
        checkIfFavorite()

        // Load related products
        loadRelatedProducts()

        console.log('Product details loaded:', product.value)
      } catch (err) {
        console.error('Error loading product details:', err)
        error.value = '상품 정보를 불러오는데 실패했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
        // 추가: requirementOptions가 비어있고, 예금/적금 상품인 경우 fallback 데이터 생성
        if (product.value && 
            (determineProductType(product.value) === 'deposit' || determineProductType(product.value) === 'saving') && 
            requirementOptions.value.length === 0) {
          console.log('loadProductDetails: No requirement options, attempting to create fallback data.');
          createFallbackData();
        }
      }
    }

    // Fetch product by id with enhanced data
    const fetchProduct = async (id) => {
      loading.value = true
      error.value = null
      requirementOptions.value = [] // Clear previous requirements data

      try {
        // First try the generic endpoint to get basic info
        const basicProduct = await productsService.getFinancialProduct(id)
        console.log('Basic product data:', basicProduct)
        // Safely log product type if it exists
        if (basicProduct.product_type) {
          console.log('Product type from basic data:', basicProduct.product_type)
        } else {
          console.log('Product type not found in basic data')
        }

        product.value = basicProduct

        if (!basicProduct) {
          console.warn('No product data received')
          return
        }

        // Determine product type, with fallbacks
        let normalizedType

        if (basicProduct.product_type) {
          normalizedType = basicProduct.product_type.toLowerCase()
        } else {
          // Try to infer product type from other properties or API endpoint structure
          if (basicProduct.intr_rate_type_nm || basicProduct.save_trm || basicProduct.interest) {
            normalizedType = 'deposit'
          } else if (basicProduct.rsrv_type || basicProduct.rsrv_type_nm) {
            normalizedType = 'saving'
          } else if (basicProduct.loan_type || basicProduct.loan_rate) {
            normalizedType = 'loan'
          } else {
            // Try to infer from product name
            const productName = basicProduct.fin_prdt_nm || ''
            console.log('Trying to infer product type from name:', productName)

            if (productName.includes('예금') || productName.includes('정기')) {
              normalizedType = 'deposit'
              console.log('Inferred as deposit from name')
            } else if (productName.includes('적금')) {
              normalizedType = 'saving'
              console.log('Inferred as saving from name')
            } else if (productName.includes('대출') || productName.includes('론')) {
              normalizedType = 'loan'
              console.log('Inferred as loan from name')
            } else {
              // Default fallback - use generic endpoint
              normalizedType = 'deposit' // Changed from financial-product to deposit as safer default
              console.log('Could not infer type, using deposit as default')
            }
          }
          console.log('Inferred product type:', normalizedType)
        }

        // For deposit and savings products, use specific endpoints that include requirements
        let detailedProduct

        try {
          // Try to fetch detailed product data based on type
          if (normalizedType === 'deposit') {
            detailedProduct = await productsService.getDepositProduct(id)
          } else if (normalizedType === 'saving') {
            detailedProduct = await productsService.getSavingProduct(id)
          } else {
            // Use the more generic method for other types
            try {
              detailedProduct = await productsService.getProductByTypeAndId(normalizedType, id)
            } catch (innerError) {
              console.warn(
                `Failed to get product with type ${normalizedType}, trying fallback endpoints`,
                innerError,
              )

              // Try fallback endpoints if the first attempt fails
              try {
                detailedProduct = await productsService.getFinancialProduct(id)
              } catch (fallbackError) {
                console.error('All fallback attempts failed:', fallbackError)
              }
            }
          }

          if (detailedProduct) {
            // Merge the detailed product data with the basic product data
            product.value = {
              ...basicProduct,
              ...detailedProduct,
            }

            // Process requirements if available
            if (detailedProduct.requirements) {
              requirementOptions.value = Array.isArray(detailedProduct.requirements)
                ? detailedProduct.requirements
                : [detailedProduct.requirements]
              console.log(
                'Requirement options loaded from detailed product:',
                requirementOptions.value,
              )
            }

            // Log the final product object
            console.log('Final product object:', product.value)
          }

          // If we still don't have requirement options for deposit/saving products, try to fetch them
          if (
            (normalizedType === 'deposit' || normalizedType === 'saving') &&
            requirementOptions.value.length === 0
          ) {
            await fetchRequirementOptions()
          }

          // After loading product data, check favorites and load related products
          checkIfFavorite()
          loadRelatedProducts()
        } catch (detailError) {
          console.warn('Could not fetch detailed product info:', detailError)
        }
      } catch (err) {
        error.value = '상품 정보를 불러오는데 실패했습니다. 다시 시도해주세요.'
        console.error('Error loading product:', err)
      } finally {
        loading.value = false;
        // 추가: requirementOptions가 비어있고, 예금/적금 상품인 경우 fallback 데이터 생성
        if (product.value && 
            (determineProductType(product.value) === 'deposit' || determineProductType(product.value) === 'saving') && 
            requirementOptions.value.length === 0) {
            console.log('fetchProduct: No requirement options, attempting to create fallback data.');
            createFallbackData();
        }
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

      // Handle potential string or number inputs
      const numRate = typeof rate === 'string' ? parseFloat(rate) : rate

      // Check if conversion resulted in a valid number
      if (isNaN(numRate)) return '0.00'

      // Format with 2 decimal places
      return numRate.toFixed(2)
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

    // Get the savings type based on product data
    const getSavingType = (product) => {
      if (!product) return '정보 없음'

      // First check if rsrv_type_nm is available (best source)
      if (product.rsrv_type_nm) {
        return product.rsrv_type_nm
      }

      // Then check for rsrv_type
      if (product.rsrv_type) {
        if (product.rsrv_type === 1) return '자유적립식'
        if (product.rsrv_type === 2) return '정액적립식'
        if (typeof product.rsrv_type === 'string') return product.rsrv_type
        return `적립 유형: ${product.rsrv_type}`
      }

      // Next check based on product name patterns
      const name = product.fin_prdt_nm?.toLowerCase() || ''
      if (name.includes('자유')) return '자유적립식'
      if (name.includes('정액')) return '정액적립식'
      if (name.includes('정기')) return '정기적금'

      // Check based on etc_note if available
      const description = product.etc_note?.toLowerCase() || ''
      if (description.includes('자유적립')) return '자유적립식'
      if (description.includes('정액적립')) return '정액적립식'

      // Default fallback
      if (product.product_type === 'DEPOSIT') return '정기예금'
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
      const banks = [
        'SC제일은행',
        '광주은행',
        '국민은행',
        '기업은행',
        '농협',
        '대구은행',
        '부산은행',
        '새마을금고',
        '수협은행',
        '신한은행',
        '신협',
        '씨티뱅크',
        '우리은행',
        '하나은행',
        '아이엠',
        '전북은행',
      ]
      // bankName이 배열에 포함되는 은행명을 포함하면 해당 은행명으로 bankName을 변경
      const matched = banks.find((b) => bankName.includes(b))
      if (matched) bankName = matched

      return new URL(`/src/assets/${bankName}.png`, import.meta.url).href
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
        토스뱅크: 'https://www.tossbank.com',
        케이뱅크: 'https://www.kbanknow.com',
        카카오뱅크: 'https://www.kakaobank.com',
        SC제일은행: 'https://www.sc.co.kr',
        광주은행: 'https://www.kjbank.com',
        대구은행: 'https://www.dgb.co.kr',
        부산은행: 'https://www.busanbank.co.kr',
        신협: 'https://www.shinhyup.com',
        씨티뱅크: 'https://www.citibank.co.kr',
        아이엠뱅크: 'https://www.imbank.co.kr',
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

    // Determine rate CSS class based on product type
    const getRateClass = (type, highlight = false) => {
      const classes = []

      // Add highlight class if needed
      if (highlight) classes.push('highlight')

      // Add type-specific class
      if (type === 'LOAN' || type === 'loan') {
        classes.push('loan-rate')
      } else {
        classes.push('savings-rate')
      }

      return classes.join(' ')
    }

    // Helper function to determine product type from other fields
    const determineProductType = (productObj) => {
      if (!productObj) return 'deposit' // Default fallback

      // Try to infer product type from available properties
      if (
        productObj.intr_rate_type_nm ||
        productObj.save_trm ||
        (productObj.interest && !productObj.loan_rate)
      ) {
        return 'deposit'
      } else if (productObj.rsrv_type || productObj.rsrv_type_nm) {
        return 'saving'
      } else if (productObj.loan_type || productObj.loan_rate) {
        return 'loan'
      }

      // Try to infer from product name if properties don't help
      if (productObj.fin_prdt_nm) {
        const productName = productObj.fin_prdt_nm
        console.log('Determining product type from name:', productName)
        if (productName.includes('예금') || productName.includes('정기')) {
          console.log('Determined as deposit from name')
          return 'deposit'
        } else if (productName.includes('적금')) {
          console.log('Determined as saving from name')
          return 'saving'
        } else if (productName.includes('대출') || productName.includes('론')) {
          console.log('Determined as loan from name')
          return 'loan'
        }
      }

      // Default fallback
      return 'deposit'
    }

    // Load data on component mount
    onMounted(() => {
      // Get the product id from the route parameters
      const id = route.params.id

      if (id) {
        fetchProduct(id)
      } else {
        loadProductDetails()
      }
    })

    // Manually fetch requirement options
    const fetchRequirementOptions = async () => {
      if (!product.value) return

      const id = route.params.id

      // Determine product type with fallbacks if product_type is missing
      let type
      if (product.value.product_type) {
        type = product.value.product_type.toLowerCase()
      } else {
        // Try to infer product type from other properties
        if (product.value.intr_rate_type_nm || product.value.save_trm || product.value.interest) {
          type = 'deposit'
        } else if (product.value.rsrv_type || product.value.rsrv_type_nm) {
          type = 'saving'
        } else {
          type = determineProductType(product.value)
          if (type === 'deposit' || type === 'saving') {
            console.log('Determined product type using helper function:', type)
          } else {
            console.warn('Cannot determine product type for requirements')
            return
          }
        }
        console.log('Inferred product type for requirements:', type)
      }

      if (!['deposit', 'saving'].includes(type)) {
        console.warn(`Product type ${type} doesn't support interest rate requirements`)
        return
      }

      console.log(`Attempting to fetch requirement options for ${type} product ${id}`)

      try {
        // First try to get from the specific endpoint with include_requirements
        let detailedData
        if (type === 'deposit') {
          detailedData = await productsService.getDepositProduct(id)
        } else if (type === 'saving') {
          detailedData = await productsService.getSavingProduct(id)
        }

        if (detailedData && detailedData.requirements) {
          requirementOptions.value = Array.isArray(detailedData.requirements)
            ? detailedData.requirements
            : [detailedData.requirements]
          console.log(
            'Success! Requirements loaded from product endpoint:',
            requirementOptions.value,
          )
          return
        }

        // If not successful, try the generic endpoint
        detailedData = await productsService.getProductByTypeAndId(type, id)
        console.log('Detailed product data:', detailedData)

        if (detailedData && detailedData.requirements) {
          requirementOptions.value = Array.isArray(detailedData.requirements)
            ? detailedData.requirements
            : [detailedData.requirements]
          console.log(
            'Success! Requirements loaded from generic endpoint:',
            requirementOptions.value,
          )
        } else {
          console.warn('No requirement options found in API response')

          // Create fallback data based on any available information in the product
          if (['deposit', 'saving'].includes(type)) {
            try {
              // Try to extract data from product properties if available
              const fallbackData = []

              // For deposit products with interest rates
              if (product.value.intr_rate || product.value.intr_rate2) {
                // Create at least one entry so chart is not empty
                fallbackData.push({
                  save_trm: product.value.save_trm || 12,
                  intr_rate: product.value.intr_rate || 3.0,
                  intr_rate2:
                    product.value.intr_rate2 ||
                    (parseFloat(product.value.intr_rate) + 0.5).toFixed(1),
                })
              }

              // If we have some term data but no requirements
              if (product.value.max_limit && !fallbackData.length) {
                fallbackData.push({
                  save_trm: product.value.save_trm || 12,
                  intr_rate: 3.0, // Default values since we don't have real data
                  intr_rate2: 3.5,
                })
              }

              if (fallbackData.length > 0) {
                requirementOptions.value = fallbackData
                console.log('Created fallback requirement data:', requirementOptions.value)
              }
            } catch (fallbackError) {
              console.error('Error creating fallback requirement data:', fallbackError)
            }
          }
        }
      } catch (error) {
        console.error('Error fetching requirement options:', error)

        // Provide a minimal fallback even after errors
        if (requirementOptions.value.length === 0 && ['deposit', 'saving'].includes(type)) {
          // Very simple fallback with just base values to allow chart to render
          requirementOptions.value = [{ save_trm: 12, intr_rate: 3.0, intr_rate2: 3.5 }]
          console.log('Using emergency fallback data after error')
        }
      }
    }

    // Create fallback data for interest rate chart
    const createFallbackData = () => {
      console.log('Creating fallback data for visualization')
      const productType = product.value?.product_type
        ? product.value.product_type.toLowerCase()
        : determineProductType(product.value)

      if (['deposit', 'saving'].includes(productType)) {
        // Create standard term options for visualization
        requirementOptions.value = [
          { save_trm: 6, intr_rate: 3.2, intr_rate2: 3.5 },
          { save_trm: 12, intr_rate: 3.5, intr_rate2: 3.8 },
          { save_trm: 24, intr_rate: 3.7, intr_rate2: 4.1 },
          { save_trm: 36, intr_rate: 3.9, intr_rate2: 4.5 },
        ]

        // If we have some product data, try to make the fallback more realistic
        if (product.value) {
          const baseRate = parseFloat(product.value?.intr_rate) || 3.0
          const maxRate =
            parseFloat(product.value?.intr_rate2 || product.value?.max_rate) || baseRate + 0.4

          // Adjust rates to match product data if available
          requirementOptions.value = requirementOptions.value.map((item, index) => {
            const termFactor = 1 + index * 0.1 // Increase rate with term
            return {
              save_trm: item.save_trm,
              intr_rate: +(baseRate * termFactor).toFixed(2),
              intr_rate2: +(maxRate * termFactor).toFixed(2),
            }
          })
        }

        console.log('Created visualization data:', requirementOptions.value)
      }
    }

    return {
      product,
      loading,
      error,
      isFavorite,
      activeTab,
      relatedProducts,
      requirementOptions,
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
      getRateClass,
      determineProductType,
      fetchRequirementOptions,
      createFallbackData,
    }
  },
}
</script>

<style scoped>
/* --- Base Page Layout --- */
.product-detail-container {
  max-width: var(--container-max-width, 1200px);
  margin: 0 auto;
  padding: var(--page-padding, 2rem 1.5rem);
  font-family: var(--font-body, 'Noto Sans KR', sans-serif);
  color: var(--text-primary, #333);
  background-color: var(--background-primary, #fff);
}

/* --- Loading and Error States --- */
.loading-container {
  text-align: center;
  padding: var(--spacing-xxl, 5rem) 0;
  color: var(--text-secondary);
  font-family: var(--font-body);
}
.loading-spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 5px solid var(--border-color-light, rgba(0, 0, 0, 0.1));
  border-radius: 50%;
  border-top-color: var(--accent-color, #3b82f6);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: var(--spacing-lg, 1rem);
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-container {
  text-align: center;
  padding: var(--spacing-xl, 4rem) var(--spacing-lg, 2rem);
  background: var(--background-error, #fef2f2);
  border-radius: var(--card-border-radius, 10px);
  color: var(--text-error, #b91c1c);
  border: 1px solid var(--border-error, #fecaca);
  margin: var(--spacing-xl, 2rem) auto;
  max-width: 600px;
}
.error-icon {
  font-size: var(--font-size-xxxl, 2.5rem);
  margin-bottom: var(--spacing-md, 1rem);
}
.error-container h3 {
  font-family: var(--font-heading);
  font-size: var(--font-size-xl, 1.5rem);
  color: var(--text-error-strong, var(--text-error));
  margin-bottom: var(--spacing-sm, 0.5rem);
}
.error-container p {
  font-family: var(--font-body);
  font-size: var(--font-size-md, 1rem);
  line-height: 1.6;
}
.retry-button {
  margin-top: var(--spacing-lg, 1.5rem);
  padding: var(--button-padding-y, 0.75rem) var(--button-padding-x, 1.5rem);
  background: var(
    --button-bg-error,
    var(--accent-color)
  ); /* Use accent or specific error button bg */
  color: var(--button-text-error, white);
  border: none;
  border-radius: var(--button-border-radius, 8px);
  font-weight: 600;
  font-family: var(--font-body);
  font-size: var(--font-size-md, 1rem);
  cursor: pointer;
  transition: background-color var(--transition-speed);
}
.retry-button:hover {
  background: var(--button-hover-bg-error, var(--accent-hover));
}

/* --- Page Header (Back, Share, Favorite) --- */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem; /* 기존 StockDetailView와 유사한 마진 */
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef; /* 구분선 추가 */
}
.back-button,
.share-button,
.favorite-button {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--button-padding-y-sm, 0.6rem) var(--button-padding-x-sm, 1.2rem);
  border-radius: var(--button-border-radius, 8px);
  font-size: var(--font-size-md, 0.95rem);
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-speed);
  border: 1px solid var(--button-border-color-secondary, var(--border-color));
  background-color: var(--button-bg-secondary, transparent);
  color: var(--button-text-secondary, var(--text-primary));
}
.back-button:hover,
.share-button:hover,
.favorite-button:hover {
  background-color: var(--button-hover-bg-secondary, var(--accent-color-opacity-10));
  border-color: var(--accent-color, #d1d5db);
  color: var(--accent-color);
}
.favorite-button.is-favorite {
  background-color: var(--accent-color-opacity-10, rgba(var(--accent-color-rgb), 0.1));
  color: var(--accent-color, #2563eb);
  border-color: var(--accent-color-translucent, var(--accent-color));
}
.favorite-button.is-favorite:hover {
  background-color: var(--accent-color-opacity-20, rgba(var(--accent-color-rgb), 0.2));
}
.favorite-button i,
.share-button i,
.back-button i {
  font-size: 1.2em;
}

/* --- Product Header Card --- */
.product-header-card {
  display: grid;
  grid-template-columns: auto 1fr auto; /* logo - main info - rate highlight */
  grid-template-areas:
    'logo mainInfo rate'
    'logo joinMethods rate';
  gap: var(--spacing-xl, 2rem);
  padding: var(--card-padding-lg, 2rem);
  background: var(--card-bg, white);
  border-radius: var(--card-border-radius, 16px);
  box-shadow: var(--shadow-lg, 0 8px 20px rgba(0, 0, 0, 0.1));
  margin-bottom: var(--spacing-xl, 2rem);
  border: 1px solid var(--card-border, transparent);
  align-items: center;
}

.product-bank-logo {
  grid-area: logo;
  width: var(--logo-size-xl, 90px);
  height: var(--logo-size-xl, 90px);
  background: var(--background-light-gray, #f3f4f6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid var(--border-color-extra-light, #e5e7eb);
  padding: var(--spacing-sm, 0.5rem);
}
.product-bank-logo img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.product-main-info {
  grid-area: mainInfo;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm, 0.75rem);
}

.product-badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm, 0.75rem);
  margin-bottom: var(--spacing-xs, 0.25rem);
}

.product-type-badge,
.new-badge {
  font-size: var(--font-size-sm, 0.9rem);
  font-weight: 700;
  padding: var(--badge-padding-y, 0.5rem) var(--badge-padding-x, 1rem);
  background-color: var(--accent-color-opacity-10, rgba(var(--accent-color-rgb), 0.1));
  color: var(--accent-color, #0369a1);
  border-radius: var(--badge-border-radius, 25px);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: var(--font-body);
}
.new-badge {
  background-color: var(--info-color-opacity-10, rgba(var(--info-color-rgb), 0.1));
  color: var(--info-color, #047857);
}

.product-name {
  font-size: var(--font-size-xxxl, 2.5rem); /* Increased size */
  font-weight: 700;
  margin: 0;
  color: var(--text-primary, #111827);
  font-family: var(--font-heading, 'Playfair Display', serif);
  line-height: 1.3;
}

.product-bank {
  display: flex;
  align-items: center;
  gap: var(--spacing-md, 1rem);
  color: var(--text-secondary, #4b5563);
  font-size: var(--font-size-lg, 1.1rem);
  font-weight: 500;
  font-family: var(--font-body);
}
.visit-bank-button {
  font-size: var(--font-size-md, 1rem);
  color: var(--accent-color, #2563eb);
  background: none;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  padding: 0;
  font-weight: 600;
  font-family: var(--font-body);
}
.visit-bank-button:hover {
  text-decoration: underline;
  color: var(--accent-hover, #1d4ed8);
}

.product-join-methods {
  grid-area: joinMethods;
  margin-top: var(--spacing-xs, 0.25rem);
  font-size: var(--font-size-md, 1rem);
  color: var(--text-secondary, #6b7280);
  font-family: var(--font-body);
}
.product-join-methods p {
  margin: 0;
}

.product-rate-highlight {
  grid-area: rate;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--card-padding-lg, 2rem) var(--card-padding-md, 1.5rem);
  background: var(--background-emphasis, rgba(var(--accent-color-rgb), 0.05));
  border-radius: var(--card-inner-border-radius, 12px);
  text-align: center;
  border: 1px solid var(--accent-color-opacity-20, rgba(var(--accent-color-rgb), 0.2));
  height: 100%; /* Fill height */
}
.product-rate-highlight .rate-value {
  font-size: var(--font-size-hero, 3rem); /* Increased size */
  font-weight: 700;
  line-height: 1.1;
  color: var(--accent-color-dark, var(--accent-color));
  margin-bottom: var(--spacing-sm, 0.5rem);
  font-family: var(--font-heading);
}
.product-rate-highlight .rate-value.loan-rate {
  color: var(--color-loan-rate-dark, var(--color-loan-rate, var(--accent-color)));
}
.product-rate-highlight .rate-label {
  font-size: var(--font-size-lg, 1.1rem);
  color: var(--text-secondary, #666);
  font-weight: 600;
  margin-bottom: var(--spacing-sm, 0.5rem);
  font-family: var(--font-body);
}
.product-rate-highlight .rate-info {
  font-size: var(--font-size-sm, 0.9rem);
  color: var(--text-tertiary, #9ca3af);
  font-family: var(--font-body);
}

/* --- Tabs --- */
.product-tabs {
  display: flex;
  gap: var(--spacing-md, 1rem);
  border-bottom: 2px solid var(--border-color, #e5e7eb);
  margin-bottom: var(--spacing-xl, 2rem);
}
.tab-button {
  padding: var(--tab-padding-y, 1rem) var(--tab-padding-x, 1.5rem);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--text-secondary, #6b7280);
  font-size: var(--font-size-lg, 1.1rem);
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-speed, 0.2s);
  margin-bottom: -2px;
}
.tab-button.active {
  color: var(--accent-color, #2563eb);
  border-bottom-color: var(--accent-color, #2563eb);
}
.tab-button:hover:not(.active) {
  color: var(--text-primary, #374151);
  border-bottom-color: var(--border-color-hover, #d1d5db);
}

/* --- Tab Content & Info Sections --- */
.tab-panel {
  padding: var(--spacing-lg, 1.5rem) 0;
}
.info-section {
  margin-bottom: var(--spacing-xl, 2.5rem);
  padding: var(--card-padding-lg, 2rem);
  background-color: var(--card-bg-secondary, var(--card-bg));
  border-radius: var(--card-border-radius, 12px);
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.05));
  border: 1px solid var(--card-border, transparent);
}
.info-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--font-size-xxl, 1.8rem);
  font-weight: 700;
  margin-bottom: var(--spacing-lg, 1.5rem);
  color: var(--text-primary, #111827);
  font-family: var(--font-heading, 'Playfair Display', serif);
  padding-bottom: var(--spacing-md, 1rem);
  border-bottom: 1px solid var(--border-color-light, #e5e7eb);
}
.section-subtitle {
  font-family: var(--font-heading);
  font-size: var(--font-size-xl, 1.4rem);
  color: var(--text-primary);
  margin-bottom: var(--spacing-md, 1rem);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg, 1.5rem) var(--spacing-xl, 2rem);
}
.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs, 0.5rem);
}
.info-item.wide {
  grid-column: 1 / -1;
}

.info-label {
  font-size: var(--font-size-md, 1rem);
  color: var(--text-secondary, #6b7280);
  font-weight: 600;
  font-family: var(--font-body);
}
.info-value {
  font-size: var(--font-size-lg, 1.1rem);
  color: var(--text-primary, #111827);
  line-height: 1.6;
  font-family: var(--font-body);
}
.info-value .join-badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm, 0.75rem);
}
.info-value .join-badge {
  font-size: var(--font-size-sm, 0.9rem);
  background: var(--tag-bg, var(--accent-color-opacity-10));
  color: var(--tag-text, var(--accent-color));
  padding: var(--badge-padding-y-sm, 0.4rem) var(--badge-padding-x-sm, 0.8rem);
  border-radius: var(--badge-border-radius-sm, 20px);
  font-weight: 600;
  font-family: var(--font-body);
}

.product-description {
  line-height: 1.7;
  color: var(--text-primary, #374151);
  white-space: pre-line;
  font-size: var(--font-size-lg, 1.1rem);
  font-family: var(--font-body);
}

/* --- Rate Specific Styles (Inside Tab) --- */
.rate-display {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping for multiple rates */
  justify-content: space-around; /* Distribute space */
  align-items: baseline; /* Align baselines of text */
  gap: var(--spacing-xl, 2rem);
  margin-bottom: var(--spacing-lg, 1.5rem);
  padding: var(--spacing-lg, 1.5rem);
  background-color: var(--background-light-gray, #f9f9f9);
  border-radius: var(--card-inner-border-radius, 10px);
}
.rate-display > div {
  /* Each rate block */
  text-align: center;
}
.rate-display .rate-value {
  font-size: var(--font-size-xxxl, 2.2rem);
  font-weight: 700;
  color: var(--accent-color, #4caf50);
  font-family: var(--font-heading);
  margin-bottom: var(--spacing-xs, 0.25rem);
}
.rate-display .rate-value.loan-rate {
  color: var(--color-loan-rate, #2196f3);
}
.rate-display .rate-value.highlight {
  /* For max_rate or similar */
  font-size: var(--font-size-hero, 2.8rem);
  color: var(--accent-color-dark, var(--accent-color));
}
.rate-display .rate-label {
  font-size: var(--font-size-md, 1rem);
  color: var(--text-secondary, #666);
  font-family: var(--font-body);
  font-weight: 500;
}

.rate-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md, 1rem);
  margin-top: var(--spacing-lg, 1.5rem);
}
.detail-item {
  display: flex; /* Use flex for better alignment */
  gap: var(--spacing-sm, 0.5rem);
  font-family: var(--font-body);
  font-size: var(--font-size-md, 1rem);
}
.detail-label {
  font-weight: 600;
  color: var(--text-secondary, #666);
  flex-shrink: 0; /* Prevent label from shrinking */
}
.detail-value {
  color: var(--text-primary, #333);
}

/* --- Join Methods & Conditions (Inside Tab) --- */
.join-methods-detailed {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg, 1.5rem);
}
.join-method-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-lg, 1.5rem);
  padding: var(--card-padding-lg, 1.75rem);
  background: var(--card-bg-secondary, #f9fafb);
  border-radius: var(--card-border-radius, 12px);
  border: 1px solid var(--card-border, transparent);
  box-shadow: var(--shadow-sm);
}
.join-method-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--icon-container-size-lg, 60px);
  height: var(--icon-container-size-lg, 60px);
  background: var(--accent-color-opacity-10, #e0f2fe);
  color: var(--accent-color, #0284c7);
  border-radius: 50%;
  font-size: var(--icon-size-xl, 2rem);
  flex-shrink: 0;
}
.join-method-content h4 {
  font-size: var(--font-size-xl, 1.3rem);
  font-weight: 700;
  margin: 0 0 var(--spacing-sm, 0.5rem) 0;
  color: #000000; /* 검은색으로 변경 */
  font-family: var(--font-heading);
}
.join-method-content p {
  margin: 0;
  color: #000000; /* 검은색으로 변경 */
  line-height: 1.6;
  font-size: var(--font-size-md, 1rem);
  font-family: var(--font-body);
}

.conditions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md, 1rem);
  margin-bottom: var(--spacing-lg, 1.5rem);
}
.condition-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md, 1rem);
  padding: var(--spacing-lg, 1rem) var(--spacing-lg, 1.25rem);
  background: var(--background-light-gray, #f3f4f6);
  border-radius: var(--card-border-radius-sm, 8px);
  font-family: var(--font-body);
  font-size: var(--font-size-md, 1rem);
  color: #000000; /* 검은색으로 변경 */
}
.condition-item i {
  color: var(--success-color, var(--accent-color));
  font-size: var(--icon-size-lg, 1.5rem);
}

.requirement-note {
  font-size: var(--font-size-md, 0.95rem);
  color: #000000; /* 검은색으로 변경 */
  margin-top: var(--spacing-lg, 1.5rem);
  padding: var(--spacing-md, 1rem);
  background-color: var(--background-info-light, #f3f4f6);
  border-left: 4px solid var(--info-color, var(--accent-color));
  border-radius: 0 var(--card-border-radius-sm, 6px) var(--card-border-radius-sm, 6px) 0;
  font-family: var(--font-body);
  line-height: 1.6;
}

/* --- Interest Rate Chart Section --- */
.interest-rate-chart-section {
  margin: var(--spacing-xl, 2rem) 0;
  border-top: 1px solid var(--border-color, #e9ecef);
  padding-top: var(--spacing-xl, 2rem);
}
.no-chart-data {
  text-align: center;
  padding: var(--spacing-xl, 2rem);
  background: var(--background-light-gray, #f9fafb);
  border-radius: var(--card-border-radius, 8px);
  font-family: var(--font-body);
}
.no-chart-data p {
  margin-bottom: var(--spacing-lg, 1rem);
  color: var(--text-secondary, #6b7280);
  font-size: var(--font-size-md, 1rem);
}
.refresh-button,
.fallback-button {
  padding: var(--button-padding-y, 0.75rem) var(--button-padding-x, 1.5rem);
  border-radius: var(--button-border-radius, 8px);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-speed, 0.2s);
  margin: var(--spacing-sm, 0.5rem);
  font-size: var(--font-size-md, 1rem);
  font-family: var(--font-body);
}
.refresh-button {
  background: var(--button-bg, var(--accent-color));
  color: var(--button-text, white);
  border: 1px solid var(--button-bg, var(--accent-color));
}
.refresh-button:hover {
  background: var(--button-hover, var(--accent-hover));
  border-color: var(--button-hover, var(--accent-hover));
}

.fallback-button {
  background: var(--button-bg-secondary, transparent);
  color: var(--button-text-secondary, var(--accent-color));
  border: 1px solid var(--button-border-color-secondary, var(--accent-color));
}
.fallback-button:hover {
  background: var(--button-hover-bg-secondary, var(--accent-color-opacity-10));
}

/* --- CTA Section --- */
.cta-section {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg, 1.5rem);
  margin: var(--spacing-xl, 2.5rem) 0;
  padding-top: var(--spacing-xl, 2rem);
  border-top: 1px solid var(--border-color, #e5e7eb);
}
.cta-button {
  flex: 1 1 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md, 0.75rem);
  padding: var(--button-padding-y-lg, 1rem) var(--button-padding-x-lg, 2rem);
  border-radius: var(--button-border-radius-lg, 12px);
  font-weight: 700;
  font-size: var(--font-size-lg, 1.1rem);
  font-family: var(--font-body);
  cursor: pointer;
  transition: all var(--transition-speed, 0.2s);
  text-align: center;
  min-width: 200px; /* Ensure buttons have a minimum width */
}
.cta-button.primary {
  background: var(--button-bg, var(--accent-color));
  color: var(--button-text, white);
  border: 1px solid var(--button-bg, var(--accent-color));
}
.cta-button.primary:hover {
  background: var(--button-hover, var(--accent-hover));
  border-color: var(--button-hover, var(--accent-hover));
}

.cta-button.secondary {
  background: var(--button-bg-secondary, transparent);
  color: var(--button-text-secondary, var(--accent-color));
  border: 2px solid var(--button-border-color-secondary, var(--accent-color)); /* Thicker border for secondary */
}
.cta-button.secondary:hover {
  background: var(--button-hover-bg-secondary, var(--accent-color-opacity-10));
}
.cta-button i {
  font-size: 1.2em;
}

/* --- Related Products --- */
.related-products {
  margin-top: var(--spacing-xxl, 3rem);
  padding-top: var(--spacing-xl, 2rem);
  border-top: 1px solid var(--border-color, #e5e7eb);
}
.related-products .section-title {
  text-align: center;
  border-bottom: none;
  margin-bottom: var(--spacing-xl, 2rem);
}
.related-products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-xl, 2rem);
}

/* --- Responsive Adjustments --- */
@media (max-width: 992px) {
  .product-header-card {
    grid-template-columns: 1fr; /* Stack on medium screens */
    grid-template-areas:
      'logo'
      'mainInfo'
      'rate'
      'joinMethods';
    text-align: center;
  }
  .product-bank-logo {
    margin: 0 auto var(--spacing-lg, 1.5rem) auto;
  }
  .product-main-info,
  .product-rate-highlight {
    align-items: center; /* Center align content in stack */
  }
  .product-rate-highlight {
    width: 100%;
    padding: var(--card-padding, 1.5rem);
  }
}

@media (max-width: 768px) {
  .product-detail-container {
    padding: var(--page-padding-sm, 1.5rem 1rem);
  }
  .product-name {
    font-size: var(--font-size-xxl, 2rem);
  }
  .product-rate-highlight .rate-value {
    font-size: var(--font-size-xxl, 2.2rem);
  }
  .section-title {
    font-size: var(--font-size-xl, 1.6rem);
  }
  .info-grid,
  .rates-grid,
  .join-methods-detailed,
  .related-products-grid {
    grid-template-columns: 1fr;
  }
  .product-tabs {
    overflow-x: auto;
    white-space: nowrap;
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
  }
  .product-tabs::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Opera */
  }
  .tab-button {
    flex-shrink: 0;
    font-size: var(--font-size-md, 1rem);
    padding: var(--tab-padding-y, 0.75rem) var(--tab-padding-x, 1rem);
  }
  .cta-section {
    flex-direction: column;
  }
  .cta-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .product-name {
    font-size: var(--font-size-xl, 1.75rem);
  }
  .product-rate-highlight .rate-value {
    font-size: var(--font-size-xl, 2rem);
  }
  .page-header {
    flex-direction: column;
    gap: var(--spacing-md, 1rem);
    align-items: stretch;
  }
  .page-header .header-actions {
    display: flex;
    justify-content: space-around;
    width: 100%;
  }
  .back-button,
  .share-button,
  .favorite-button {
    flex-grow: 1;
    justify-content: center;
  }
}

.header-actions {
  display: flex;
  align-items: center; /* 버튼들을 세로 중앙으로 정렬 */
  gap: 0.75rem; /* 버튼 사이의 간격 추가 */
}
</style>
