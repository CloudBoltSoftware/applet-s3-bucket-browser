<template>
  <ErrorIcon :error="restoreError" />
  <VBtn
    icon="mdi-file-undo"
    title="Restore File"
    :disabled="isDeleted"
    @click="restoreItem"
  />
</template>

<script setup>
import { computed, inject, ref } from 'vue';
import { convertObjectToFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';
import ErrorIcon from './ErrorIcon.vue';
/**
 * @typedef {Object} Props
 * @property {String} Props.itemKey - The file item key
 * @property {String} Props.path - The file item path
 * @property {Boolean} Props.isDeleteMarker - Boolean if the item is deleted
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
  isDeleteMarker: {
    type: Boolean,
    default: false
  },
  versionId: {
    type: String,
    default: ''
  }
})

const api = inject('api')
const { bucketResource, bucketPath, refreshResource, isFlat } = useBuckets(api)
const restoreError = ref()
const isDeleted = computed(() => props.isDeleteMarker)
const retoreItemForm = computed(() => ({
  version_id: props.versionId,
  key: props.itemKey,
  state: JSON.stringify({
    full_path: bucketPath.value,
    flat: isFlat.value
  }),
  restore: true
}))

const restoreItem = async () => {
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
