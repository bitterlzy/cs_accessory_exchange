<template>
  <div>
    <h1 class="page-title">交换请求</h1>
    <div class="card">
      <input v-model="search" placeholder="搜索..." style="margin-bottom:12px" />
      <table class="table" v-if="listings.length">
        <thead><tr><th>卖家</th><th>物品</th><th>期望</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="l in filtered" :key="l.id">
            <td>{{ l.seller?.username }}</td>
            <td v-if="l.offered_item?.definition">{{ l.offered_item.definition.name }}</td>
            <td>{{ l.want_description || l.want_category || '任意' }}</td>
            <td><span class="badge badge-active">{{ l.status }}</span></td>
            <td><button class="btn-primary btn-sm" @click="propose(l)">发起交换</button></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">暂无活跃请求</div>
    </div>

    <div class="card" v-if="showPropose">
      <h3>发起交换提议</h3>
      <p>对请求 #{{ proposeTarget?.id }} 发起交换</p>
      <div class="form-group">
        <label>选择要交换的物品 (你的库存)</label>
        <select v-model="proposeItemId"><option v-for="i in myItems" :key="i.id" :value="i.id">{{ i.definition?.name }} ({{ i.quality }})</option></select>
      </div>
      <div class="form-group"><label>备注</label><textarea v-model="proposeNote"></textarea></div>
      <button class="btn-primary btn-sm" @click="submitPropose">确认发起</button>
      <button class="btn-secondary btn-sm" style="margin-left:8px" @click="showPropose = false">取消</button>
      <p v-if="proposeError" style="color:#e94560;font-size:13px">{{ proposeError }}</p>
    </div>
  </div>
</template>
<script>
import { listingApi, offerApi, inventoryApi } from '../api'
export default {
  data() { return { listings: [], search: '', myItems: [], showPropose: false, proposeTarget: null, proposeItemId: null, proposeNote: '', proposeError: '' } },
  computed: { filtered() { return this.listings.filter(function(l) { return !this.search || (l.offered_item?.definition?.name || '').toLowerCase().includes(this.search.toLowerCase()) }, this) } },
  async mounted() { try { var r = await listingApi.list(); this.listings = r.data.listings || [] } catch(e) {} },
  methods: {
    async propose(l) {
      this.proposeTarget = l; this.showPropose = true; this.proposeError = ''
      try { var r = await inventoryApi.list(); this.myItems = r.data } catch(e) {}
    },
    async submitPropose() {
      this.proposeError = ''
      try { await offerApi.create({ listing_id: this.proposeTarget.id, proposer_item_ids: [this.proposeItemId], note: this.proposeNote }); this.showPropose = false; alert('提议已发送！') }
      catch(e) { this.proposeError = e.response?.data?.error || '发起失败' }
    }
  }
}
</script>
