<template>
  <div v-if="showPhishingModal" class="phishing-modal">
    <div class="phishing-modal-content">
      <h3>⚠️ {{ phishingObject.title }}</h3>
      <p>📢 {{ phishingObject.content }}</p>
      <div class="phishing-modal-footer">
        <label class="checkbox-container">
          <input type="checkbox" v-model="doNotShowToday" />
          <span class="checkbox-text">{{ phishingObject.doNotShowToday }}</span>
        </label>
        <button class="btn btn-primary" @click="closePhishingModal">
          {{ phishingObject.closeButton }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const showPhishingModal = ref(true)
const doNotShowToday = ref(false)

const phishingObject = {
  title: '피싱 경고',
  content: '',
  doNotShowToday: '오늘 하루 보지 않기',
  closeButton: '닫기',
}

onMounted(() => {
  const lastShown = localStorage.getItem('phishingModalLastShown')
  const today = new Date().toDateString()

  if (lastShown === today) {
    showPhishingModal.value = false
  }
})

function closePhishingModal() {
  showPhishingModal.value = false

  if (doNotShowToday.value) {
    const today = new Date().toDateString()
    localStorage.setItem('phishingModalLastShown', today)
  }
}
</script>

<style scoped>
.phishing-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(3px);
}

.phishing-modal-content {
  background-color: #fff8e1;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  border: 1px solid #ffe082;
  position: relative;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.phishing-modal-content h3 {
  color: #d97706;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.phishing-modal-content p {
  color: #333333;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
}

.phishing-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-container input {
  margin-right: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #d9c99a 0%, #fef08a 100%);
  color: #333333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #fbbf24;
}
</style>
