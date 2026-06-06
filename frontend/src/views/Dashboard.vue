<template>
  <div>
    <h1 class="page-title">仪表盘</h1>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px">
      <div class="card"><h3>我的库存</h3><p style="font-size:28px;font-weight:700;color:#e94560">{{ stats.inventory }}</p></div>
      <div class="card"><h3>活跃请求</h3><p style="font-size:28px;font-weight:700;color:#e94560">{{ stats.activeListings }}</p></div>
      <div class="card"><h3>待处理提议</h3><p style="font-size:28px;font-weight:700;color:#e94560">{{ stats.pendingOffers }}</p></div>
      <div class="card"><h3>已完成交换</h3><p style="font-size:28px;font-weight:700;color:#e94560">{{ stats.completedTrades }}</p></div>
    </div>
    <div class="card" style="margin-top:20px">
      <h3>最近通知</h3>
      <div v-if="notifications.length === 0" class="empty-state">暂无通知</div>
      <div v-for="n in notifications.slice(0,5)" :key="n.id" style="padding:8px 0;border-bottom:1px solid #eee;font-size:14px">
        <strong>{{ n.title }}</strong><span v-if="!n.is_read" class="badge badge-pending" style="margin-left:8px">未读</span>
        <p style="margin:2px 0 0;color:#666;font-size:13px">{{ n.body }}</p>
      </div>
    </div>
  </div>
</template>
<script>
import { inventoryApi, listingApi, offerApi, tradeApi, notifApi, userApi } from '../api'
export default {
  data() { return { stats: { inventory: 0, activeListings: 0, pendingOffers: 0, completedTrades: 0 }, notifications: [] } },
  async mounted() {
    try {
      var inv = await inventoryApi.list()
      this.stats.inventory = inv.data.length
    } catch(e) {}
    try {
      var list = await listingApi.list()
      this.stats.activeListings = list.data.total || 0
    } catch(e) {}
    try {
      var off = await offerApi.list()
      this.stats.pendingOffers = off.data.filter(function(o) { return o.status === 'pending' }).length
    } catch(e) {}
    try {
      var tr = await tradeApi.list()
      this.stats.completedTrades = tr.data.length
    } catch(e) {}
    try {
      var n = await notifApi.list()
      this.notifications = n.data.notifications || []
    } catch(e) {}
  }
}
</script>
