<template>
  <div class="chart-wrapper">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useSettingsStore } from '@/stores/settings';
import Chart from 'chart.js/auto';

const chartCanvas = ref(null);
const chart = ref(null);
const settingsStore = useSettingsStore();

// 차트 데이터 (실제 프로젝트에서는 API로 가져오기)
const getChartData = () => {
  return {
    labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
    datasets: [
      {
        label: '금(KRW/g)',
        data: [85000, 86500, 88000, 87500, 90000, 93000],
        borderColor: '#FFD700',
        backgroundColor: 'rgba(255, 215, 0, 0.1)',
        borderWidth: 3,
        tension: 0.3,
        fill: true
      },
      {
        label: '은(KRW/g)',
        data: [1200, 1180, 1250, 1300, 1320, 1350],
        borderColor: '#C0C0C0',
        backgroundColor: 'rgba(192, 192, 192, 0.1)',
        borderWidth: 3,
        tension: 0.3,
        fill: true
      }
    ]
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
                  label += new Intl.NumberFormat('ko-KR').format(context.parsed.y);
                  if (context.datasetIndex === 0) {
                    label += ' 원/g';
                  } else {
                    label += ' 원/g';
                  }
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
                return value.toLocaleString('ko-KR');
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

onMounted(() => {
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