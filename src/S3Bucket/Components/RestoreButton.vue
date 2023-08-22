<template>
  <VTooltip location="start" :text="restoreError" >
    <template #activator="{ props: activatorProps }">
      <VIcon v-if="restoreError" v-bind="activatorProps" color="error" size="x-small" icon="mdi-alert-circle" class="mt-1"/>
    </template>
  </VTooltip>
  <VBtn icon="mdi-file-undo" title="Restore File" @click="restoreItem"  />
</template>
    
<script setup>
import { computed, inject, ref } from "vue";
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
  },
});

const api = inject('api')
const { bucketResource, refreshResource } = useBuckets(api)
const restoreError = ref()

// TODO CMP-127 - This button requires versioning and additional work 
// Currently is disabled in the example
const retoreItemForm = computed(() => ({
  key: props.item.key,
  path: props.item.path,
  version_id:  props.item.version_id,
  restore: 'True'
}))

const restoreItem = async () => {
  // TODO - Backend issue
  try {
    const formData = convertObjectToFormData(retoreItemForm.value)
    await api.base.instance.post(`http://localhost:8001/ajax/s3-promote-version/${bucketResource.value.id}/`, formData)
    refreshResource()
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    restoreError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}
</script>
<style scoped></style>
