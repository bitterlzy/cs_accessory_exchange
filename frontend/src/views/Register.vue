<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>注册</h2>
      <form @submit.prevent="register">
        <div class="form-group"><label>邮箱</label><input v-model="form.email" type="email" required /></div>
        <div class="form-group"><label>用户名</label><input v-model="form.username" required /></div>
        <div class="form-group"><label>手机号</label><input v-model="form.phone" type="tel" required /></div>
        <div class="form-group"><label>密码</label><input v-model="form.password" type="password" required /></div>
        <p v-if="error" style="color:#e94560;font-size:13px">{{ error }}</p>
        <button type="submit" class="btn-primary" style="width:100%" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
        <p style="margin-top:12px;font-size:13px;text-align:center">已有账号？<router-link to="/login">登录</router-link></p>
      </form>
    </div>
  </div>
</template>
<script>
import { authApi, setTokens } from '../api'
export default {
  data() { return { form: { email: '', username: '', phone: '', password: '' }, error: '', loading: false } },
  methods: {
    async register() {
      this.loading = true; this.error = ''
      try {
        var r = await authApi.register(this.form)
        setTokens(r.data.token, r.data.refresh_token)
        this.$router.push('/dashboard')
      } catch(e) { this.error = e.response?.data?.error || '注册失败' }
      finally { this.loading = false }
    }
  }
}
</script>
<style scoped>
.auth-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #1a1a2e; }
.auth-card { background: #fff; padding: 40px; border-radius: 12px; width: 360px; }
.auth-card h2 { margin-top: 0; text-align: center; }
</style>
