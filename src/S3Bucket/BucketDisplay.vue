<template>
  <div class="d-flex flex-column">
    <BucketBreadcrumbs 
      :state="state"
      :name="resource.name"
      class="justify-start"
      @update:fetch="(val) => fetchSelection(val)"
      />
    <div class="d-flex justify-space-between">
      <VBtnGroup>
        <DownloadButton :selected-items="selectedItems" />
        <DeleteModal  :selected-items="selectedItems" @update:refresh="refreshResource" />
        <MultiFileModal v-if="dropModal" :drop-modal="dropModal" :drop-files="dropFiles" :drop-files-form="dropFilesForm" @update:refresh="refreshResource" @update:clear="() => dropModal = !dropModal"/>
        <UploadModal @update:refresh="refreshResource"/>
        <CreateModal @update:refresh="refreshResource"/>
        <VBtn v-if="isFlat" icon="mdi-folder-eye" title="Toggle Folder View" size="x-large" @click="fetchFlattenedView"/>
        <VBtn v-else icon="mdi-view-headline"  title="Toggle Flat List View" size="x-large" @click="fetchFlattenedView" />
      </VBtnGroup>
      <VTooltip location="top" text="Toggle Version Mode" >
        <template #activator="{ props: activatorProps }">
          <VSwitch v-if="hasVersionMode" v-model="isVersionMode" v-bind="activatorProps" inset color="primary" label="Version" density="compact" hide-details class="flex-grow-0 mr-2"/>
        </template>
      </VTooltip>
    </div>
      <VAlert v-if="dropError" closable type="warning" icon="mdi-alert-circle" text="Cannot upload Folders. Drop files only." />
      <VAlert v-if="tableError" closable type="error" icon="mdi-alert-circle" :text="tableError" />
      <VCard ref="dropZoneRef" flat>
        <NestedTable 
          :is-loading="isLoading"
          :state="state"
          :is-version-mode="isVersionMode"
          :data-table-items="dataTableItems"
          :selected-items="selectedItems"
          @update:fetch="(val) => fetchSelection(val)"
          @update:refresh="refreshResource"
          @update:items="(val) => selectedItems = val"
          />
        <VOverlay v-model="isOverDropZone" contained class="align-center justify-center text-h6 text-white">Drop Files to Upload</VOverlay>
    </VCard>
  </div>
</template>

<script setup>
import { useDropZone } from '@vueuse/core';
import { computed, inject, onUnmounted, ref, toValue } from "vue";
import { convertObjectToFormData } from '../helpers/axiosHelper';
import BucketBreadcrumbs from "./Components/BucketBreadcrumbs.vue";
import DownloadButton from "./Components/DownloadButton.vue";
import NestedTable from "./Components/NestedTable.vue";
import CreateModal from "./Modals/CreateModal.vue";
import DeleteModal from "./Modals/DeleteModal.vue";
import MultiFileModal from './Modals/MultiFileModal.vue';
import UploadModal from "./Modals/UploadModal.vue";

/**
 * @typedef {Object} Props
 * @property {Object} Props.state - The selected S3 Bucket state
 * @property {Boolean} Props.isFlat - Boolean if the current view is flat vs nested folders 
 */
/** @type {Props} */
const props = defineProps({
  state: {
    type: Object,
    default: () => {},
  },
  isFlat: {
    type: Boolean,
    required: true
  }
});
const api = inject('api')
const path =  inject('path')
const resource = toValue(inject('resource'))
const emit = defineEmits(["update:updateFlatten", "update:resource"]);

// TODO CMP-127 - Update when Version mode is restored
const hasVersionMode = ref(false)
const isVersionMode = ref(false)

const isLoading = ref(false)
const tableError = ref()
const selectedItems = ref()
const dataTableItems = computed(() => {
  let list = props.state?.dir_list
  if (isVersionMode.value) {
    return list
  } 
  return list.filter((item) => !item.is_file ? item : item.is_delete_marker ? false : item )
})

const currentPathForm = computed(() => {
  const currentPath = props.state.path_dirs[props.state.path_dirs.length - 1]
  if (currentPath) {
    return {
      path: currentPath.path,
      name: currentPath.name
    }
  } 
  return {
    path: '',
    name: ''
  }
})

const dropZoneRef = ref(null)
const dropError = ref()
const dropModal = ref(false)
const dropFiles = ref([])
const dropFilesForm = computed(() => ({
  bucket_name: resource.name,
  path: path.value
}))
const onDrop = (files) => {
  if (files) {
    dropFiles.value = files.filter(file => file.type !== '')
    dropModal.value = true
  }
  if (!files.findIndex(file => file.type === '')) {
    dropError.value = true
    clearError()
  }
}
const { isOverDropZone } = useDropZone(dropZoneRef, onDrop)
const clearError = () => setTimeout(() => dropError.value = false, 5000)
onUnmounted(clearTimeout(clearError))

const fetchFlattenedView = async () => {
  emit("update:updateFlatten")
  // Flatten form created here to handle the props update delay from the above emit
  const flattenForm = {
    path: '',
    flat: !props.isFlat ? 'True' : 'False'
  }
  try {
    isLoading.value = true
    const formData = convertObjectToFormData(flattenForm)
    const flattenResponse = await api.base.instance.post(`http://localhost:8001/ajax/s3-browser-info/${resource.id}/`, formData)
    emit("update:resource", flattenResponse.data)
    isLoading.value = false
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    tableError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}

const fetchSelection = async (form) => {
  try {
    const formData = convertObjectToFormData(form)
    const response = await api.base.instance.post(`http://localhost:8001/ajax/s3-browser-info/${resource.id}/`, formData)
    emit("update:resource", response.data)
    dropError.value = false
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    tableError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}

const refreshResource = async () => fetchSelection(currentPathForm.value)
</script>
<style scoped></style>
