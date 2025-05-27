<!-- Saved Videos View -->
<template>
  <div class="saved-videos-view">
    <SavedVideos />
  </div>
</template>

<script>
import SavedVideos from '@/components/youtube/SavedVideos.vue'

export default {
  name: 'SavedVideosView',
  components: {
    SavedVideos,
  },
}
</script>
