<!-- filepath: /Users/ryong/git/Final-PJT/frontend/src/components/KakaoMap.vue -->
<template>
  <div>
    <div class="map-container">
      <div class="location-selector">
        <select v-model="selectedCity" @change="onCityChange">
          <option value="">시/도 선택</option>
          <option v-for="city in mapInfo" :key="city.name" :value="city.name">
            {{ city.name }}
          </option>
        </select>

        <select v-model="selectedDistrict" @change="onDistrictChange" :disabled="!selectedCity">
          <option value="">구/군 선택</option>
          <option v-for="district in districts" :key="district" :value="district">
            {{ district }}
          </option>
        </select>

        <select v-model="selectedBank" @change="searchBanks">
          <option value="">은행 선택</option>
          <option v-for="bank in bankInfo" :key="bank" :value="bank">{{ bank }}</option>
        </select>

        <button class="search-button" @click="searchNearbyBanks" :disabled="!currentLocation">
          근처 은행 검색
        </button>
      </div>

      <div id="map" ref="mapContainer"></div>

      <div class="search-results" v-if="bankSearchResults.length > 0">
        <h3>검색 결과</h3>
        <ul class="bank-list">
          <li
            v-for="(bank, index) in bankSearchResults"
            :key="index"
            @click="moveToBank(bank)"
            class="bank-item"
          >
            <div class="bank-name">{{ bank.place_name }}</div>
            <div class="bank-address">{{ bank.address_name }}</div>
            <div class="bank-distance" v-if="bank.distance">
              {{ formatDistance(bank.distance) }} 떨어져 있음
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import mapOptions from '../../mapOptions.json'

export default {
  name: 'KakaoMap',

  props: {
    initialLatitude: {
      type: Number,
      default: 37.5665, // Seoul default
    },
    initialLongitude: {
      type: Number,
      default: 126.978,
    },
    initialLevel: {
      type: Number,
      default: 3, // Zoom level
    },
    markers: {
      type: Array,
      default: () => [],
    },
  },

  data() {
    return {
      map: null,
      mapInfo: mapOptions.mapInfo,
      bankInfo: mapOptions.bankInfo,
      selectedCity: '',
      selectedDistrict: '',
      selectedBank: '',
      districts: [],
      kakaoMarkers: [],
      currentLatitude: this.initialLatitude,
      currentLongitude: this.initialLongitude,
      places: null,
      bankSearchResults: [],
      currentLocation: null,
    }
  },

  mounted() {
    // Wait for the Kakao Maps API to load
    if (window.kakao && window.kakao.maps) {
      this.initializeMap()
    } else {
      const script = document.createElement('script')
      /* global kakao */
      script.onload = () => kakao.maps.load(this.initializeMap)
      script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAPS_API_KEY}&libraries=services,clusterer,drawing&autoload=false`
      document.head.appendChild(script)
    }
  },

  methods: {
    initializeMap() {
      const container = this.$refs.mapContainer
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.currentLatitude = position.coords.latitude
          this.currentLongitude = position.coords.longitude
          this.currentLocation = {
            lat: this.currentLatitude,
            lng: this.currentLongitude,
          }

          this.$emit('current-location', this.currentLocation)

          if (this.map) {
            const newCenter = new kakao.maps.LatLng(this.currentLatitude, this.currentLongitude)
            this.map.setCenter(newCenter)

            // Add a marker for current location
            this.addMarker({
              lat: this.currentLatitude,
              lng: this.currentLongitude,
              content: '<div style="padding:5px;">현재 위치</div>',
            })
          }
        },
        () => {
          console.error('Unable to retrieve your location')
        },
      )

      const options = {
        center: new kakao.maps.LatLng(this.currentLatitude, this.currentLongitude),
        level: this.initialLevel,
      }

      this.map = new kakao.maps.Map(container, options)

      // Initialize places service
      this.places = new kakao.maps.services.Places()

      // Add markers if provided
      if (this.markers && this.markers.length > 0) {
        this.addMarkers(this.markers)
      }

      // Add a marker for current location right after map initialization
      const currentLocationMarker = {
        lat: this.currentLatitude,
        lng: this.currentLongitude,
        content: '<div style="padding:5px;">현재 위치</div>',
      }
      this.addMarker(currentLocationMarker)

      // Add event listener for map click
      kakao.maps.event.addListener(this.map, 'click', (mouseEvent) => {
        const latlng = mouseEvent.latLng

        this.currentLocation = {
          lat: latlng.getLat(),
          lng: latlng.getLng(),
        }

        this.$emit('map-clicked', this.currentLocation)
      })
    },

    onCityChange() {
      if (this.selectedCity) {
        const cityData = this.mapInfo.find((city) => city.name === this.selectedCity)
        this.districts = cityData ? cityData.countries : []
        this.selectedDistrict = ''

        // Search for the city coordinates and move the map
        this.searchAndMoveToLocation(this.selectedCity)

        // If a bank is selected, search for banks in the new city
        if (this.selectedBank) {
          this.searchBanks()
        }
      } else {
        this.districts = []
        this.selectedDistrict = ''
      }
    },

    onDistrictChange() {
      if (this.selectedDistrict) {
        // Search for the district coordinates and move the map
        const searchTerm =
          this.selectedCity && this.selectedDistrict
            ? `${this.selectedCity} ${this.selectedDistrict}`
            : this.selectedDistrict

        this.searchAndMoveToLocation(searchTerm)

        // If a bank is selected, search for banks in the new district
        if (this.selectedBank) {
          this.searchBanks()
        }
      }
    },

    searchAndMoveToLocation(searchTerm) {
      if (!searchTerm || !this.map) return

      const geocoder = new kakao.maps.services.Geocoder()

      geocoder.addressSearch(searchTerm, (result, status) => {
        if (status === kakao.maps.services.Status.OK) {
          const coords = new kakao.maps.LatLng(result[0].y, result[0].x)

          // Update current location
          this.currentLocation = {
            lat: coords.getLat(),
            lng: coords.getLng(),
          }

          // Move the map to the location
          this.map.setCenter(coords)

          // Adjust zoom level based on whether it's a city or district
          if (this.selectedDistrict) {
            this.map.setLevel(5) // Closer zoom for districts
          } else {
            this.map.setLevel(7) // Wider zoom for cities
          }

          // Clear previous markers except the current location marker
          this.clearMarkers()

          // Add a marker for the selected location
          this.addMarker({
            lat: coords.getLat(),
            lng: coords.getLng(),
            content: `<div style="padding:5px;">${searchTerm}</div>`,
          })

          this.$emit('location-changed', {
            address: searchTerm,
            lat: coords.getLat(),
            lng: coords.getLng(),
          })
        }
      })
    },

    addMarkers(markerData) {
      // Clear existing markers
      this.clearMarkers()

      // Add new markers
      markerData.forEach((marker) => {
        const position = new kakao.maps.LatLng(marker.lat, marker.lng)

        const markerObj = new kakao.maps.Marker({
          position: position,
          map: this.map,
        })

        // If marker has content, add an info window
        if (marker.content) {
          const infoWindow = new kakao.maps.InfoWindow({
            content: marker.content,
          })

          kakao.maps.event.addListener(markerObj, 'click', () => {
            infoWindow.open(this.map, markerObj)
            this.$emit('marker-clicked', marker)
          })
        } else {
          kakao.maps.event.addListener(markerObj, 'click', () => {
            this.$emit('marker-clicked', marker)
          })
        }

        this.kakaoMarkers.push(markerObj)
      })
    },

    clearMarkers() {
      this.kakaoMarkers.forEach((marker) => {
        marker.setMap(null)
      })
      this.kakaoMarkers = []
    },

    // Public method to add a new marker programmatically
    addMarker(markerData) {
      const position = new kakao.maps.LatLng(markerData.lat, markerData.lng)

      const markerObj = new kakao.maps.Marker({
        position: position,
        map: this.map,
      })

      if (markerData.content) {
        const infoWindow = new kakao.maps.InfoWindow({
          content: markerData.content,
        })

        kakao.maps.event.addListener(markerObj, 'click', () => {
          infoWindow.open(this.map, markerObj)
          this.$emit('marker-clicked', markerData)
        })
      }

      this.kakaoMarkers.push(markerObj)
      return markerObj
    },

    // Update map size if container changes
    updateMapSize() {
      if (this.map) {
        setTimeout(() => {
          this.map.relayout()
        }, 100)
      }
    },

    // Search for banks based on the selected bank name
    searchBanks() {
      if (!this.selectedBank || !this.map) return

      let searchTerm = this.selectedBank

      // If a location is selected, include it in the search term
      if (this.selectedCity) {
        searchTerm = `${this.selectedCity} ${this.selectedBank}`

        if (this.selectedDistrict) {
          searchTerm = `${this.selectedCity} ${this.selectedDistrict} ${this.selectedBank}`
        }
      }

      this.searchForPlaces(searchTerm)
    },

    // Search for nearby banks based on current location
    searchNearbyBanks() {
      if (!this.currentLocation || !this.map) return

      let searchTerm = this.selectedBank || '은행'

      // Create a places search object
      const placesSearchCB = (result, status) => {
        if (status === kakao.maps.services.Status.OK) {
          this.clearMarkers()
          this.handlePlacesSearchResult(result)
        } else {
          console.error('Places search failed:', status)
          this.bankSearchResults = []
        }
      }

      // Search nearby using the location coordinates
      this.places.keywordSearch(searchTerm, placesSearchCB, {
        location: new kakao.maps.LatLng(this.currentLocation.lat, this.currentLocation.lng),
        radius: 5000, // Search within 5km
        sort: kakao.maps.services.SortBy.DISTANCE, // Sort by distance
      })
    },

    // Handle search result
    searchForPlaces(keyword) {
      if (!keyword || !this.map) return

      // Create a places search object
      const placesSearchCB = (result, status) => {
        if (status === kakao.maps.services.Status.OK) {
          this.clearMarkers()
          this.handlePlacesSearchResult(result)
        } else {
          console.error('Places search failed:', status)
          this.bankSearchResults = []
        }
      }

      // Execute the search
      this.places.keywordSearch(keyword, placesSearchCB)
    },

    // Process bank search results
    handlePlacesSearchResult(places) {
      // Save search results
      this.bankSearchResults = places

      // Create bounds to fit all markers
      const bounds = new kakao.maps.LatLngBounds()

      // Add markers for all places
      places.forEach((place) => {
        const position = new kakao.maps.LatLng(place.y, place.x)
        bounds.extend(position)

        // Create marker
        const marker = new kakao.maps.Marker({
          position: position,
          map: this.map,
        })

        // Create content for info window
        const content = `
          <div style="padding:5px;min-width:200px;">
            <h3 style="margin:5px 0;">${place.place_name}</h3>
            <p style="margin:5px 0;">${place.address_name}</p>
            ${place.phone ? `<p style="margin:5px 0;">전화: ${place.phone}</p>` : ''}
            ${place.distance ? `<p style="margin:5px 0;">거리: ${this.formatDistance(place.distance)}</p>` : ''}
          </div>
        `

        // Create info window
        const infoWindow = new kakao.maps.InfoWindow({
          content: content,
          removable: true,
        })

        // Add click event to marker
        kakao.maps.event.addListener(marker, 'click', () => {
          infoWindow.open(this.map, marker)
          this.$emit('bank-clicked', place)
        })

        this.kakaoMarkers.push(marker)
      })

      // Adjust map to show all markers
      this.map.setBounds(bounds)
    },

    // Move to the selected bank
    moveToBank(bank) {
      if (!bank || !this.map) return

      const position = new kakao.maps.LatLng(bank.y, bank.x)
      this.map.setCenter(position)
      this.map.setLevel(2) // Zoom in

      // Find the marker for this bank and trigger its click event
      const marker = this.kakaoMarkers.find(
        (marker) =>
          marker.getPosition().getLat() === parseFloat(bank.y) &&
          marker.getPosition().getLng() === parseFloat(bank.x),
      )

      if (marker) {
        // Simulate click on this marker
        kakao.maps.event.trigger(marker, 'click')
      }
    },

    // Format distance in meters to a more readable format
    formatDistance(distanceInMeters) {
      if (distanceInMeters < 1000) {
        return `${distanceInMeters}m`
      } else {
        return `${(distanceInMeters / 1000).toFixed(1)}km`
      }
    },
  },

  watch: {
    markers: {
      handler(newMarkers) {
        if (this.map && newMarkers) {
          this.addMarkers(newMarkers)
        }
      },
      deep: true,
    },
  },
}
</script>

<style scoped>
.map-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.location-selector {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  background: linear-gradient(to right, var(--color-background-start), var(--color-background-end));
  padding: 20px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.location-selector select {
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid var(--color-secondary);
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  min-width: 180px;
  background-color: var(--color-white);
  color: var(--color-text);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23A38D77' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 30px;
}

.location-selector select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(163, 141, 119, 0.2);
}

.location-selector select:disabled {
  background-color: var(--color-secondary);
  opacity: 0.7;
  cursor: not-allowed;
}

.search-button {
  padding: 10px 20px;
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  font-weight: 500;
  transition: all var(--transition-normal);
  min-width: 150px;
  box-shadow: var(--shadow-sm);
}

.search-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.search-button:active:not(:disabled) {
  transform: translateY(0);
}

.search-button:disabled {
  background-color: var(--color-secondary);
  color: var(--color-text-light);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

#map {
  width: 100%;
  height: 550px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  margin-bottom: 30px;
  border: 2px solid var(--color-secondary);
}

.search-results {
  background: linear-gradient(to bottom, var(--color-background-start), var(--color-background-end));
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
  box-shadow: var(--shadow-md);
  animation: fadeIn var(--transition-normal);
}

.search-results h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: var(--font-size-xl);
  border-bottom: 1px solid var(--color-secondary);
  padding-bottom: 10px;
}

.bank-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
  border-radius: 8px;
  background-color: var(--color-white);
  box-shadow: var(--shadow-sm);
}

.bank-list::-webkit-scrollbar {
  width: 8px;
}

.bank-list::-webkit-scrollbar-track {
  background: var(--color-secondary);
  border-radius: 10px;
}

.bank-list::-webkit-scrollbar-thumb {
  background-color: var(--color-primary);
  border-radius: 10px;
}

.bank-item {
  padding: 15px 20px;
  border-bottom: 1px solid var(--color-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.bank-item:last-child {
  border-bottom: none;
}

.bank-item:hover {
  background-color: var(--color-background-start);
  transform: translateX(5px);
}

.bank-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background-color: transparent;
  transition: background-color var(--transition-fast);
}

.bank-item:hover::before {
  background-color: var(--color-primary);
}

.bank-name {
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: var(--font-size-base);
}

.bank-address {
  font-size: var(--font-size-sm);
  color: var(--color-text);
  margin-bottom: 6px;
  font-family: var(--font-body);
}

.bank-distance {
  font-size: var(--font-size-xs);
  color: var(--color-text-light);
  font-style: italic;
  display: flex;
  align-items: center;
}

.bank-distance::before {
  content: "📍";
  margin-right: 5px;
  font-style: normal;
}

/* Responsive styles */
@media (max-width: 768px) {
  .location-selector {
    flex-direction: column;
    gap: 10px;
  }
  
  .location-selector select,
  .search-button {
    width: 100%;
    min-width: 0;
  }
  
  #map {
    height: 400px;
  }
}

@media (max-width: 480px) {
  .search-results {
    padding: 15px;
  }
  
  .bank-item {
    padding: 12px 15px;
  }
  
  #map {
    height: 350px;
  }
}
</style>
