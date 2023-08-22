<template>
  <VTooltip location="start" :text="downloadError" >
    <template #activator="{ props: activatorProps }">
      <VIcon v-if="downloadError" v-bind="activatorProps" color="error" size="x-small" icon="mdi-alert-circle" class="mt-1"/>
    </template>
  </VTooltip>
  <VBtn icon="mdi-file-download" :disabled="isDisabled" size="x-large" title="Download" @click="downloadFiles"/>
</template>
    
<script setup>
import { computed, inject, ref } from "vue";
import { convertObjectToFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';
/**
 * @typedef {Object} Props
 * @property {Array} Props.selectedItems - The selected S3 Bucket items
 */
/** @type {Props} */
const props = defineProps({
  selectedItems: {
    type: Array,
    default: () => [],
  },
});
const api = inject('api')
const { bucketResource, bucketLocation } = useBuckets()
const downloadError = ref()

// Disabled download if there are no items, or folder items
const isDisabled = computed(() => {
  if (props.selectedItems.length === 0 || props.selectedItems.findIndex((entry) => !entry.is_file) !== -1) {
    return true
  }
  return false
})

const filePaths = computed(() => 
  props.selectedItems.map((item) => ({
    path: item.url,
    location: bucketLocation.value
  }))
)

async function downloadFiles() {
  filePaths.value.forEach(async (entry) => {
    try {
      const formData = convertObjectToFormData(entry)
      // Because this function is `async`, we can use `await` to wait for the API call to finish.
      // Alternatively, we could use `.then()` and `.catch()` to handle the response.
      // https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises
      const response = await api.base.instance.post(`http://localhost:8001/ajax/s3-download-file/${bucketResource.value.id}/`,  formData)
      if (response.status === 200) {
        window.open(response.data.url, "_blank")
      }
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      downloadError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  })
}
</script>
<style scoped></style>
