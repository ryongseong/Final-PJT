<template>
  <div class="pagination-container" v-if="totalPages > 1">
    <div class="pagination">
      <button class="pagination-button" @click="onPageChange(1)" :disabled="currentPage === 1">
        처음
      </button>
      <button
        class="pagination-button"
        @click="onPageChange(currentPage - 1)"
        :disabled="currentPage === 1"
      >
        이전
      </button>

      <div class="page-numbers">
        <button
          v-for="page in displayedPages"
          :key="page"
          @click="onPageChange(page)"
          class="page-number"
          :class="{ active: currentPage === page }"
        >
          {{ page }}
        </button>
      </div>

      <button
        class="pagination-button"
        @click="onPageChange(currentPage + 1)"
        :disabled="currentPage === totalPages"
      >
        다음
      </button>
      <button
        class="pagination-button"
        @click="onPageChange(totalPages)"
        :disabled="currentPage === totalPages"
      >
        마지막
      </button>
    </div>

    <div class="page-info">
      <span
        >{{ totalItems }}개 중 {{ (currentPage - 1) * itemsPerPage + 1 }}-{{
          Math.min(currentPage * itemsPerPage, totalItems)
        }}개 표시</span
      >
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'PaginationControl',
  props: {
    currentPage: {
      type: Number,
      required: true,
    },
    totalPages: {
      type: Number,
      required: true,
    },
    totalItems: {
      type: Number,
      required: true,
    },
    itemsPerPage: {
      type: Number,
      required: true,
    },
  },
  emits: ['page-change'],
  setup(props, { emit }) {
    const displayedPages = computed(() => {
      const pages = []
      const maxVisiblePages = 5

      // Always show current page in the middle when possible
      let startPage = Math.max(1, props.currentPage - Math.floor(maxVisiblePages / 2))
      let endPage = Math.min(props.totalPages, startPage + maxVisiblePages - 1)

      // Adjust start page if we're near the end
      if (endPage - startPage + 1 < maxVisiblePages && startPage > 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages
    })

    const onPageChange = (page) => {
      if (page >= 1 && page <= props.totalPages) {
        emit('page-change', page)
      }
    }

    return {
      displayedPages,
      onPageChange,
    }
  },
}
</script>

<style scoped>
.pagination-container {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding-bottom: 2rem;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  min-width: 2.5rem;
  height: 2.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.page-number:hover {
  background: #f3f4f6;
}

.page-number.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.pagination-button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background: white;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #f3f4f6;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #6b7280;
}

@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
