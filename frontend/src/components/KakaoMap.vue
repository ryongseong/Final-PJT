<template>
  <div ref="mapContainer" style="width: 100%; height: 400px"></div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useMapStore } from '@/stores/map'

const mapContainer = ref(null)
const mapStore = useMapStore()

onMounted(async () => {
  await nextTick() // DOM 완전히 렌더링 후
  mapStore.waitForKakao(mapContainer.value)
})
</script>
