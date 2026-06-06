<template>
  <div>
    <h1 class="page-title">交换历史</h1>
    <div class="card">
      <table class="table" v-if="trades.length">
        <thead><tr><th>日期</th><th>对方</th><th>物品</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="t in trades" :key="t.id">
            <td>{{ new Date(t.created_at).toLocaleString() }}</td>
            <td>{{ t.proposer?.id === userId ? t.receiver?.username : t.proposer?.username }}</td>
            <td><span v-for="oi in t.offer_items" :key="oi.id"><span v-if="oi.inventory_item?.definition">{{ oi.inventory_item.definition.name }} </span></span></td>
            <td><span class="badge badge-active">{{ t.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">暂无交换记录</div>
    </div>
  </div>
</template>
<script>
import { tradeApi, userApi } from '../api'
export default {
  data() { return { trades: [], userId: null } },
  async mounted() {
    try { var r = await tradeApi.list(); this.trades = r.data } catch(e) {}
    try { var u = await userApi.me(); this.userId = u.data.id } catch(e) {}
  }
}
</script>
