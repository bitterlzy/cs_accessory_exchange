<template>
  <div>
    <h1 class="page-title">实名认证</h1>
    <div class="card">
      <div v-if="status.verification_level === 'verified'">
        <p style="color:#28a745;font-size:16px">✔ 已通过实名认证</p>
        <p>真实姓名：{{ status.real_name }}</p>
        <p>支付宝：{{ status.alipay_account }}</p>
      </div>
      <div v-else-if="status.verification_level === 'pending'">
        <p style="color:#856404">⏳ 认证审核中</p>
        <button class="btn-primary btn-sm" @click="doVerify" :disabled="loading">{{ loading ? '处理中...' : '模拟通过认证' }}</button>
      </div>
      <div v-else>
        <p>实名认证后可进行交易。请提交以下信息：</p>
        <form @submit.prevent="submitKYC">
          <div class="form-group"><label>真实姓名</label><input v-model="form.real_name" required /></div>
          <div class="form-group"><label>身份证号</label><input v-model="form.id_number" required /></div>
          <div class="form-group"><label>支付宝账号</label><input v-model="form.alipay_account" required /></div>
          <button type="submit" class="btn-primary btn-sm" :disabled="loading">{{ loading ? '提交中...' : '提交认证' }}</button>
        </form>
        <p v-if="error" style="color:#e94560;font-size:13px">{{ error }}</p>
      </div>
    </div>
  </div>
</template>
<script>
import { kycApi } from '../api'
export default {
  data() { return { status: {}, form: { real_name: '', id_number: '', alipay_account: '' }, error: '', loading: false } },
  async mounted() { await this.loadStatus() },
  methods: {
    async loadStatus() { try { var r = await kycApi.status(); this.status = r.data } catch(e) {} },
    async submitKYC() {
      this.loading = true; this.error = ''
      try { await kycApi.submit(this.form); await this.loadStatus() }
      catch(e) { this.error = e.response?.data?.error || '提交失败' }
      finally { this.loading = false }
    },
    async doVerify() {
      this.loading = true
      try { await kycApi.verify(); await this.loadStatus() }
      catch(e) { alert('验证失败') }
      finally { this.loading = false }
    }
  }
}
</script>
