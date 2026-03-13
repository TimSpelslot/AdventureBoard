<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5">User Approval</div>
      <q-btn flat icon="refresh" label="Refresh" @click="fetchUsers" :loading="loading" />
    </div>

    <q-banner v-if="accessDenied" class="bg-negative text-white q-mb-md" rounded>
      Admin access required.
    </q-banner>

    <q-table
      v-else
      title="Manage User Privileges"
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
    >
      <template #body-cell-privilege_level="props">
        <q-td :props="props">
          <q-select
            dense
            outlined
            emit-value
            map-options
            :options="privilegeOptions"
            :model-value="pendingLevels[props.row.id]"
            @update:model-value="(v) => (pendingLevels[props.row.id] = Number(v))"
            style="min-width: 180px"
          />
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="primary"
            label="Save"
            size="sm"
            :disable="pendingLevels[props.row.id] === props.row.privilege_level"
            :loading="savingUserId === props.row.id"
            @click="savePrivilege(props.row)"
          />
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, inject } from 'vue';

export default defineComponent({
  name: 'AdminUsersPage',
  setup() {
    return {
      me: inject('me') as any,
      privilegeOptions: [
        { label: 'Noob (0)', value: 0 },
        { label: 'Approved (1)', value: 1 },
        { label: 'Admin (2)', value: 2 },
      ],
      columns: [
        { name: 'display_name', label: 'Display Name', field: 'display_name', align: 'left' as const },
        { name: 'email', label: 'Email', field: 'email', align: 'left' as const },
        { name: 'privilege_level', label: 'Privilege', field: 'privilege_level', align: 'left' as const },
        { name: 'actions', label: 'Actions', field: 'actions', align: 'left' as const },
      ],
    };
  },
  data() {
    return {
      loading: false,
      rows: [] as any[],
      pendingLevels: {} as Record<number, number>,
      savingUserId: null as null | number,
      accessDenied: false,
    };
  },
  async mounted() {
    if (!this.me || this.me.privilege_level < 2) {
      this.accessDenied = true;
      return;
    }
    await this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      this.loading = true;
      try {
        const resp = await this.$api.get('/api/users');
        this.rows = (resp.data || []).slice().sort((a: any, b: any) => {
          if (b.privilege_level !== a.privilege_level) {
            return b.privilege_level - a.privilege_level;
          }
          return String(a.display_name || '').localeCompare(String(b.display_name || ''));
        });

        this.pendingLevels = {};
        for (const user of this.rows) {
          this.pendingLevels[user.id] = Number(user.privilege_level);
        }
      } catch (e) {
        this.$q.notify({ type: 'negative', message: this.$extractErrors(e).join(', ') || 'Failed to fetch users' });
      } finally {
        this.loading = false;
      }
    },
    async savePrivilege(row: any) {
      const nextLevel = this.pendingLevels[row.id];
      if (nextLevel === row.privilege_level) {
        return;
      }

      this.savingUserId = row.id;
      try {
        const resp = await this.$api.patch(`/api/users/${row.id}`, {
          privilege_level: nextLevel,
        });

        row.privilege_level = resp.data.privilege_level;
        this.pendingLevels[row.id] = row.privilege_level;
        this.$q.notify({ type: 'positive', message: `${row.display_name} updated to level ${row.privilege_level}` });
      } catch (e) {
        this.$q.notify({ type: 'negative', message: this.$extractErrors(e).join(', ') || 'Failed to update user' });
      } finally {
        this.savingUserId = null;
      }
    },
  },
});
</script>
