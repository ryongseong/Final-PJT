<!-- src/views/NotFoundView.vue -->
<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>페이지를 찾을 수 없습니다</h2>
      <p>요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.</p>
      <router-link to="/" class="home-button">홈으로 이동</router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
}

h1 {
  font-size: 8rem;
  color: #4f46e5;
  margin: 0;
  line-height: 1;
}

h2 {
  font-size: 2rem;
  color: #333;
  margin: 0 0 20px;
}

p {
  color: #666;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.home-button {
  display: inline-block;
  padding: 12px 30px;
  background-color: #4f46e5;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.home-button:hover {
  background-color: #4338ca;
}
</style>
