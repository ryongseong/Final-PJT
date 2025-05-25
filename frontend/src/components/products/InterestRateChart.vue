<template>
  <div class="interest-rate-chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

// Register all Chart.js components
Chart.register(...registerables)

export default {
  name: 'InterestRateChart',
  props: {
    requirements: {
      type: Array,
      required: true,
    },
    productType: {
      type: String,
      default: 'deposit',
    },
  },
  setup(props) {
    const chartCanvas = ref(null)
    let chart = null

    // Format period labels (e.g., "6개월" for 6)
    const formatPeriod = (period) => {
      // Handle string or number inputs
      const numPeriod = typeof period === 'string' ? parseInt(period, 10) : period
      return isNaN(numPeriod) ? period : `${numPeriod}개월`
    }

    // Create and render the chart
    const renderChart = () => {
      if (!chartCanvas.value || !props.requirements || props.requirements.length === 0) return

      // Sort requirements by save_trm (period)
      const sortedRequirements = [...props.requirements].sort((a, b) => {
        // Handle string or number values
        const termA = typeof a.save_trm === 'string' ? parseInt(a.save_trm, 10) : a.save_trm
        const termB = typeof b.save_trm === 'string' ? parseInt(b.save_trm, 10) : b.save_trm
        return termA - termB
      })

      console.log('Sorted requirements:', sortedRequirements)

      // Prepare data
      const periods = sortedRequirements.map((req) => formatPeriod(req.save_trm))
      const basicRates = sortedRequirements.map((req) => {
        const rate = parseFloat(req.intr_rate)
        return isNaN(rate) ? 0 : rate
      })
      const maxRates = sortedRequirements.map((req) => {
        const rate = parseFloat(req.intr_rate2)
        return isNaN(rate) ? 0 : rate
      })

      console.log('Chart data ready:', { periods, basicRates, maxRates })

      // Color settings based on product type
      const basicRateColor =
        props.productType === 'deposit' ? 'rgba(54, 162, 235, 0.7)' : 'rgba(153, 102, 255, 0.7)'
      const maxRateColor =
        props.productType === 'deposit' ? 'rgba(54, 162, 235, 1)' : 'rgba(153, 102, 255, 1)'

      // Destroy existing chart if it exists
      if (chart) {
        chart.destroy()
      }

      // Create new chart
      chart = new Chart(chartCanvas.value, {
        type: 'bar',
        data: {
          labels: periods,
          datasets: [
            {
              label: '기본 금리',
              data: basicRates,
              backgroundColor: basicRateColor,
              borderColor: basicRateColor.replace('0.7', '1'),
              borderWidth: 1,
            },
            {
              label: '최고 우대금리',
              data: maxRates,
              backgroundColor: maxRateColor,
              borderColor: maxRateColor,
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: '금리 (%)',
                font: {
                  weight: 'bold',
                },
              },
              ticks: {
                callback: function (value) {
                  return value.toFixed(2) + '%'
                },
                precision: 0.1,
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.05)',
              },
            },
            x: {
              title: {
                display: true,
                text: '가입 기간',
                font: {
                  weight: 'bold',
                },
              },
              grid: {
                display: false,
              },
            },
          },
          plugins: {
            legend: {
              position: 'top',
              labels: {
                boxWidth: 15,
                usePointStyle: true,
                padding: 20,
              },
            },
            title: {
              display: true,
              text: props.productType === 'deposit' ? '예금 금리 정보' : '적금 금리 정보',
              font: {
                size: 16,
                weight: 'bold',
              },
              padding: {
                bottom: 20,
              },
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              padding: 10,
              titleFont: {
                size: 13,
              },
              bodyFont: {
                size: 12,
              },
              callbacks: {
                label: function (context) {
                  return context.dataset.label + ': ' + context.raw.toFixed(2) + '%'
                },
              },
            },
          },
        },
      })
    }

    // Watch for changes in requirements data
    watch(
      () => props.requirements,
      () => {
        renderChart()
      },
      { deep: true },
    )

    // Initialize chart when component is mounted
    onMounted(() => {
      try {
        console.log('InterestRateChart mounted, requirements:', props.requirements)
        renderChart()
      } catch (error) {
        console.error('Error rendering chart on mount:', error)
      }
    })

    // Clean up when component is unmounted
    onUnmounted(() => {
      if (chart) {
        chart.destroy()
      }
    })

    return { chartCanvas }
  },
}
</script>

<style scoped>
.interest-rate-chart-container {
  width: 100%;
  height: 400px;
  margin: 20px 0;
  padding: 15px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
</style>
