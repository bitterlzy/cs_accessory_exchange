<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h1 class="page-title">库存管理</h1>
      <button class="btn-primary" @click="showAdd = true">+ 添加饰品</button>
    </div>
    
    <div class="card" v-if="showAdd">
      <h3>添加饰品</h3>
      <form @submit.prevent="addItem">
        <div class="form-group"><label>Definition ID (种子数据 ID)</label><input v-model.number="form.definition_id" type="number" required /></div>
        <div class="form-group"><label>品质</label>
          <select v-model="form.quality"><option>FN</option><option>MW</option><option>FT</option><option>WW</option><option>BS</option></select>
        </div>
        <div class="form-group"><label>磨损值 (可选)</label><input v-model.number="form.float_value" step="0.01" /></div>
        <div class="form-group"><label><input v-model="form.stat_trak" type="checkbox" /> StatTrak</label></div>
        <button type="submit" class="btn-primary btn-sm">确认添加</button>
        <button type="button" class="btn-secondary btn-sm" style="margin-left:8px" @click="showAdd = false">取消</button>
      </form>
      <p v-if="addError" style="color:#e94560;font-size:13px">{{ addError }}</p>
    </div>

    <div class="card">
      <input v-model="search" placeholder="搜索饰品名称..." style="margin-bottom:12px" />
      <table class="table" v-if="items.length">
        <thead><tr><th>名称</th><th>品质</th><th>磨损</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="item in filtered" :key="item.id">
            <td v-if="item.definition">{{ item.definition.name }}</td>
            <td>{{ item.quality }}</td>
            <td>{{ item.float_value || '-' }}</td>
            <td><span class="badge" :class="'badge-' + item.status">{{ item.status }}</span></td>
            <td><button v-if="item.status === 'available'" class="btn-secondary btn-sm" @click="deleteItem(item.id)">删除</button></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">库存为空，添加一些饰品吧</div>
    </div>
  </div>
</template>
<script>
import { inventoryApi } from '../api'
export default {
  data() { return { items: [], showAdd: false, search: '', form: { definition_id: 15, quality: 'FT', float_value: null, stat_trak: false }, addError: '' } },
  computed: { filtered() { return this.items.filter(function(i) { return !this.search || (i.definition && i.definition.name.toLowerCase().includes(this.search.toLowerCase())) }, this) } },
  async mounted() { await this.load() },
  methods: {
    async load() { try { var r = await inventoryApi.list(); this.items = r.data } catch(e) {} },
    async addItem() {
      this.addError = ''
      try { await inventoryApi.create(this.form); this.showAdd = false; await this.load() }
      catch(e) { this.addError = e.response?.data?.error || '添加失败' }
    },
    async deleteItem(id) { if (!confirm('确认删除？')) return; try { await inventoryApi.remove(id); await this.load() } catch(e) {} }
  }
}
</script>
