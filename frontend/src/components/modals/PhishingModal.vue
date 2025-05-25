<template>
  <div v-if="showModal" class="modal-backdrop" @click="closeModal">
    <div class="phishing-alert" @click.stop>
      <div class="alert-header">
        <font-awesome-icon icon="triangle-exclamation" class="warning-icon" />
        <h3>{{ $t('phishing.title').replace('⚠️', '') }}</h3>
      </div>
      <div class="alert-content">
        <p>{{ $t('phishing.content') }}</p>
        <p class="report-number">{{ $t('phishing.reportNumber') }}</p>
      </div>
      <div class="alert-footer">
        <label class="dont-show">
          <input type="checkbox" v-model="dontShowToday" />
          {{ $t('phishing.dontShowToday') }}
        </label>
        <button class="close-button" @click="closeModal">
          {{ $t('phishing.closeButton') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const showModal = ref(false)
const dontShowToday = ref(false)

const closeModal = () => {
  if (dontShowToday.value) {
    const today = new Date().toISOString().split('T')[0]
    localStorage.setItem('phishingAlertDismissed', today)
  }
  showModal.value = false
}

onMounted(() => {
  const lastDismissed = localStorage.getItem('phishingAlertDismissed')
  const today = new Date().toISOString().split('T')[0]
  
  if (lastDismissed !== today) {
    showModal.value = true
  }
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.phishing-alert {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 500px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  padding: 20px;
}

.alert-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.alert-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.warning-icon {
  color: #ff9800;
  font-size: 1.5rem;
}

.alert-content {
  margin-bottom: 20px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.report-number {
  margin-top: 10px;
  font-weight: 500;
  color: var(--accent-color);
}

.alert-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.dont-show {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  cursor: pointer;
}

.close-button {
  padding: 8px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-button:hover {
  opacity: 0.9;
}
</style> 