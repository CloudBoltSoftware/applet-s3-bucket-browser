<template>
  <ErrorIcon :error="restoreError" />
  <VBtn
    icon="mdi-file-undo"
    :title="buttonText"
    :disabled="isDeleteMarker"
    @click="restoreItem"
  />
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { convertObjectToFormData } from '../../helpers/axiosHelper'
import { useBuckets } from '../../helpers/useBuckets'
import ErrorIcon from './ErrorIcon.vue'
/**
 * @typedef {Object} Props
 * @property {String} Props.itemKey - The original file item key
 * @property {Boolean} Props.isDeleteMarker - Boolean if the item is a delete marker (Delete markers are metadata and cannot be restored)
 * @property {String} Props.versionId - The version id for a version of the item
 * @property {Boolean} Props.buttonShowId - Boolean if button text should show the version ID
 */
/** @type {Props} */
const props = defineProps({
  itemKey: {
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
  },
  buttonShowId: {
    type: Boolean,
    default: false
  }
})

const api = inject('api')
const { bucketResource, refreshResource } = useBuckets(api)
const restoreError = ref()
const buttonText = computed(() =>
  props.buttonShowId
    ? `Restore Latest Version [${props.versionId}]`
    : 'Restore File'
)
const retoreItemForm = computed(() => ({
  resource_id: bucketResource.value.id,
  version_id: props.versionId,
  key: props.itemKey
}))

const restoreItem = async () => {
  try {
    const formData = convertObjectToFormData(retoreItemForm.value)
    await api.v3.cmp.inboundWebHooks.runPost(
      's3_bucket_browser/promote_version',
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
