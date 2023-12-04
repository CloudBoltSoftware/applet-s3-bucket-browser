<template>
  <ErrorIcon :error="restoreError" />
  <VBtn icon="mdi-file-undo" title="Restore File" @click="restoreItem" />
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { convertObjectToFormData } from '../../helpers/axiosHelper'
import { useBuckets } from '../../helpers/useBuckets'
import ErrorIcon from './ErrorIcon.vue'
/**
 * @typedef {Object} Props
 * @property {String} Props.itemKey - The file item key
 * @property {String} Props.path - The file item path
 * @property {String} Props.versionId - The version id for the Bucket item
 */
/** @type {Props} */

const props = defineProps({
  itemKey: {
    type: String,
    default: ''
  },
  path: {
    type: String,
    default: ''
  },
  versionId: {
    type: String,
    default: ''
  }
})

const api = inject('api')
const { bucketResource, refreshResource } = useBuckets(api)
const restoreError = ref()

// TODO CMP-127 - This button requires versioning and additional work
// Currently is disabled in the example
const retoreItemForm = computed(() => ({
  key: props.itemKey,
  path: props.path,
  version_id: props.versionId,
  restore: 'True'
}))

const restoreItem = async () => {
  // TODO - Backend issue
  try {
    const formData = convertObjectToFormData(retoreItemForm.value)
    await api.base.instance.post(
      `ajax/s3-promote-version/${bucketResource.value.id}/`,
      formData
    )
    refreshResource()
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    restoreError.value = error
  }
}
</script>
<style scoped></style>
