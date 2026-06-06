<template>
  <div>
    <h1 class="page-title">Steam 绑定</h1>
    <div class="card" v-if="accounts.length === 0">
      <p>绑定 Steam 账号以进行交易</p>
      <form @submit.prevent="linkSteam">
        <div class="form-group"><label>Steam 交易链接</label><input v-model="form.trade_url" placeholder="https://steamcommunity.com/tradeoffer/new/?partner=..." required /></div>
        <div class="form-group"><label>Steam 昵称</label><input v-model="form.steam_name" /></div>
        <button type="submit" class="btn-primary btn-sm" :disabled="loading">{{ loading ? '绑定中...' : '绑定 Steam 账号' }}</button>
      </form>
      <p v-if="error" style="color:#e94560;font-size:13px">{{ error }}</p>
      <p style="font-size:12px;color:#999;margin-top:8px">⚠ 绑定后不可更改</p>
    </div>
    <div class="card" v-else>
      <p>✔ 已绑定 Steam 账号</p>
      <div v-for="a in accounts" :key="a.id" style="padding:8px 0">
        <p>Steam ID: {{ a.steam_id }}</p>
        <p>交易链接: <a :href="a.trade_url" target="_blank">{{ a.trade_url }}</a></p>
        <p>状态: {{ a.is_verified ? '已验证' : '未验证' }}</p>
      </div>
    </div>
  </div>
</template>
<script>
import { steamApi } from '../api'
export default {
  data() { return { accounts: [], form: { trade_url: '', steam_name: '' }, error: '', loading: false } },
  async mounted() { await this.loadAccounts() },
  methods: {
    async loadAccounts() { try { var r = await steamApi.accounts(); this.accounts = r.data } catch(e) {} },
    async linkSteam() {
      this.loading = true; this.error = ''
      try { await steamApi.link(this.form); await this.loadAccounts() }
      catch(e) { this.error = e.response?.data?.error || '绑定失败' }
      finally { this.loading = false }
    }
  }
}
</script>
