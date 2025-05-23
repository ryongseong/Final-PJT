<!-- filepath: /Users/ryong/git/Final-PJT/frontend/src/views/MapView.vue -->
<template>
  <div class="map-view">
    <h1>금융기관 위치 검색</h1>
    <div class="instructions">
      <p>
        지역(시/도, 구/군)과 은행을 선택하여 원하는 은행을 검색하거나, 현재 위치 근처의 은행을
        검색할 수 있습니다.
      </p>
    </div>

    <div class="map-wrapper">
      <KakaoMap
        ref="kakaoMap"
        :markers="markers"
        @location-changed="onLocationChanged"
        @marker-clicked="onMarkerClicked"
        @map-clicked="onMapClicked"
        @bank-clicked="onBankClicked"
        @current-location="onCurrentLocation"
      />
    </div>

    <div class="info-panel" v-if="selectedLocation">
      <h3>선택된 위치 정보</h3>
      <div v-if="selectedBank">
        <p><strong>은행명:</strong> {{ selectedBank.place_name }}</p>
        <p><strong>주소:</strong> {{ selectedBank.address_name }}</p>
        <p v-if="selectedBank.phone"><strong>전화번호:</strong> {{ selectedBank.phone }}</p>
        <p v-if="selectedBank.distance">
          <strong>거리:</strong> {{ formatDistance(selectedBank.distance) }}
        </p>
        <div class="directions-link" v-if="selectedBank.road_address_name">
          <a :href="getKakaoMapUrl(selectedBank)" target="_blank" class="btn btn-directions">
            길찾기
          </a>
          <a :href="getNaverMapUrl(selectedBank)" target="_blank" class="btn btn-directions naver">
            네이버 지도에서 보기
          </a>
        </div>
      </div>
      <div v-else>
        <p><strong>주소:</strong> {{ selectedLocation.address }}</p>
        <p><strong>위도:</strong> {{ selectedLocation.lat }}</p>
        <p><strong>경도:</strong> {{ selectedLocation.lng }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import KakaoMap from '@/components/KakaoMap.vue'

export default {
  name: 'MapView',
  components: {
    KakaoMap,
  },
  data() {
    return {
      markers: [],
      selectedLocation: null,
      selectedBank: null,
      currentLocation: null,
    }
  },
  methods: {
    onLocationChanged(location) {
      console.log('Location changed:', location)
      this.selectedLocation = location
      this.selectedBank = null
    },

    onCurrentLocation(location) {
      this.currentLocation = location
    },

    onMarkerClicked(marker) {
      this.selectedLocation = marker
      // Check if the marker is a bank
      if (marker.place_name) {
        this.selectedBank = marker
      } else {
        this.selectedBank = null
      }
    },

    onBankClicked(bank) {
      this.selectedLocation = {
        address: bank.address_name,
        lat: bank.y,
        lng: bank.x,
      }
      this.selectedBank = bank
    },

    onMapClicked(location) {
      this.selectedLocation = {
        address: '선택한 위치',
        ...location,
      }
      this.selectedBank = null

      // We don't need to add a marker here, as the component will handle it
    },

    formatDistance(distanceInMeters) {
      if (distanceInMeters < 1000) {
        return `${distanceInMeters}m`
      } else {
        return `${(distanceInMeters / 1000).toFixed(1)}km`
      }
    },

    getKakaoMapUrl(bank) {
      return `https://map.kakao.com/link/to/${encodeURIComponent(bank.place_name)},${bank.y},${bank.x}/from/${encodeURIComponent('현재위치')},${this.currentLocation.lat},${this.currentLocation.lng}`
    },

    getNaverMapUrl(bank) {
      // Construct a Naver Maps URL with search terms
      return `https://map.naver.com/v5/search/${encodeURIComponent(bank.place_name + ' ' + bank.address_name)}`
    },

    // Helper method for saving favorite locations (can be implemented if needed)
    saveFavoriteLocation(bank) {
      console.log('Saving bank to favorites:', bank)
      // Call your API or store in local storage
    },
  },
}
</script>

<style scoped>
.map-view {
  padding: 30px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: var(--font-size-3xl);
  text-align: center;
  animation: fadeIn 0.8s ease-out;
}

.instructions {
  margin-bottom: 30px;
  color: var(--color-text);
  font-size: var(--font-size-base);
  line-height: 1.6;
  text-align: center;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  background: linear-gradient(to right, var(--color-background-start), var(--color-background-end));
  padding: 20px;
  border-radius: 10px;
  box-shadow: var(--shadow-sm);
  animation: fadeIn 1s ease-out;
}

.map-wrapper {
  margin-bottom: 30px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--color-secondary);
  animation: slideInUp 1.2s ease-out;
}

.info-panel {
  background: linear-gradient(to bottom, var(--color-background-start), var(--color-background-end));
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
  box-shadow: var(--shadow-md);
  animation: fadeIn 1.4s ease-out;
}

.info-panel h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: var(--font-size-xl);
  border-bottom: 1px solid var(--color-secondary);
  padding-bottom: 10px;
}

.info-panel p {
  margin: 12px 0;
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--color-text);
  display: flex;
  align-items: center;
}

.info-panel p strong {
  color: var(--color-accent);
  margin-right: 10px;
  min-width: 80px;
  display: inline-block;
  font-family: var(--font-heading);
}

.directions-link {
  margin-top: 25px;
  display: flex;
  gap: 15px;
}

.btn {
  display: inline-block;
  padding: 12px 20px;
  border-radius: 30px;
  text-decoration: none;
  color: var(--color-white);
  font-weight: 500;
  font-family: var(--font-body);
  transition: all var(--transition-normal);
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.btn:active {
  transform: translateY(-1px);
}

.btn-directions {
  background-color: var(--color-primary);
  position: relative;
  overflow: hidden;
}

.btn-directions::before {
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
  transition: all 0.6s;
}

.btn-directions:hover {
  background-color: var(--color-primary-dark);
}

.btn-directions:hover::before {
  left: 100%;
}

.btn-directions.naver {
  background-color: #03c75a;
}

.btn-directions.naver:hover {
  background-color: #02a54a;
}

@media (max-width: 992px) {
  h1 {
    font-size: var(--font-size-2xl);
  }
  
  .instructions {
    font-size: var(--font-size-sm);
  }
}

@media (max-width: 768px) {
  .map-view {
    padding: 20px 15px;
  }
  
  .instructions {
    padding: 15px;
  }

  .directions-link {
    flex-direction: column;
  }
  
  .info-panel {
    padding: 20px;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: var(--font-size-xl);
  }
  
  .info-panel p strong {
    min-width: 70px;
    font-size: var(--font-size-sm);
  }
}
</style>
