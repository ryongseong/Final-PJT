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

    <div class="map-content-area">
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
          <div class="directions-link" v-if="selectedBank.y && selectedBank.x">
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

    onMarkerClicked(markerData) {
      // Ensure lat/lng are present, falling back to y/x if available from older structures
      const lat = markerData.lat || markerData.y;
      const lng = markerData.lng || markerData.x;

      // Standardize selectedLocation for all marker clicks
      this.selectedLocation = {
        address: markerData.address_name || markerData.place_name || markerData.title || '주소 정보 없음',
        lat: lat,
        lng: lng,
      };

      // If it's a bank or has a place_name, treat it as a selectable entity for directions
      if (markerData.place_name && lat && lng) {
        this.selectedBank = {
          place_name: markerData.place_name,
          // Ensure address_name has a fallback if not directly provided
          address_name: markerData.address_name || markerData.road_address_name || '상세 주소 정보 없음',
          road_address_name: markerData.road_address_name, // Keep for potential display or specific use
          phone: markerData.phone || '',
          distance: markerData.distance,
          y: lat, // Use consistent lat for y
          x: lng, // Use consistent lng for x
        };
      } else if (lat && lng) {
        // If not a bank (no place_name) but has coordinates, allow directions to this point
        // This primarily handles the case where a generic map click was treated as a marker click
        // or a marker without detailed place information was clicked.
        this.selectedBank = {
          place_name: markerData.title || '선택된 위치',
          address_name: this.selectedLocation.address, // Use address from selectedLocation
          road_address_name: '',
          phone: '',
          y: lat,
          x: lng,
        };
      } else {
        // If no coordinates, cannot show directions
        this.selectedBank = null;
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
        lat: location.lat,
        lng: location.lng,
      };

      this.selectedBank = {
        place_name: '선택한 위치',
        address_name: location.address || '상세 주소 없음',
        road_address_name: location.address || '상세 주소 없음',
        y: location.lat,
        x: location.lng,
      };

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
  padding: 2rem; /* Consistent padding */
  max-width: 1200px;
  margin: 0 auto;
  font-family: var(--font-family-base); /* Apply global font */
  color: var(--text-primary);
  background-color: var(--background-primary); /* Ensure view has background */
  display: flex; /* Make map-view a flex container */
  flex-direction: column; /* Stack children vertically by default */
}

.map-view h1 {
  font-family: 'Pretendard Variable', serif; /* Title font */
  font-size: 2.2rem;
  color: var(--text-primary);
  margin-bottom: 1rem; /* Consistent margin */
  text-align: center; /* Center title */
}

.instructions {
  margin-bottom: 2rem; /* Increased margin */
  color: var(--text-secondary);
  font-size: 1rem; /* Standardized font size */
  line-height: 1.6;
  background-color: var(--card-bg); /* Card style for instructions */
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
}

.map-content-area {
  display: flex;
  flex-direction: column; /* Default to vertical stacking */
  gap: 2rem; /* Gap between map and info panel */
  flex-grow: 1; /* Allow this area to grow */
}

.map-wrapper {
  margin-bottom: 0; /* Removed bottom margin as gap is handled by flex */
  border-radius: var(--border-radius-lg); /* Consistent border radius */
  overflow: hidden;
  box-shadow: var(--card-shadow); /* Consistent shadow */
  border: 1px solid var(--card-border); /* Consistent border */
  /* height: 60vh; Fixed height for map - We might need to make this flexible */
  min-height: 400px;
  flex-shrink: 0; /* Prevent map from shrinking too much in flex layout */
}

.info-panel {
  background-color: var(--card-bg); /* Use card background */
  border-radius: var(--border-radius-lg);
  padding: 1.5rem; /* Consistent padding */
  margin-top: 0; /* Removed top margin as gap is handled by flex */
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  overflow-y: auto; /* Allow vertical scrolling if content overflows */
  max-height: 60vh; /* Example max-height, can be adjusted */
  flex-grow: 1; /* Allow info panel to take available space */
}

.info-panel h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color); /* Use theme border color */
  padding-bottom: 0.8rem;
  font-size: 1.5rem; /* Adjusted font size */
  font-weight: 600;
}

.info-panel p {
  margin: 0.8rem 0;
  font-size: 0.95rem; /* Standardized font size */
  line-height: 1.6;
  color: var(--text-secondary);
}

.info-panel p strong {
  color: var(--text-primary);
  font-weight: 600;
}

.directions-link {
  margin-top: 1.5rem;
  display: flex;
  gap: 0.8rem; /* Consistent gap */
}

/* Using global .action-btn styles if available, otherwise defining similar ones */
.btn.btn-directions {
  /* Assuming .action-btn and .primary-btn, .secondary-btn from variables.css might apply */
  /* For demonstration, specific styles that mimic the theme are below */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius-md);
  text-decoration: none;
  font-weight: 500;
  transition: background-color var(--transition-speed), border-color var(--transition-speed), color var(--transition-speed);
  text-align: center;
  font-size: 0.9rem;
  border: 1px solid transparent;
  cursor: pointer;
}

.btn-directions {
  background-color: var(--accent-color); /* Theme accent color */
  color: var(--button-text);
  border-color: var(--accent-color);
}

.btn-directions:hover {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.btn-directions.naver {
  background-color: var(--background-primary); /* Use a secondary button style */
  color: var(--text-primary);
  border-color: var(--border-color);
}

.btn-directions.naver:hover {
  background-color: var(--border-color);
  color: var(--text-primary);
  border-color: var(--accent-hover); /* Or slightly darker border */
}

/* @media (min-width: 992px) { 
  .map-content-area {
    flex-direction: row; 
  }
  .map-wrapper {
    flex: 2; 
    height: auto; 
     min-height: 500px; 
  }
  .info-panel {
    flex: 1; 
    max-height: none; 
     align-self: flex-start; 
  }
} */

@media (max-width: 768px) {
  .map-view {
    padding: 1rem; /* Adjust padding for mobile */
  }

  .map-view h1 {
    font-size: 1.8rem; /* Adjust title size for mobile */
  }

  .instructions {
    padding: 1rem;
  }

  .map-wrapper {
    height: 50vh; /* Adjust map height for mobile */
  }

  .info-panel {
    padding: 1rem;
  }

  .info-panel h3 {
    font-size: 1.3rem;
  }

  .directions-link {
    flex-direction: column;
  }

  .btn.btn-directions {
    width: 100%; /* Full width buttons on mobile */
  }
}
</style>
