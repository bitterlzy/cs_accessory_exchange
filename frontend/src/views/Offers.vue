<template>
  <div>
    <h1 class="page-title">交换提议</h1>
    <div class="card">
      <table class="table" v-if="offers.length">
        <thead><tr><th>方向</th><th>对方</th><th>物品</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="o in offers" :key="o.id">
            <td>{{ o.proposer?.id === userId ? '发出' : '收到' }}</td>
            <td>{{ o.proposer?.id === userId ? o.receiver?.username : o.proposer?.username }}</td>
            <td><span v-for="oi in o.offer_items" :key="oi.id"><span v-if="oi.inventory_item?.definition">{{ oi.inventory_item.definition.name }} </span></span></td>
            <td><span class="badge" :class="'badge-' + o.status">{{ o.status }}</span></td>
            <td>
              <button v-if="o.status==='pending' && o.receiver?.id === userId" class="btn-primary btn-sm" @click="acceptOffer(o.id)">接受</button>
              <button v-if="o.status==='pending' && o.receiver?.id === userId" class="btn-secondary btn-sm" style="margin-left:4px" @click="rejectOffer(o.id)">拒绝</button>
              <button v-if="o.status==='accepted'" class="btn-primary btn-sm" @click="confirmTrade(o.id)">确认交换</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">暂无交换提议</div>
    </div>
  </div>
</template>
<script>
import { offerApi, userApi } from '../api'
export default {
  data() { return { offers: [], userId: null } },
  async mounted() {
    try { var r = await offerApi.list(); this.offers = r.data } catch(e) {}
    try { var u = await userApi.me(); this.userId = u.data.id } catch(e) {}
  },
  methods: {
    async acceptOffer(id) { try { await offerApi.accept(id); this.$router.go(0) } catch(e) { alert(e.response?.data?.error || '操作失败') } },
    async rejectOffer(id) { try { await offerApi.reject(id); this.$router.go(0) } catch(e) { alert(e.response?.data?.error || '操作失败') } },
    async confirmTrade(id) { try { await offerApi.confirm(id); this.$router.go(0) } catch(e) { alert(e.response?.data?.error || '操作失败') } }
  }
}
</script>
