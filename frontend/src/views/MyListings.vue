<template>
  <div>
    <h1 class="page-title">我的请求</h1>
    <div class="card">
      <h3>发布新请求</h3>
      <form @submit.prevent="createListing">
        <div class="form-group"><label>选择物品</label><select v-model.number="form.offered_item_id"><option v-for="i in myItems" :key="i.id" :value="i.id" v-if="i.status==='available'">{{ i.definition?.name }} ({{ i.quality }})</option></select></div>
        <div class="form-group"><label>期望品类</label><input v-model="form.want_category" placeholder="如 weapon" /></div>
        <div class="form-group"><label>品质</label><select v-model="form.want_quality"><option>any</option><option>FN</option><option>MW</option><option>FT</option><option>WW</option><option>BS</option></select></div>
        <div class="form-group"><label>描述</label><textarea v-model="form.want_description" placeholder="想换什么？"></textarea></div>
        <button type="submit" class="btn-primary btn-sm">发布</button>
      </form>
      <p v-if="createError" style="color:#e94560;font-size:13px">{{ createError }}</p>
    </div>
    <div class="card">
      <table class="table" v-if="myListings.length">
        <thead><tr><th>物品</th><th>期望</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="l in myListings" :key="l.id">
            <td v-if="l.offered_item?.definition">{{ l.offered_item.definition.name }}</td>
            <td>{{ l.want_description || l.want_category || '任意' }}</td>
            <td><span class="badge" :class="'badge-' + l.status">{{ l.status }}</span></td>
            <td><button v-if="l.status==='active'" class="btn-secondary btn-sm" @click="closeListing(l.id)">关闭</button></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">还没有发布过请求</div>
    </div>
  </div>
</template>
<script>
import { listingApi, inventoryApi } from '../api'
export default {
  data() { return { myListings: [], myItems: [], form: { offered_item_id: null, want_category: '', want_quality: 'any', want_description: '' }, createError: '' } },
  async mounted() { await this.load() },
  methods: {
    async load() {
      try { var r = await listingApi.my(); this.myListings = r.data } catch(e) {}
      try { var r = await inventoryApi.list(); this.myItems = r.data } catch(e) {}
    },
    async createListing() {
      this.createError = ''
      try { await listingApi.create(this.form); this.form = { offered_item_id: null, want_category: '', want_quality: 'any', want_description: '' }; await this.load() }
      catch(e) { this.createError = e.response?.data?.error || '发布失败' }
    },
    async closeListing(id) { try { await listingApi.close(id); await this.load() } catch(e) {} }
  }
}
</script>
