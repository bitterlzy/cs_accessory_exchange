<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h1 class="page-title">通知</h1>
      <button class="btn-secondary btn-sm" @click="markAllRead">全部已读</button>
    </div>
    <div class="card">
      <div v-if="notifications.length === 0" class="empty-state">暂无通知</div>
      <div v-for="n in notifications" :key="n.id" style="padding:12px 0;border-bottom:1px solid #eee" :style="{background: n.is_read ? 'transparent' : '#f8f9ff'}">
        <div style="display:flex;justify-content:space-between">
          <strong>{{ n.title }}</strong>
          <span v-if="!n.is_read"><button class="btn-sm" style="background:none;color:#e94560" @click="markRead(n.id)">标为已读</button></span>
        </div>
        <p style="margin:4px 0 0;color:#666;font-size:13px">{{ n.body }}</p>
        <small style="color:#999;font-size:12px">{{ new Date(n.created_at).toLocaleString() }}</small>
      </div>
    </div>
  </div>
</template>
<script>
import { notifApi } from '../api'
export default {
  data() { return { notifications: [] } },
  async mounted() { await this.load() },
  methods: {
    async load() { try { var r = await notifApi.list(); this.notifications = r.data.notifications || [] } catch(e) {} },
    async markRead(id) { try { await notifApi.markRead(id); await this.load() } catch(e) {} },
    async markAllRead() { try { await notifApi.markAllRead(); await this.load() } catch(e) {} }
  }
}
</script>
