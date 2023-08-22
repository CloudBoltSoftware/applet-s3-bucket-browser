import { computed, ref } from 'vue'
import { useBuckets } from './useBuckets'

const dropZoneRef = ref(null)
const dropError = ref()
const dropModal = ref(false)
const dropFiles = ref([])

export function useDrop() {
  const { bucketResource, bucketPath } = useBuckets()

  const dropFilesForm = computed(() => ({
    bucket_name: bucketResource.value.name,
    path: bucketPath.value
  }))

  const onDrop = (files) => {
    if (files) {
      dropFiles.value = files.filter((file) => file.type !== '')
      dropModal.value = true
    }
    if (!files.findIndex((file) => file.type === '')) {
      dropError.value = true
      clearError()
    }
  }

  const clearError = () => setTimeout(() => (dropError.value = false), 5000)
  const clearModal = () => (dropModal.value = !dropModal.value)

  return {
    onDrop,
    clearModal,
    clearError,
    dropZoneRef,
    dropFilesForm,
    dropError,
    dropModal,
    dropFiles
  }
}
