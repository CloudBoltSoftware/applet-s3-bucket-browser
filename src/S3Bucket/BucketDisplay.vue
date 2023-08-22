<template>
  <div class="d-flex flex-column">
    <BucketBreadcrumbs v-if="bucketResource" class="justify-start" />
    <div class="d-flex justify-space-between">
      <VBtnGroup>
        <DownloadButton :selected-items="selectedItems" />
        <DeleteModal :selected-items="selectedItems" />
        <MultiFileModal v-if="dropModal" @update:clear="clearModal" />
        <UploadModal />
        <CreateModal />
        <VBtn
          v-if="isFlat"
          icon="mdi-folder-eye"
          title="Toggle Folder View"
          size="x-large"
          @click="getFlattenedView"
        />
        <VBtn
          v-else
          icon="mdi-view-headline"
          title="Toggle Flat List View"
          size="x-large"
          @click="getFlattenedView"
        />
      </VBtnGroup>
      <VTooltip location="top" text="Toggle Version Mode">
        <template #activator="{ props: activatorProps }">
          <VSwitch
            v-if="hasVersionMode"
            v-model="isVersionMode"
            v-bind="activatorProps"
            inset
            color="primary"
            label="Version"
            density="compact"
            hide-details
            class="flex-grow-0 mr-2"
          />
        </template>
      </VTooltip>
    </div>
    <VAlert
      v-if="dropError"
      closable
      type="warning"
      icon="mdi-alert-circle"
      text="Cannot upload Folders. Drop files only."
    />
    <VAlert
      v-if="tableError"
      closable
      type="error"
      icon="mdi-alert-circle"
      :text="tableError"
    />
    <VCard ref="dropZoneRef" flat>
      <NestedTable
        :is-version-mode="isVersionMode"
        :data-table-items="dataTableItems"
        :selected-items="selectedItems"
        @update:items="(val) => (selectedItems = val)"
      />
      <VOverlay
        v-model="isOverDropZone"
        contained
        class="align-center justify-center text-h6 text-white"
        >Drop Files to Upload</VOverlay
      >
    </VCard>
  </div>
</template>

<script setup>
import { useDropZone } from '@vueuse/core'
import { computed, inject, onUnmounted, ref } from 'vue'
import { useBuckets } from '../helpers/useBuckets'
import { useDrop } from '../helpers/useDrop'
import BucketBreadcrumbs from './Components/BucketBreadcrumbs.vue'
import DownloadButton from './Components/DownloadButton.vue'
import NestedTable from './Components/NestedTable.vue'
import CreateModal from './Modals/CreateModal.vue'
import DeleteModal from './Modals/DeleteModal.vue'
import MultiFileModal from './Modals/MultiFileModal.vue'
import UploadModal from './Modals/UploadModal.vue'

const api = inject('api')
const { getFlattenedView, isFlat, bucketResource, bucketState } =
  useBuckets(api)
const { dropZoneRef, onDrop, dropModal, dropError, clearModal, clearError } =
  useDrop(api)
const { isOverDropZone } = useDropZone(dropZoneRef, onDrop)
onUnmounted(clearTimeout(clearError))

// TODO CMP-127 - Update when Version mode is restored
const hasVersionMode = ref(false)
const isVersionMode = ref(false)

const tableError = ref()
const selectedItems = ref()
const dataTableItems = computed(() => {
  let list = bucketState.value?.dir_list
  if (isVersionMode.value) {
    return list
  }
  return list.filter((item) =>
    !item.is_file ? item : item.is_delete_marker ? false : item
  )
})
</script>
<style scoped></style>
