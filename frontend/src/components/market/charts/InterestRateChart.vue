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
      label: '한국은행 기준금리 (%)',
      data: [],
      borderColor: '#4f46e5',
      backgroundColor: 'rgba(79, 70, 229, 0.1)',
      borderWidth: 3,
      tension: 0.2,
      fill: true
    },
    {
      label: '1년 만기 정기예금 평균금리 (%)',
      data: [],
      borderColor: '#6D63FF',
      backgroundColor: 'rgba(109, 99, 255, 0.1)',
      borderWidth: 3,
      tension: 0.2,
      fill: true
    }
  ]
});

// 한국은행 API에서 금리 데이터 가져오기
const fetchInterestRates = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    // API 키 가져오기
    const apiKey = settingsStore.getApiKey('bok') || import.meta.env.VITE_BOK_API_KEY;
    
    if (!apiKey) {
      console.warn('BOK API key not provided, using sample data');
      useDefaultData();
      isLoading.value = false;
      return;
    }
    
    // 현재 날짜 기준으로 마지막 6분기 계산
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth() + 1;
    const currentQuarter = Math.ceil(currentMonth / 3);
    
    // 최근 6분기 계산
    let quarters = [];
    for (let i = 0; i < 6; i++) {
      let year = currentYear;
      let quarter = currentQuarter - i;
      
      if (quarter <= 0) {
        quarter += 4;
        year -= 1;
      }
      
      quarters.unshift({ year, quarter });
    }
    
    // 한국은행 API 호출 (통계코드: 722Y001 - 한국은행 기준금리)
    const bokResponse = await axios.get('https://ecos.bok.or.kr/api/StatisticSearch', {
      params: {
        apiKey: apiKey,
        serviceName: 'StatisticSearch',
        language: 'ko',
        startDate: `${quarters[0].year}${quarters[0].quarter}`,
        endDate: `${quarters[5].year}${quarters[5].quarter}`,
        statsCode: '722Y001',
        itemCode1: 'A',
        cycle: 'Q',
        format: 'json'
      }
    });
    
    // 예금 금리 데이터 호출 (통계코드: 721Y001 - 수신금리, 신규취급액 기준)
    const depositResponse = await axios.get('https://ecos.bok.or.kr/api/StatisticSearch', {
      params: {
        apiKey: apiKey,
        serviceName: 'StatisticSearch',
        language: 'ko',
        startDate: `${quarters[0].year}${quarters[0].quarter}`,
        endDate: `${quarters[5].year}${quarters[5].quarter}`,
        statsCode: '721Y001',
        itemCode1: '5110000',  // 정기예금(1년)
        cycle: 'Q',
        format: 'json'
      }
    });
    
    // 응답 데이터 처리
    const bokData = bokResponse.data?.StatisticSearch?.row || [];
    const depositData = depositResponse.data?.StatisticSearch?.row || [];
    
    // 라벨 생성
    chartData.labels = quarters.map(q => {
      return locale.value === 'ko' 
        ? `${q.year}년 ${q.quarter}분기`
        : `${q.year} Q${q.quarter}`;
    });
    
    // 기준금리 데이터 추출
    chartData.datasets[0].data = bokData.map(item => parseFloat(item.DATA_VALUE));
    
    // 예금금리 데이터 추출
    chartData.datasets[1].data = depositData.map(item => parseFloat(item.DATA_VALUE));
    
    // 다국어 라벨 설정
    chartData.datasets[0].label = locale.value === 'ko' 
      ? '한국은행 기준금리 (%)' 
      : 'Bank of Korea Base Rate (%)';
    
    chartData.datasets[1].label = locale.value === 'ko'
      ? '1년 만기 정기예금 평균금리 (%)' 
      : '1-Year Fixed Deposit Average Rate (%)';
    
    isLoading.value = false;
  } catch (err) {
    console.error('금리 데이터 로딩 중 오류 발생:', err);
    error.value = err.message || '금리 데이터를 가져오는 중 오류가 발생했습니다.';
    isLoading.value = false;
    
    // 오류 발생 시 데모 데이터 사용
    useDefaultData();
  }
};

// 데모 데이터 (API 오류 시 사용)
const useDefaultData = () => {
  // 라벨 설정
  chartData.labels = locale.value === 'ko' 
    ? ['2022년 1분기', '2022년 2분기', '2022년 3분기', '2022년 4분기', '2023년 1분기', '2023년 2분기']
    : ['2022 Q1', '2022 Q2', '2022 Q3', '2022 Q4', '2023 Q1', '2023 Q2'];
  
  // 데이터 설정
  chartData.datasets[0].data = [1.25, 1.75, 2.25, 3.25, 3.5, 3.5];
  chartData.datasets[1].data = [1.5, 2.1, 2.7, 3.8, 4.1, 4.0];
  
  // 다국어 라벨 설정
  chartData.datasets[0].label = locale.value === 'ko' 
    ? '한국은행 기준금리 (%)' 
    : 'Bank of Korea Base Rate (%)';
  
  chartData.datasets[1].label = locale.value === 'ko'
    ? '1년 만기 정기예금 평균금리 (%)' 
    : '1-Year Fixed Deposit Average Rate (%)';
};

// 데이터 로딩 재시도
const retryLoading = async () => {
  await fetchInterestRates();
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
                  label += context.parsed.y.toFixed(2) + '%';
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
                return value + '%';
              }
            },
            suggestedMin: 0,
            suggestedMax: 5
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
window.addEventListener('languageChanged', async () => {
  await fetchInterestRates();
  createChart();
});

onMounted(async () => {
  // 초기 데이터 로드
  await fetchInterestRates();
  
  // 차트 생성
  createChart();
  
  // 창 크기 변경 시 차트 리사이징
  window.addEventListener('resize', createChart);
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
}
</style> 