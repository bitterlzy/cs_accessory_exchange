<template>
  <div id="app-root">
    <nav class="navbar" v-if="$route.path !== '/login' && $route.path !== '/register'">
      <div class="nav-inner">
        <router-link to="/dashboard" class="brand">CS饰品交换</router-link>
        <div class="nav-links">
          <router-link to="/inventory">库存</router-link>
          <router-link to="/listings">请求</router-link>
          <router-link to="/my-listings">我的</router-link>
          <router-link to="/offers">提议</router-link>
          <router-link to="/trades">历史</router-link>
          <router-link to="/notifications">通知</router-link>
          <router-link to="/kyc">认证</router-link>
          <router-link to="/steam">Steam</router-link>
          <a href="#" @click.prevent="logout">退出</a>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>
<script>
import { clearTokens } from './api'
export default {
  methods: {
    logout() { clearTokens(); this.$router.push('/login') }
  }
}
</script>
<style>
#app-root { min-height: 100vh; background: #f5f6fa; }
.navbar { background: #1a1a2e; color: #fff; padding: 0 20px; position: sticky; top: 0; z-index: 100; }
.nav-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; height: 56px; gap: 30px; }
.brand { color: #fff; text-decoration: none; font-size: 18px; font-weight: 700; white-space: nowrap; }
.nav-links { display: flex; gap: 16px; overflow-x: auto; }
.nav-links a { color: #ccc; text-decoration: none; font-size: 14px; white-space: nowrap; padding: 4px 0; }
.nav-links a:hover, .nav-links a.router-link-exact-active { color: #fff; border-bottom: 2px solid #e94560; }
.main-content { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
.card { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
button { cursor: pointer; border: none; border-radius: 6px; padding: 8px 18px; font-size: 14px; }
.btn-primary { background: #e94560; color: #fff; }
.btn-primary:hover { background: #d63851; }
.btn-secondary { background: #e8e8e8; color: #333; }
.btn-secondary:hover { background: #ddd; }
.btn-sm { padding: 4px 12px; font-size: 13px; }
input, select, textarea { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; width: 100%; box-sizing: border-box; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-size: 13px; color: #555; }
.page-title { font-size: 22px; font-weight: 600; margin-bottom: 20px; color: #1a1a2e; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
.table th { background: #f8f9fc; font-weight: 600; color: #555; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.badge-active { background: #d4edda; color: #155724; }
.badge-closed { background: #f8d7da; color: #721c24; }
.badge-pending { background: #fff3cd; color: #856404; }
.empty-state { text-align: center; padding: 40px; color: #999; }
</style>
