import { computed, ref } from 'vue'
import { convertObjectToFormData } from './axiosHelper'

const buckets = ref()
const bucketState = ref()
const bucketLocation = ref()
const bucketResource = ref()
const bucketPath = ref()
const bucketLoading = ref(false)
const isFlat = ref()

const currentPathForm = computed(() => {
  const currentPath =
    bucketState.value?.path_dirs[bucketState.value.path_dirs.length - 1]
  if (currentPath) {
    return {
      path: currentPath.path,
      name: currentPath.name,
      flat: isFlat.value ? 'True' : 'False'
    }
  }
  return {
    path: '',
    name: '',
    flat: isFlat.value ? 'True' : 'False'
  }
})

export function useBuckets(api = {}) {
  const currentError = ref()
  const getBuckets = async () => {
    try {
      const response = await api.base.instance.get('ajax/s3-list-buckets/')
      buckets.value = response.data.bucket_info
      currentError.value = ''
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      currentError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  }

  const getResourceSelection = async (resource) => {
    try {
      bucketLoading.value = true
      const response = await api.base.instance.get(
        `ajax/s3-browser-info/${resource.id}/`
      )
      bucketLocation.value = response.data.location
      bucketResource.value = response.data.resource
      bucketState.value = response.data.state
      bucketPath.value = response.data.state.full_path
      isFlat.value = response.data.state.flat
      bucketLoading.value = false
      currentError.value = ''
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      currentError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  }

  const updateResourceSelection = async (newResource) => {
    bucketLocation.value = newResource.location
    bucketResource.value = newResource.resource
    bucketState.value = newResource.state
    bucketPath.value = newResource.state.full_path
  }

  const fetchSelection = async (form) => {
    try {
      const formData = convertObjectToFormData(form)
      const response = await api.base.instance.post(
        `ajax/s3-browser-info/${bucketResource.value.id}/`,
        formData
      )
      updateResourceSelection(response.data)
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      currentError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  }

  const getFlattenedView = async () => {
    // Flatten form created here to handle the props update delay from the above emit
    const flattenForm = {
      path: '',
      flat: !isFlat.value ? 'True' : 'False'
    }
    try {
      bucketLoading.value = true
      const formData = convertObjectToFormData(flattenForm)
      const flattenResponse = await api.base.instance.post(
        `ajax/s3-browser-info/${bucketResource.value.id}/`,
        formData
      )
      isFlat.value = !isFlat.value
      updateResourceSelection(flattenResponse.data)
      bucketLoading.value = false
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      currentError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  }

  const refreshResource = async () => fetchSelection(currentPathForm.value)

  return {
    getBuckets,
    getResourceSelection,
    getFlattenedView,
    updateResourceSelection,
    fetchSelection,
    refreshResource,
    currentError,
    buckets,
    bucketState,
    bucketLocation,
    bucketLoading,
    bucketResource,
    bucketPath,
    isFlat
  }
}
