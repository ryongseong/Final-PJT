<template>
  <div class="admin-navbar">
    <div class="admin-navbar-container">
      <h2 class="admin-title">금융상품 관리 센터</h2>

      <nav class="admin-nav">
        <router-link to="/admin" class="admin-nav-link" exact-active-class="active">
          대시보드
        </router-link>
        <router-link to="/admin/financial-products" class="admin-nav-link" active-class="active">
          금융상품 목록
        </router-link>
        <router-link to="/admin/deposits" class="admin-nav-link" active-class="active">
          예금상품 관리
        </router-link>
        <router-link to="/admin/savings" class="admin-nav-link" active-class="active">
          적금상품 관리
        </router-link>
        <router-link to="/admin/loans" class="admin-nav-link" active-class="active">
          대출상품 관리
        </router-link>
      </nav>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminNavbar',
}
</script>

<style scoped>
.admin-navbar {
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--card-border);
  padding: 1rem 0;
  margin-bottom: 2rem;
  box-shadow: var(--card-shadow);
}

.admin-navbar-container {
  max-width: var(--max-width-content, 1200px);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0 2rem;
}

.admin-title {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-family: 'Pretendard Variable', serif;
  font-size: 1.8rem;
  font-weight: 700;
}

.admin-nav {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.admin-nav-link {
  text-decoration: none;
  color: var(--text-secondary);
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius-md);
  transition: all var(--transition-speed);
  font-weight: 500;
  font-size: 0.95rem;
  border: 1px solid transparent;
}

.admin-nav-link:hover {
  background-color: var(--background-primary);
  color: var(--accent-color);
  border-color: var(--border-color);
}

.admin-nav-link.active {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}

@media (max-width: 992px) {
  .admin-navbar-container {
    padding: 0 1.5rem;
  }
  .admin-title {
    font-size: 1.6rem;
  }
}

@media (max-width: 768px) {
  .admin-navbar-container {
    align-items: center;
  }
  .admin-title {
    text-align: center;
  }
  .admin-nav {
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  .admin-nav-link {
    padding: 0.75rem 1rem;
    text-align: center;
    width: 100%;
  }
}
</style>
