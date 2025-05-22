<template>
  <div class="filter-bar">
    <div class="search-container">
      <input 
        v-model="searchInput" 
        type="text" 
        class="search-input" 
        placeholder="상품명 또는 은행명으로 검색..."
        @input="onSearch"
      />
      <button class="search-button" @click="onSearch">
        <i class="fas fa-search"></i>
      </button>
    </div>
    
    <div class="filter-options">
      <div class="filter-dropdown">
        <select v-model="selectedProductType" @change="onFilterChange">
          <option value="all">모든 상품</option>
          <option value="deposit">예금 상품</option>
          <option value="saving">적금 상품</option>
          <option value="loan">대출 상품</option>
        </select>
      </div>
      
      <div class="sort-dropdown">
        <select v-model="selectedSortOption" @change="onSortChange">
          <option value="name">이름순</option>
          <option value="rate-desc">금리 높은순</option>
          <option value="rate-asc">금리 낮은순</option>
          <option value="bank">은행명순</option>
          <option value="date">출시일순</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';

export default {
  name: 'ProductFilterBar',
  props: {
    initialProductType: {
      type: String,
      default: 'all'
    },
    initialSortOption: {
      type: String,
      default: 'name'
    },
    initialSearchQuery: {
      type: String,
      default: ''
    }
  },
  setup(props, { emit }) {
    const searchInput = ref(props.initialSearchQuery);
    const selectedProductType = ref(props.initialProductType);
    const selectedSortOption = ref(props.initialSortOption);
    
    // Debounce search to avoid excessive API calls
    let searchTimeout = null;
    
    const onSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        emit('search', searchInput.value);
      }, 300);
    };
    
    const onFilterChange = () => {
      emit('filter', selectedProductType.value);
    };
    
    const onSortChange = () => {
      emit('sort', selectedSortOption.value);
    };
    
    // Update component if props change
    watch(() => props.initialProductType, (newValue) => {
      selectedProductType.value = newValue;
    });
    
    watch(() => props.initialSortOption, (newValue) => {
      selectedSortOption.value = newValue;
    });
    
    watch(() => props.initialSearchQuery, (newValue) => {
      searchInput.value = newValue;
    });
    
    return {
      searchInput,
      selectedProductType,
      selectedSortOption,
      onSearch,
      onFilterChange,
      onSortChange
    };
  }
};
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-container {
  position: relative;
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.search-button {
  position: absolute;
  top: 50%;
  right: 0.75rem;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #777;
  cursor: pointer;
}

.filter-options {
  display: flex;
  gap: 1rem;
}

.filter-dropdown, .sort-dropdown {
  flex: 1;
}

select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 1rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24'%3E%3Cpath fill='%23888' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
}

@media (min-width: 768px) {
  .filter-bar {
    flex-direction: row;
    align-items: center;
  }
  
  .search-container {
    max-width: 50%;
  }
  
  .filter-options {
    flex: 1;
  }
}
</style>