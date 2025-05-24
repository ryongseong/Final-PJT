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
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  padding: 1rem 0;
  margin-bottom: 2rem;
}

.admin-navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  padding: 0 1rem;
}

.admin-title {
  margin: 0 0 1rem 0;
  color: #343a40;
  font-size: 1.5rem;
}

.admin-nav {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.admin-nav-link {
  text-decoration: none;
  color: #495057;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.admin-nav-link:hover {
  background-color: #e9ecef;
}

.admin-nav-link.active {
  background-color: #007bff;
  color: white;
}

@media (max-width: 768px) {
  .admin-nav {
    flex-direction: column;
    gap: 0.5rem;
  }

  .admin-nav-link {
    padding: 0.75rem 1rem;
  }
}
</style>
