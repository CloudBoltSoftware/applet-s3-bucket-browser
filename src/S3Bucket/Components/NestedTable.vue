<!-- eslint-disable vue/no-v-model-argument -->
<template>
  <VDataTable
    v-model:expanded="expanded"
    :headers="isVersionMode ? versionHeaders : headers"
    :item-value="(item) => item"
    :loading="bucketLoading"
    show-select
    :show-expand="isVersionMode ? true : false"
    @update:model-value="(val) => emit('update:items', val)"
  >
    <template #[`item.name`]="{ item }">
      <td class="d-inline-flex">
        <VIcon v-if="item.raw.nested_version" icon="mdi-alpha-l" class="ml-1" />
        <VIcon
          v-else
          :icon="item.raw.is_file ? 'mdi-file' : 'mdi-folder'"
          color="blue-darken-3"
          class="align-self-center"
        />
        <FolderButton v-if="!item.raw.is_file" v-bind="item.raw" />
        <div v-else class="ml-4">{{ item.raw.name }}</div>
      </td>
    </template>
    <template #[`item.last_modified`]="{ item }">
      {{ item.raw.is_file ? parseDate(item.raw) : '' }}
    </template>
    <template #[`item.size`]="{ item }">
      <span :class="item.raw.is_delete_marker ? 'font-weight-thin' : ''">{{
        item.raw.is_delete_marker ? 'Deleted' : item.raw.size
      }}</span>
    </template>
    <template #[`item.actions`]="{ item }">
      <td v-if="item.raw.is_file" class="d-inline-flex">
        <VBtnGroup variant="text">
          <VBtn
            v-if="isVersionMode"
            icon="mdi-file-download"
            title="Download"
            :disabled="item.raw.is_delete_marker"
            @click="downloadFile(item.raw.download_url)"
          />
          <RestoreButton
            v-if="isVersionMode"
            :item-key="item.raw.key"
            :path="item.raw.path"
            :version-id="item.raw.version_id"
          />
          <RenameModal
            :name="item.raw.name"
            :is-deleted="item.raw.is_delete_marker"
          />
          <OverviewModal :source-item="item.raw" />
        </VBtnGroup>
      </td>
    </template>
    <template #[`item.data-table-expand`]="{ item, isExpanded, toggleExpand }">
      <VIcon
        v-if="item.raw.is_file"
        :icon="isExpanded ? 'mdi-menu-down' : 'mdi-menu-up'"
        @click="toggleExpand(item)"
      />
    </template>
    <template #expanded-row="{ item }">
      <tr v-for="(entry, idx) in item.raw?.versions" :key="idx">
        <td></td>
        <td>
          <VIcon icon="mdi-alpha-l" class="ml-1 mt-n1" />
          <span class="mx-2">{{ entry.version_id }}</span
          ><span class="ml-2 text-disabled">Version Id</span>
        </td>
        <td>{{ item.raw.item_type }}</td>
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
            />
          </VBtnGroup>
        </td>
        <td></td>
      </tr>
    </template>
  </VDataTable>
</template>

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
  { title: 'Size', align: 'end', key: 'size' },
  { title: 'Storage Class', align: 'end', key: 'storage_class' },
  { title: 'Actions', align: 'center', key: 'actions', sortable: false }
]
const versionHeaders = [
  { title: 'Name', align: 'start', key: 'name' },
  { title: 'Type', align: 'start', key: 'item_type' },
  { title: 'Last Modified', align: 'start', key: 'last_modified' },
  { title: 'Size', align: 'start', key: 'size' },
  { title: 'Storage Class', align: 'start', key: 'storage_class' },
  { title: 'Actions', align: 'start', key: 'actions', sortable: false },
  { title: '', align: 'center', key: 'data-table-expand', sortable: false }
]

const parseDate = (entry) => {
  // Converting from database UTC values to local string
  const modifiedDate = new Date(entry.last_modified).toDateString()
  const modifiedTime = new Date(entry.last_modified).toLocaleTimeString('en-US')

  return `${modifiedDate}  ${modifiedTime}`
}

const downloadFile = (url) => {
  // TODO Better Decoding needed
  const adjustedUrl = url.replace(/&amp;/g, '&')
  window.open(adjustedUrl, '_blank')
}
</script>
<style scoped></style>
