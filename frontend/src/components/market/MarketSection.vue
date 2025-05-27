<template>
  <section class="market-section">
    <div class="container">
      <h2 class="section-title">{{ $t('market.title') }}</h2>
      <p class="section-description">{{ $t('market.description') }}</p>

      <div class="cards-container">
        <!-- 금 가격 비교 -->
        <div class="market-card">
          <h3>{{ $t('market.preciousGold') }}</h3>
          <div class="chart-container">
            <GoldPriceChart />
          </div>
          <p class="card-description">{{ $t('market.preciousGoldDesc') }}</p>
        </div>

        <!-- 은 가격 비교 -->
        <div class="market-card">
          <h3>{{ $t('market.preciousSilver') }}</h3>
          <div class="chart-container">
            <SilverPriceChart />
          </div>
          <p class="card-description">{{ $t('market.preciousSilverDesc') }}</p>
        </div>
      </div>
    </div>
  </section>
  <section class="market-section">
    <div class="container">
      <div class="market-card-exchange">
        <h3>{{ $t('market.exchangeRates') }}</h3>
        <div class="chart-container-exchange">
          <ExchangeRateChart />
        </div>
        <p class="card-description">{{ $t('market.exchangeRatesDesc') }}</p>
      </div>
    </div>
  </section>
  <section class="market-section">
    <div class="container">
      <div class="cards-container">
        <div class="market-card">
          <h3>{{ $t('market.kopsi') }}</h3>
          <div class="chart-container">
            <KospiChart />
          </div>
          <p class="card-description">{{ $t('market.kopsiDesc') }}</p>
        </div>

        <div class="market-card">
          <h3>{{ $t('market.kosdaq') }}</h3>
          <div class="chart-container">
            <KosdaqChart />
          </div>
          <p class="card-description">{{ $t('market.kosdaqDesc') }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import ExchangeRateChart from './charts/ExchangeRateChart.vue'
import GoldPriceChart from './charts/GoldPriceChart.vue'
import KosdaqChart from './charts/KosdaqChart.vue'
import KospiChart from './charts/KospiChart.vue'
import SilverPriceChart from './charts/SilverPriceChart.vue'
</script>

<style scoped>
.market-section {
  padding: 6rem 1rem; /* 섹션 크기 증가 */
  margin: 2rem 0; /* 섹션 간격 추가 */
  background: var(--background-gradient);
  transition: var(--transition-speed);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-family: 'Pretendard Variable', serif;
  font-size: 3rem; /* 제목 크기 증가 */
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  text-align: center;
  transition: var(--transition-speed);
  font-weight: 700;
  text-shadow: var(--hero-text-shadow);
}

.section-description {
  font-family: 'Pretendard Variable', sans-serif;
  text-align: center;
  margin-bottom: 4rem; /* 마진 증가 */
  color: var(--text-secondary);
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  transition: var(--transition-speed);
  font-size: 1.2rem; /* 설명 글씨 크기 증가 */
  line-height: 1.6;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2.5rem; /* 카드 간 간격 증가 */
  transition: var(--transition-speed);
}

.market-card {
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 2rem; /* 패딩 증가 */
  box-shadow: var(--card-shadow);
  transition: var(--transition-speed);
  border: 1px solid var(--card-border);
  transform: translateY(0);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.market-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.market-card h3 {
  font-family: 'Pretendard Variable', serif;
  font-size: 1.8rem; /* 제목 크기 증가 */
  margin-bottom: 1.8rem;
  color: var(--text-primary);
  transition: var(--transition-speed);
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 300px; /* 차트 크기 증가 */
  margin-bottom: 1.5rem;
  transition: var(--transition-speed);
  position: relative;
}

.chart-container-exchange {
  width: 100%;
  height: 500px; /* 차트 크기 증가 */
  margin-bottom: 1.5rem;
  transition: var(--transition-speed);
  position: relative;
}

.card-description {
  font-family: 'Pretendard Variable', sans-serif;
  color: var(--text-secondary);
  font-size: 1rem; /* 설명 글씨 크기 증가 */
  transition: var(--transition-speed);
  line-height: 1.6;
}

/* 반응형 레이아웃 */
@media (max-width: 1200px) {
  .cards-container {
    grid-template-columns: repeat(3, 1fr);
    padding: 0 1.5rem;
  }

  .chart-container {
    height: 250px;
  }
}

@media (max-width: 992px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-title {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .market-section {
    padding: 4rem 1rem;
  }

  .cards-container {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 2.2rem;
  }

  .section-description {
    font-size: 1.1rem;
    margin-bottom: 3rem;
  }
}
</style>
