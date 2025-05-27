<template>
  <div class="chart-wrapper">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import Chart from 'chart.js/auto'
import productsService from '@/services/products'

const chartCanvas = ref(null)
const chart = ref(null)
const settingsStore = useSettingsStore()

// KOSPI 차트 데이터
const getChartData = async () => {
  const response = await productsService.getKospiData()

  return {
    labels: response.data.map((item) => item.date),
    datasets: [
      {
        label: 'KOSPI 지수',
        data: response.data.map((item) => item.close),
        borderColor: '#FFD700',
        backgroundColor: 'rgba(255, 215, 0, 0.1)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
      },
    ],
  }
}

const createChart = async () => {
  if (chartCanvas.value) {
    if (chart.value) {
      chart.value.destroy()
    }

    const ctx = chartCanvas.value.getContext('2d')

    const textColor = settingsStore.isDarkMode ? '#F0ECE6' : '#333333'
    const gridColor = settingsStore.isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'

    const data = await getChartData()

    chart.value = new Chart(ctx, {
      type: 'line',
      data: data,
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
                size: 14,
              },
              padding: 20,
            },
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
              size: 14,
            },
            titleFont: {
              family: 'Inter, sans-serif',
              size: 16,
              weight: 'bold',
            },
            callbacks: {
              label: function (context) {
                let label = context.dataset.label || ''
                if (label) {
                  label += ': '
                }
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('ko-KR').format(context.parsed.y) + ' pt'
                }
                return label
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              color: gridColor,
              drawBorder: false,
            },
            ticks: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 13,
              },
              padding: 10,
            },
          },
          y: {
            grid: {
              color: gridColor,
              drawBorder: false,
            },
            ticks: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 13,
              },
              padding: 10,
              callback: function (value) {
                return value.toLocaleString('ko-KR')
              },
            },
          },
        },
        elements: {
          point: {
            radius: 0,
            hoverRadius: 8,
            hitRadius: 0,
          },
          line: {
            borderWidth: 3,
          },
        },
        interaction: {
          mode: 'index',
          intersect: false,
        },
        hover: {
          mode: 'index',
          intersect: false,
        },
      },
    })
  }
}

watch(
  () => settingsStore.isDarkMode,
  () => {
    createChart()
  },
)

window.addEventListener('languageChanged', () => {
  createChart()
})

onMounted(() => {
  createChart()
  window.addEventListener('resize', createChart)
})

onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.destroy()
  }
  window.removeEventListener('resize', createChart)
  window.removeEventListener('languageChanged', createChart)
})
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
