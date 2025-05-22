<template>
  <div class="join-methods">
    <div v-if="showLabel" class="join-label">가입 방법:</div>
    <div class="join-badges">
      <span v-if="hasJoinWay('1')" class="join-badge">
        <i class="fas fa-building"></i>
        <span v-if="showText">영업점</span>
      </span>
      <span v-if="hasJoinWay('2')" class="join-badge">
        <i class="fas fa-laptop"></i>
        <span v-if="showText">인터넷</span>
      </span>
      <span v-if="hasJoinWay('3')" class="join-badge">
        <i class="fas fa-phone"></i>
        <span v-if="showText">전화</span>
      </span>
      <span v-if="hasJoinWay('4')" class="join-badge">
        <i class="fas fa-mobile-alt"></i>
        <span v-if="showText">모바일</span>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JoinMethods',
  props: {
    joinWay: {
      type: String,
      required: true
    },
    showLabel: {
      type: Boolean,
      default: true
    },
    showText: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    hasJoinWay(code) {
      if (!this.joinWay) return false;
      return this.joinWay.includes(code);
    }
  }
}
</script>

<style scoped>
.join-methods {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.join-label {
  font-size: 0.9rem;
  color: #6b7280;
}

.join-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.join-badge {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  background: #f1f1f1;
  color: #555;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
}

.join-badge i {
  font-size: 0.9rem;
}
</style>