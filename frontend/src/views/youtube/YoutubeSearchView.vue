<!-- YouTube Search View -->
<template>
  <div class="youtube-view">
    <YoutubeSearch />
  </div>
</template>

<script>
import YoutubeSearch from '@/components/youtube/YoutubeSearch.vue'

export default {
  name: 'YoutubeSearchView',
  components: {
    YoutubeSearch,
  },
}
</script>
