<template>
  <VTooltip location="start" :text="restoreError">
    <template #activator="{ props: activatorProps }">
      <VIcon
        v-if="restoreError"
        v-bind="activatorProps"
        color="error"
        size="x-small"
        icon="mdi-alert-circle"
        class="mt-1"
      />
    </template>
  </VTooltip>
  <VBtn icon="mdi-file-undo" title="Restore File" :disabled="isDeleted" @click="restoreItem" />
</template>

<script setup>
import { computed, inject, ref } from 'vue';
import { convertObjectToFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';

/**
 * @typedef {Object} Props
 * @property {Object} Props.item - The S3 Bucket file item
 */
/** @type {Props} */

const props = defineProps({
  item: {
    type: Object,
    default: () => {}
  }
})

const api = inject('api')
const { bucketResource, bucketPath, refreshResource, isFlat } = useBuckets(api)
const restoreError = ref()
const isDeleted = computed(() => props.item.is_delete_marker)
const retoreItemForm = computed(() => ({
  version_id: props.item.version_id,
  key: props.item.key,
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
    restoreError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}
</script>
<style scoped></style>
