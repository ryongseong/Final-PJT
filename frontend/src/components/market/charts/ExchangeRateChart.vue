<template>
  <div class="chart-wrapper">
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>{{ $t('market.loadingData') }}</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ $t('market.errorLoadingData') }}</p>
      <button @click="retryLoading" class="retry-button">
        {{ $t('market.retry') }}
      </button>
    </div>
    <canvas v-else ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, reactive } from 'vue';
import { useSettingsStore } from '@/stores/settings';
import { useI18n } from 'vue-i18n';
import Chart from 'chart.js/auto';
import axios from 'axios';

const chartCanvas = ref(null);
const chart = ref(null);
const settingsStore = useSettingsStore();
const { t, locale } = useI18n();

const isLoading = ref(true);
const error = ref(null);
const chartData = reactive({
  labels: [],
  datasets: [
    {
      label: 'USD/KRW',
      data: [],
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      borderWidth: 3,
      tension: 0.4,
      fill: true
    },
    {
      label: 'EUR/KRW',
      data: [],
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 3,
      tension: 0.4,
      fill: true
    },
    {
      label: 'JPY/KRW(100엔)',
      data: [],
      borderColor: '#EC4899',
      backgroundColor: 'rgba(236, 72, 153, 0.1)',
      borderWidth: 3,
      tension: 0.4,
      fill: true
    }
  ]
});

// 최근 6개월 데이터 가져오기
const fetchExchangeRates = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    // 현재 날짜에서 6개월 전까지의 날짜 범위 계산
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 6);
    
    const formatDate = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    
    // API 요청을 위한 날짜 형식 변환
    const startDateStr = formatDate(startDate);
    const endDateStr = formatDate(endDate);
    
    // 환율 API 키 가져오기
    const apiKey = settingsStore.getApiKey('exchangeRate') || import.meta.env.VITE_EXCHANGE_RATE_API;
    
    // 환율 API 호출
    const response = await axios.get('https://api.exchangerate.host/timeseries', {
      params: {
        start_date: startDateStr,
        end_date: endDateStr,
        base: 'USD',
        symbols: 'KRW,EUR,JPY',
        access_key: apiKey
      }
    });
    
    // 응답 데이터 처리
    const { rates } = response.data;
    
    // 날짜 라벨 및 환율 데이터 구성
    const dates = Object.keys(rates).sort();
    const monthlyData = {};
    
    // 월별 데이터로 그룹화
    dates.forEach(date => {
      const monthYear = date.substring(0, 7); // YYYY-MM 형식
      if (!monthlyData[monthYear]) {
        monthlyData[monthYear] = {
          usdKrw: [],
          eurKrw: [],
          jpyKrw: []
        };
      }
      
      if (rates[date].KRW) {
        monthlyData[monthYear].usdKrw.push(rates[date].KRW);
        
        // EUR/KRW 계산: USD/KRW ÷ USD/EUR
        if (rates[date].EUR) {
          const eurKrw = rates[date].KRW / rates[date].EUR;
          monthlyData[monthYear].eurKrw.push(eurKrw);
        }
        
        // JPY/KRW 계산: USD/KRW ÷ USD/JPY × 100 (100엔 단위)
        if (rates[date].JPY) {
          const jpyKrw = (rates[date].KRW / rates[date].JPY) * 100;
          monthlyData[monthYear].jpyKrw.push(jpyKrw);
        }
      }
    });
    
    // 월별 평균 계산
    const months = Object.keys(monthlyData).sort().slice(-6); // 최근 6개월
    
    const calculateAverage = (arr) => {
      if (arr.length === 0) return 0;
      return arr.reduce((sum, val) => sum + val, 0) / arr.length;
    };
    
    // 차트 데이터 업데이트
    chartData.labels = months.map(month => {
      const [year, monthNum] = month.split('-');
      return locale.value === 'ko' 
        ? `${year}년 ${monthNum}월`
        : `${new Date(year, monthNum - 1).toLocaleString(locale.value === 'ko' ? 'ko-KR' : 'en-US', { month: 'short' })} ${year}`;
    });
    
    chartData.datasets[0].data = months.map(month => 
      parseFloat(calculateAverage(monthlyData[month].usdKrw).toFixed(2))
    );
    
    chartData.datasets[1].data = months.map(month => 
      parseFloat(calculateAverage(monthlyData[month].eurKrw).toFixed(2))
    );
    
    chartData.datasets[2].data = months.map(month => 
      parseFloat(calculateAverage(monthlyData[month].jpyKrw).toFixed(2))
    );
    
    isLoading.value = false;
  } catch (err) {
    console.error('환율 데이터 로딩 중 오류 발생:', err);
    error.value = err.message || '환율 데이터를 가져오는 중 오류가 발생했습니다.';
    isLoading.value = false;
    
    // 오류 발생 시 데모 데이터 사용
    useDefaultData();
  }
};

// 데모 데이터 (API 오류 시 사용)
const useDefaultData = () => {
  const months = locale.value === 'ko' 
    ? ['1월', '2월', '3월', '4월', '5월', '6월']
    : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    
  chartData.labels = months;
  chartData.datasets[0].data = [1320, 1330, 1310, 1340, 1360, 1350];
  chartData.datasets[1].data = [1430, 1450, 1440, 1470, 1490, 1480];
  chartData.datasets[2].data = [980, 970, 960, 950, 940, 930];
};

// 데이터 로딩 재시도
const retryLoading = async () => {
  await fetchExchangeRates();
  createChart();
};

// 차트 데이터 반환 함수
const getChartData = () => {
  return {
    labels: chartData.labels,
    datasets: chartData.datasets
  };
};

const createChart = () => {
  if (chartCanvas.value) {
    // 이전 차트 인스턴스 제거
    if (chart.value) {
      chart.value.destroy();
    }
    
    const ctx = chartCanvas.value.getContext('2d');
    
    // 다크모드에 따른 글자색 설정
    const textColor = settingsStore.isDarkMode ? '#F0ECE6' : '#333333';
    const gridColor = settingsStore.isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    chart.value = new Chart(ctx, {
      type: 'line',
      data: getChartData(),
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 14
              },
              padding: 20
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: settingsStore.isDarkMode ? '#3A3A3A' : 'white',
            titleColor: textColor,
            bodyColor: textColor,
            borderColor: gridColor,
            borderWidth: 1,
            padding: 12,
            bodyFont: {
              family: 'Inter, sans-serif',
              size: 14
            },
            titleFont: {
              family: 'Inter, sans-serif',
              size: 16,
              weight: 'bold'
            },
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('ko-KR').format(context.parsed.y) + ' 원';
                }
                return label;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: gridColor,
              drawBorder: false
            },
            ticks: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 13
              },
              padding: 10
            }
          },
          y: {
            grid: {
              color: gridColor,
              drawBorder: false
            },
            ticks: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 13
              },
              padding: 10,
              callback: function(value) {
                return value.toLocaleString('ko-KR') + '원';
              }
            }
          }
        },
        elements: {
          point: {
            radius: 5,
            hoverRadius: 8,
            hitRadius: 10
          },
          line: {
            borderWidth: 3
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        hover: {
          mode: 'index',
          intersect: false
        }
      }
    });
  }
};

// 다크모드 변경 감지
watch(() => settingsStore.isDarkMode, () => {
  createChart();
});

// 언어 변경 감지
window.addEventListener('languageChanged', () => {
  createChart();
});

onMounted(async () => {
  // 초기 데이터 로드
  await fetchExchangeRates();
  
  // 차트 생성
  createChart();
  
  // 창 크기 변경 시 차트 리사이징
  window.addEventListener('resize', createChart);
});

// 언어 변경 시 차트 라벨 업데이트
watch(locale, async () => {
  await fetchExchangeRates();
  createChart();
});

onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.destroy();
  }
  window.removeEventListener('resize', createChart);
  window.removeEventListener('languageChanged', createChart);
});
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--accent-color);
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.dark .loading-spinner {
  border-color: rgba(255, 255, 255, 0.1);
  border-top-color: var(--accent-color);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  background-color: var(--accent-hover);
  transform: translateY(-2px);
}
</style>