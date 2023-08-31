<template>
  <ErrorIcon :error="downloadError" />
  <VBtn
    icon="mdi-file-download"
    :disabled="isDisabled"
    size="x-large"
    title="Download"
    @click="downloadFiles"
  />
</template>

<script setup>
import { computed, inject, ref } from 'vue';
import { convertObjectToFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';
import ErrorIcon from './ErrorIcon.vue';
/**
 * @typedef {Object} Props
 * @property {Array} Props.selectedItems - The selected S3 Bucket items
 */
/** @type {Props} */
const props = defineProps({
  selectedItems: {
    type: Array,
    default: () => []
  }
})
const api = inject('api')
const { bucketResource, bucketLocation } = useBuckets()
const downloadError = ref()

// Disabled download if there are no items, or folder items
const isDisabled = computed(
  () =>
    props.selectedItems.length === 0 ||
    props.selectedItems.every((entry) => entry.is_file)
)

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
      const response = await api.base.instance.post(
        `ajax/s3-download-file/${bucketResource.value.id}/`,
        formData
      )
      if (response.status === 200) {
        window.open(response.data.url, '_blank')
      }
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      downloadError.value = error
    }
  })
}
</script>
<style scoped></style>
