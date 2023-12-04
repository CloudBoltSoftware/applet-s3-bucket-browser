<!-- eslint-disable vue/no-v-model-argument -->
<template>
  <VDataTable
    v-model:expanded="expanded"
    :headers="isVersionMode ? versionHeaders : headers"
    :item-value="(row) => row"
    :loading="bucketLoading"
    show-select
    :show-expand="isVersionMode ? true : false"
    @update:model-value="(val) => emit('update:items', val)"
  >
    <template #[`item.name`]="row">
      <td class="d-inline-flex">
        <VIcon
          v-if="rawItemData(row).nested_version"
          icon="mdi-alpha-l"
          class="ml-4"
        />
        <VIcon
          v-else
          :icon="
            rawItemData(row).is_file
              ? rawItemData(row)?.is_delete_marker
                ? 'mdi-file-cancel'
                : 'mdi-file'
              : 'mdi-folder'
          "
          color="blue-darken-3"
          class="align-self-center"
        />
        <FolderButton
          v-if="!rawItemData(row).is_file"
          :url="rawItemData(row).url"
          :name="rawItemData(row).name"
          :is-deleted="rawItemData(row).is_delete_marker"
        />
        <div v-else class="ml-4">{{ rawItemData(row).name }}</div>
      </td>
    </template>
    <template #[`item.last_modified`]="row">
      {{ rawItemData(row).is_file ? parseDate(rawItemData(row)) : '' }}
    </template>
    <template #[`item.actual_size`]="row">
      <span
        :class="rawItemData(row).is_delete_marker ? 'font-weight-thin' : ''"
        >{{
          rawItemData(row).is_delete_marker ? 'Deleted' : rawItemData(row).size
        }}</span
      >
    </template>
    <template #[`item.storage_class`]="row">
      {{ rawItemData(row).storage_class }}
    </template>
    <template #[`item.actions`]="row">
      <td v-if="rawItemData(row).is_file" class="d-inline-flex">
        <VBtnGroup variant="text">
          <VBtn
            v-if="isVersionMode"
            icon="mdi-file-download"
            title="Download"
            :disabled="rawItemData(row).is_delete_marker"
            @click="downloadFile(rawItemData(row).download_url)"
          />
          <RestoreButton
            v-if="isVersionMode"
            :item-key="rawItemData(row).key"
            :path="rawItemData(row).path"
            :version-id="
              findLastActiveVersion(rawItemData(row).versions)?.version_id
            "
            :is-delete-marker="
              findLastActiveVersion(rawItemData(row).versions)?.is_delete_marker
            "
            :is-active-version="
              Boolean(findLastActiveVersion(rawItemData(row).versions))
            "
          />
          <RenameModal
            :name="rawItemData(row).name"
            :is-deleted="rawItemData(row).is_delete_marker"
          />
          <OverviewModal :source-item="rawItemData(row)" />
        </VBtnGroup>
      </td>
    </template>
    <template #[`item.data-table-expand`]="row">
      <VIcon
        v-if="rawItemData(row).is_file"
        :icon="row.isExpanded ? 'mdi-menu-down' : 'mdi-menu-up'"
        @click="row.toggleExpand(row.item)"
      />
    </template>
    <template #expanded-row="row">
      <tr
        v-for="(entry, idx) in rawItemData(row)?.versions"
        :key="idx"
        class="expanded"
      >
        <td></td>
        <td>
          <VIcon icon="mdi-alpha-l" class="ml-1 mt-n1" />
          <span class="mx-2">{{ entry.version_id }}</span
          ><span class="ml-2 text-disabled">Version Id</span>
        </td>
        <td>{{ rawItemData(row).item_type }}</td>
        <td>{{ parseDate(entry) }}</td>
        <td :class="entry.is_delete_marker ? 'font-weight-thin' : ''">
          {{ entry.size }}
        </td>
        <td>{{ entry.storage_class }}</td>
        <td>
          <VBtnGroup variant="text">
            <VBtn
              icon="mdi-file-download"
              title="Download"
              :disabled="entry.is_delete_marker"
              @click="downloadFile(entry.download_url)"
            />
            <RestoreButton
              :item-key="entry.key"
              :path="entry.path"
              :version-id="entry.version_id"
              :is-delete-marker="entry.is_delete_marker"
              :is-active-version="entry.is_latest"
            />
          </VBtnGroup>
        </td>
        <td></td>
      </tr>
    </template>
  </VDataTable>
</template>

<script>
import {
  downloadFile,
  findLastActiveVersion,
  parseDate,
  rawItemData
} from '../../helpers/commonHelpers'

export default {
  rawItemData,
  downloadFile,
  parseDate,
  findLastActiveVersion
}
</script>
<script setup>
import { ref } from 'vue'
import { useBuckets } from '../../helpers/useBuckets'
import OverviewModal from '../Modals/OverviewModal.vue'
import RenameModal from '../Modals/RenameModal.vue'
import FolderButton from './FolderButton.vue'
import RestoreButton from './RestoreButton.vue'

/**
 * @typedef {Object} Props
 * @property {Boolean} Props.isVersionMode - Boolean if Bucket Version mode is on
 * @property {Array} Props.selectedItems - The array of the selected dataTable items
 * @property {Function} Props.updatedSelectedItems - Function to update the array of the selected table items
 */
/** @type {Props} */
defineProps({
  isVersionMode: {
    type: Boolean,
    default: false
  },
  selectedItems: {
    type: Array,
    default: () => []
  },
  updatedSelectedItems: {
    type: Function,
    default: () => {}
  }
})

const { bucketLoading } = useBuckets()
const expanded = ref([])
const emit = defineEmits(['update:items'])

const headers = [
  { title: 'Name', align: 'start', key: 'name' },
  { title: 'Type', align: 'end', key: 'item_type' },
  { title: 'Last Modified', align: 'start', key: 'last_modified' },
  { title: 'Size', align: 'end', key: 'actual_size' },
  { title: 'Storage Class', align: 'end', key: 'storage_class' },
  { title: 'Actions', align: 'center', key: 'actions', sortable: false }
]
const versionHeaders = [
  { title: 'Name', align: 'start', key: 'name' },
  { title: 'Type', align: 'start', key: 'item_type' },
  { title: 'Last Modified', align: 'start', key: 'last_modified' },
  { title: 'Size', align: 'start', key: 'actual_size' },
  { title: 'Storage Class', align: 'start', key: 'storage_class' },
  { title: 'Actions', align: 'start', key: 'actions', sortable: false },
  { title: '', align: 'center', key: 'data-table-expand', sortable: false }
]
</script>
<style scoped>
/* blue-grey-lighten-5 #ECEFF1 */
.expanded td {
  background-color: #eceff1 !important;
}
</style>
