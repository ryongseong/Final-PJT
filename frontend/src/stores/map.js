import { defineStore } from 'pinia'

export const useMapStore = defineStore('map', () => {
  const waitForKakao = (container) => {
    if (!container) {
      console.warn('Map container is not ready yet')
      return
    }

    if (window.kakao && window.kakao.maps) {
      const options = {
        center: new window.kakao.maps.LatLng(37.5665, 126.978),
        level: 3,
      }
      new window.kakao.maps.Map(container, options)
    } else {
      setTimeout(() => waitForKakao(container), 100)
    }
  }

  return {
    waitForKakao,
  }
})
