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
      kakaoOverlays: [],
      activeOverlay: null,
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
      script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_API}&libraries=services,clusterer,drawing&autoload=false`
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

            // Add a marker and custom overlay for current location
            this.addMarkerWithCustomOverlay({
              lat: this.currentLatitude,
              lng: this.currentLongitude,
              content: '<div style="padding: 8px 12px; background-color: rgba(255, 255, 255, 0.9); color: #333; font-size: 13px; font-weight: 600; text-align: center; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin: 0;">현재 위치</div>',
              title: 'currentLocation',
              yAnchor: 2.0 // Adjust to position slightly more above the marker
            });
          } else {
            // Map is not yet initialized
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

      // Check if a current location marker already exists to prevent duplicates
      const existingCurrentLocationMarker = this.kakaoMarkers.find(m => m.getTitle && m.getTitle() === 'currentLocation');

      if (!existingCurrentLocationMarker) {
        this.addMarkerWithCustomOverlay({
          lat: this.currentLatitude, 
          lng: this.currentLongitude,
          content: '<div style="padding: 8px 12px; background-color: rgba(255, 255, 255, 0.9); color: #333; font-size: 13px; font-weight: 600; text-align: center; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin: 0;">현재 위치</div>',
          title: 'currentLocation',
          yAnchor: 2.0 // Adjust to position slightly more above the marker
        });
      }

      // Add event listener for map click (to close active overlay)
      kakao.maps.event.addListener(this.map, 'click', (mouseEvent) => {
        if (this.activeOverlay) {
          this.activeOverlay.setMap(null);
          this.activeOverlay = null;
        }
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
          this.clearOverlays()

          // Add a marker and custom overlay for the selected location
          this.addMarkerWithCustomOverlay({
            lat: coords.getLat(),
            lng: coords.getLng(),
            content: `<div style="padding: 8px 12px; background-color: rgba(255, 255, 255, 0.9); color: #333; font-size: 13px; font-weight: 600; text-align: center; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin: 0;">${searchTerm}</div>`,
            title: 'searchLocation',
            yAnchor: 2.0 // Adjust to position slightly more above the marker
          });

          this.$emit('location-changed', {
            address: searchTerm,
            lat: coords.getLat(),
            lng: coords.getLng(),
          })
        }
      })
    },

    addMarkers(markerDataArray) {
      this.clearMarkers();
      this.clearOverlays();

      markerDataArray.forEach((markerData) => {
        this.addMarkerWithCustomOverlay(markerData);
      });
    },

    clearMarkers() {
      this.kakaoMarkers.forEach((marker) => {
        marker.setMap(null);
      });
      this.kakaoMarkers = [];
    },

    clearOverlays() {
      this.kakaoOverlays.forEach((overlay) => {
        overlay.setMap(null);
      });
      this.kakaoOverlays = [];
      if (this.activeOverlay) {
        this.activeOverlay.setMap(null);
        this.activeOverlay = null;
      }
    },

    // New method to add marker with CustomOverlay
    addMarkerWithCustomOverlay(markerData) {
      const position = new kakao.maps.LatLng(markerData.lat, markerData.lng);

      const markerObj = new kakao.maps.Marker({
        position: position,
        map: this.map,
        title: markerData.title || undefined
      });

      if (markerData.content) {
        let finalContent; 
        if (typeof markerData.content === 'string') {
          const originalContent = markerData.content;
          const trimmedContentForCheck = originalContent.trim();

          if (trimmedContentForCheck.includes('class="custom-overlay-bank-detail"')) {
            // Bank detail HTML from handlePlacesSearchResult - use as is
            finalContent = originalContent; 
          } else if (trimmedContentForCheck.startsWith('<div style="padding:')) {
            // Simple styled content like "현재 위치" or selected search location - use as is
            finalContent = originalContent;
          } else {
            // Fallback for plain text or unknown HTML structure: strip HTML and wrap in default style
            const textOnly = trimmedContentForCheck.replace(/<[^>]+>/g, '').trim();
            if (textOnly) {
              finalContent = `<div style="padding: 8px 12px; background-color: rgba(255, 255, 255, 0.9); color: #333; font-size: 13px; font-weight: 600; text-align: center; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin: 0;">${textOnly}</div>`;
            } else {
              finalContent = ''; // Avoid creating an overlay for empty content
            }
          }
        } else {
          // If markerData.content is not a string (e.g. already a DOM element)
          finalContent = markerData.content;
        }

        // Ensure customOverlay is only created if finalContent is truthy and not just whitespace
        if (finalContent && String(finalContent).trim() !== '') {
          const customOverlay = new kakao.maps.CustomOverlay({
            content: finalContent,
            position: position,
            xAnchor: 0.5,
            yAnchor: markerData.yAnchor || 1.5, 
            zIndex: 3
          });
          
          customOverlay.setMap(null); // Initially hide the overlay

          kakao.maps.event.addListener(markerObj, 'click', () => {
            // If there's an active overlay and it's different from the current one, hide it.
            if (this.activeOverlay && this.activeOverlay !== customOverlay) {
              this.activeOverlay.setMap(null);
            }
            
            // Toggle visibility of the current overlay
            if (customOverlay.getMap()) {
              customOverlay.setMap(null);
              // If we are hiding the currently active overlay, clear activeOverlay
              if (this.activeOverlay === customOverlay) {
                this.activeOverlay = null;
              }
            } else {
              customOverlay.setMap(this.map);
              this.activeOverlay = customOverlay;
            }
            this.$emit('marker-clicked', markerData);
          });
          this.kakaoOverlays.push(customOverlay); // Store overlay
        }
      }
      this.kakaoMarkers.push(markerObj);
      return markerObj;
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
      this.clearMarkers(); // Clear existing markers
      this.clearOverlays(); // Clear existing overlays

      this.bankSearchResults = places;
      const bounds = new kakao.maps.LatLngBounds();

      places.forEach((place) => {
        const position = new kakao.maps.LatLng(place.y, place.x);
        bounds.extend(position);

        // Ensure place_name, address_name are defined to prevent 'undefined' in content string
        const placeName = place.place_name || '이름 정보 없음';
        const addressName = place.address_name || '주소 정보 없음';

        let content = `
          <div class="custom-overlay-bank-detail" style="display: flex; flex-direction: column; background-color:white; border-radius:8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); width:320px; max-height:250px; font-family: 'Malgun Gothic', Dotum, '돋움', sans-serif; line-height:1.5;">
            <div style="padding:12px 16px; background-color:#f0f2f5; border-bottom:1px solid #e0e3e8; border-top-left-radius:8px; border-top-right-radius:8px; display:flex; justify-content:space-between; align-items:center;">
              <h5 style="margin:0; font-size:17px; font-weight:600; color:#1c1e21;">${placeName}</h5>
              <button onclick="this.closest('.custom-overlay-bank-detail').style.display='none'; event.stopPropagation();" style="background:transparent; border:none; font-size:20px; color:#606770; cursor:pointer; padding:0; line-height:1;">×</button>
            </div>
            <div style="padding:16px; overflow-y:auto; flex-grow:1;">
              <p style="margin:0 0 8px 0; font-size:14px; color:#333;">
                <span style="color:#606770; display:inline-block; width:20px; text-align:center; margin-right:5px;">📍</span>${addressName}
              </p>
              ${place.phone ? `<p style="margin:0 0 8px 0; font-size:14px; color:#333;"><span style="color:#606770; display:inline-block; width:20px; text-align:center; margin-right:5px;">📞</span>${place.phone}</p>` : ''}
              ${place.distance ? `<p style="margin:0; font-size:14px; color:#333;"><span style="color:#606770; display:inline-block; width:20px; text-align:center; margin-right:5px;">🚶</span>${this.formatDistance(place.distance)}</p>` : ''}
            </div>
          </div>
        `; // Removed .replace(/\n\s*/g, '') to preserve newlines in the template literal

        this.addMarkerWithCustomOverlay({
            lat: place.y,
            lng: place.x,
            content: content, // Use the content string directly
            title: placeName,
            yAnchor: 1.6 // Slightly adjust yAnchor for bank details card
        });
      });

      if (places.length > 0) {
        this.map.setBounds(bounds);
      }
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
  overflow-y: auto;
}

.location-selector {
  margin-bottom: var(--spacing-md, 1rem);
  display: flex;
  gap: var(--spacing-sm, 0.5rem);
  flex-wrap: wrap;
  padding: var(--spacing-sm, 0.5rem);
  background-color: var(--background-secondary, #f0f0f0);
  border-radius: var(--border-radius-md, 6px);
}

.location-selector select {
  padding: var(--input-padding-y, 0.5rem) var(--input-padding-x, 0.75rem);
  border-radius: var(--input-border-radius, 4px);
  border: 1px solid var(--border-color, #ccc);
  font-size: var(--font-size-sm, 0.9rem);
  min-width: 150px;
  background-color: var(--input-bg, #fff);
  color: var(--input-text);
  flex-grow: 1;
}

.search-button {
  padding: var(--button-padding-y, 0.5rem) var(--button-padding-x, 1rem);
  background-color: var(--button-bg, var(--accent-color));
  color: var(--button-text, #fff);
  border: none;
  border-radius: var(--button-border-radius, 4px);
  cursor: pointer;
  font-size: var(--font-size-sm, 0.9rem);
  transition: background-color 0.3s;
  flex-grow: 0;
}

.search-button:hover:not(:disabled) {
  background-color: var(--button-hover-bg, var(--accent-hover));
}

.search-button:disabled {
  background-color: var(--button-disabled-bg, #cccccc);
  color: var(--button-disabled-text, #888888);
  cursor: not-allowed;
  opacity: 0.7;
}

#map {
  width: 100%;
  height: 500px;
  border-radius: var(--border-radius-lg, 8px);
  overflow: hidden;
  box-shadow: var(--card-shadow, 0 2px 8px rgba(0, 0, 0, 0.1));
  margin-bottom: var(--spacing-lg, 1.5rem);
}

.search-results {
  width: 100%;
  background-color: var(--card-bg, #fff);
  padding: var(--spacing-lg, 1.5rem);
  border-radius: var(--border-radius-lg, 8px);
  box-shadow: var(--card-shadow, 0 2px 10px rgba(0, 0, 0, 0.1));
  max-height: 350px;
  overflow-y: auto;
}

.search-results h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-md, 1rem);
  font-size: var(--font-size-lg, 1.2rem);
  color: var(--text-primary, #333);
  font-weight: 600;
  border-bottom: 1px solid var(--border-color, #eee);
  padding-bottom: var(--spacing-sm, 0.5rem);
}

.bank-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.bank-item {
  padding: var(--spacing-md, 1rem) var(--spacing-sm, 0.75rem);
  border-bottom: 1px solid var(--border-color-light, #f0f0f0);
  cursor: pointer;
  transition: background-color var(--transition-speed, 0.2s);
}

.bank-item:last-child {
  border-bottom: none;
}

.bank-item:hover {
  background-color: var(--background-secondary-hover, #f0f0f0);
}

.bank-name {
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: var(--spacing-xs, 0.25rem);
  font-size: var(--font-size-md, 1rem);
}

.bank-address {
  font-size: var(--font-size-sm, 0.9rem);
  color: var(--text-secondary, #666);
  margin-bottom: var(--spacing-xs, 0.25rem);
}

.bank-distance {
  font-size: var(--font-size-xs, 0.8rem);
  color: var(--accent-color, #007bff);
}

/* Explicit dark mode styling for search results text */
::v-deep .dark .search-results h3,
::v-deep .dark .bank-list .bank-item .bank-name {
  color: var(--text-primary); /* Uses light color from variables.css in dark mode */
}

::v-deep .dark .bank-list .bank-item .bank-address {
  color: var(--text-secondary); /* Uses light color from variables.css in dark mode */
}

/* Explicit dark mode styling for location selector and search button */
::v-deep .dark .location-selector select {
  background-color: var(--input-bg);
  color: var(--input-text);
  border-color: var(--input-border);
}

/* To ensure select dropdown options also follow dark theme (browser dependent) */
::v-deep .dark .location-selector select option {
  background-color: var(--input-bg);
  color: var(--input-text);
}

::v-deep .dark .search-button {
  background-color: var(--button-secondary-bg);
  color: var(--button-secondary-text);
  border: 1px solid var(--button-secondary-border);
}

::v-deep .dark .search-button:hover:not(:disabled) {
  background-color: var(--button-secondary-hover-bg);
  border-color: var(--button-secondary-border); /* Keep border consistent or use hover border if defined */
}

::v-deep .dark .search-button:disabled {
  background-color: var(--button-disabled-bg, #4a4a4a); /* Using a specific dark disabled bg */
  color: var(--button-disabled-text, #888888);
  opacity: 0.5;
}

/* Kakao InfoWindow Customization */
/* All custom styling is now INLINE within the 'content' HTML strings. */
/* CSS classes like .custom-infowindow, .card-style, .card-header, etc., are NO LONGER USED. */
/* .kakao-infowindow-content might only act as a very basic fallback if some unstyled string gets through. */

.kakao-infowindow-content { /* Minimal fallback styling */
  padding: 8px;
  background-color: white;
  color: black;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  font-size:14px; /* ensure basic readability */
}

.kakao-infowindow-content p {
  color: black !important;
  margin: 0;
}

.kakao-infowindow-content h5.infowindow-title {
  font-size: 1rem;
  font-weight: 700;
  color: black !important;
  margin: 0 0 4px 0;
}

/* All previously defined classes for infowindow styling like:
   .infowindow-current-location,
   .infowindow-selected-location,
   .custom-infowindow.card-style,
   .custom-infowindow .card-header,
   .custom-infowindow .card-title,
   .custom-infowindow .card-body,
   .custom-infowindow .card-text,
   .custom-infowindow .infowindow-phone
   ARE NOW REMOVED as styles are inline. */
</style>
