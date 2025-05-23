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
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 10px;
  color: #333;
}

.instructions {
  margin-bottom: 20px;
  color: #666;
  font-size: 16px;
  line-height: 1.5;
}

.map-wrapper {
  margin-bottom: 20px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-panel {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-panel h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.info-panel p {
  margin: 10px 0;
  font-size: 15px;
  line-height: 1.5;
}

.directions-link {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.btn {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  color: white;
  font-weight: 500;
  transition: background-color 0.3s;
  text-align: center;
}

.btn-directions {
  background-color: #f9a825;
}

.btn-directions:hover {
  background-color: #f57f17;
}

.btn-directions.naver {
  background-color: #03c75a;
}

.btn-directions.naver:hover {
  background-color: #02a54a;
}

@media (max-width: 768px) {
  .map-view {
    padding: 10px;
  }

  .directions-link {
    flex-direction: column;
  }
}
</style>
