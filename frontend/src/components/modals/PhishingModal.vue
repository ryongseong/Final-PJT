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
// import { useI18n } from 'vue-i18n' // 주석 처리 또는 삭제

// const { t } = useI18n() // 주석 처리 또는 삭제
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
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: var(--overlay-bg, rgba(0, 0, 0, 0.7));
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.phishing-alert {
  width: 90%;
  max-width: 500px;
  background: var(--modal-bg, var(--card-bg));
  border-radius: var(--modal-border-radius, var(--card-border-radius, 12px));
  box-shadow: var(--shadow-xl, 0 10px 25px rgba(0,0,0,0.2));
  border: 1px solid var(--modal-border, var(--card-border));
  z-index: 1000;
  padding: var(--spacing-xl, 1.5rem);
  font-family: var(--font-body);
}

.alert-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-lg, 1.25rem);
  gap: var(--spacing-md, 0.75rem);
}

.warning-icon {
  font-size: var(--icon-size-xl, 1.8rem);
  color: var(--warning-color-icon, #f97316);
}

.alert-header h3 {
  font-size: var(--font-size-xl, 1.4rem);
  color: var(--text-primary);
  font-weight: 700;
  margin: 0;
  font-family: var(--font-heading);
}

.alert-content p {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md, 1rem);
  line-height: 1.6;
  font-size: var(--font-size-md, 1rem);
}

.alert-content p.report-number {
  font-weight: 600;
  color: var(--warning-color-text, var(--accent-color));
  background-color: var(--warning-color-bg-light, rgba(249, 115, 22, 0.1));
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 0.75rem);
  border-radius: var(--border-radius-sm, 6px);
  text-align: center;
  margin-top: var(--spacing-md, 1rem);
}

.alert-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-lg, 1.5rem);
  padding-top: var(--spacing-lg, 1.25rem);
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.dont-show {
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  font-size: var(--font-size-sm, 0.9rem);
  cursor: pointer;
}

.dont-show input[type="checkbox"] {
  margin-right: var(--spacing-sm, 0.5rem);
  accent-color: var(--accent-color);
}

.alert-footer .close-button {
  padding: var(--button-padding-y, 0.6rem) var(--button-padding-x, 1.2rem);
  font-size: var(--button-font-size, 0.95rem);
  font-weight: 500;
  background-color: var(--button-bg, var(--accent-color));
  color: var(--button-text, #FFFFFF);
  border: 1px solid transparent;
  border-radius: var(--button-border-radius, var(--border-radius-md, 8px));
  cursor: pointer;
  transition: background-color var(--transition-speed), opacity var(--transition-speed);
}

.alert-footer .close-button:hover {
  background-color: var(--button-hover, var(--accent-hover));
  opacity: 0.9;
}
</style> 