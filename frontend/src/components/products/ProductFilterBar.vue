<template>
  <div class="filter-bar">
    <div class="search-box">
      <input 
        v-model="searchInput" 
        type="text" 
        class="search-input-field"
        placeholder="상품명 또는 은행명으로 검색..."
        @input="onSearch"
        @keyup.enter="triggerSearchImmediately"
      />
      <i class="search-icon fas fa-search" @click="triggerSearchImmediately"></i>
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
    
    let searchTimeout = null;
    
    const onSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        emit('search', searchInput.value);
      }, 300);
    };

    const triggerSearchImmediately = () => {
      if (searchTimeout) clearTimeout(searchTimeout);
      emit('search', searchInput.value);
    };
    
    const onFilterChange = () => {
      console.log('[ProductFilterBar] onFilterChange triggered. Selected type:', selectedProductType.value);
      emit('filter', selectedProductType.value);
    };
    
    const onSortChange = () => {
      emit('sort', selectedSortOption.value);
    };
    
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
      onSortChange,
      triggerSearchImmediately
    };
  }
};
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md, 1rem);
  padding: var(--spacing-md, 1rem);
  background: var(--card-bg, #f8f9fa);
  border-radius: var(--border-radius-lg, 8px);
  margin-bottom: var(--spacing-lg, 1.5rem);
  box-shadow: var(--card-shadow, 0 1px 3px rgba(0, 0, 0, 0.05));
  border: 1px solid var(--card-border, transparent);
}

.search-box {
  display: flex;
  align-items: center;
  background-color: var(--background-primary);
  border-radius: var(--input-border-radius, 8px);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  flex-grow: 1;
  border: 1px solid var(--border-color);
}

.search-input-field {
  border: none;
  outline: none;
  background-color: transparent;
  flex-grow: 1;
  padding: var(--spacing-sm, 0.5rem);
  font-size: var(--font-size-sm, 0.95rem);
  color: var(--text-input, var(--text-primary));
  font-family: var(--font-body);
  line-height: 1.5;
}

.search-input-field::placeholder {
  color: var(--text-secondary);
}

.search-icon {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-left: var(--spacing-sm, 0.5rem);
  cursor: pointer;
  transition: color var(--transition-speed, 0.2s);
}

.search-icon:hover {
  color: var(--accent-color);
}

.filter-options {
  display: flex;
  gap: var(--spacing-md, 1rem);
  flex-wrap: wrap;
}

.filter-dropdown, .sort-dropdown {
  flex: 1;
  min-width: 180px;
}

select {
  width: 100%;
  padding: var(--input-padding-y, 0.6rem) var(--input-padding-x, 1rem);
  border: 1px solid var(--input-border, var(--border-color, #ced4da));
  border-radius: var(--border-radius-md, 8px);
  background-color: var(--input-bg);
  font-size: var(--font-size-sm, 0.95rem);
  color: var(--text-input);
  cursor: pointer;
  line-height: 1.5;
  box-sizing: border-box;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right var(--input-padding-x, 1rem) center;
  background-size: 16px 12px;
}

select option {
  background-color: var(--background-primary);
  color: var(--text-primary);
}

select:focus {
 outline: 2px solid var(--accent-color-opacity-50, rgba(0,123,255,0.5)); 
 outline-offset: -1px;
}

@media (min-width: 768px) {
  .filter-bar {
    flex-direction: row;
    align-items: center;
  }
  
  .search-box {
    /* max-width: 40%; */
    flex-grow: 3;
    flex-basis: 0;
  }
  
  .filter-options {
    flex-grow: 2;
    flex-basis: 0;
    justify-content: flex-end;
  }

  .filter-dropdown, .sort-dropdown {
    flex-grow: 1;
    flex-basis: 0;
    min-width: 150px;
  }
}
</style>