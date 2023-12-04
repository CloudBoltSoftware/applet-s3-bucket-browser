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
      resource_id: bucketResource.value.id,
      path: currentPath.path,
      name: currentPath.name,
      flat: isFlat.value ? 'True' : 'False'
    }
  }
  return {
    resource_id: bucketResource.value.id,
    path: '',
    name: '',
    flat: isFlat.value ? 'True' : 'False'
  }
})

export function useBuckets(api = {}) {
  const currentError = ref()
  const getBuckets = async () => {
    try {
      const response = await api.v3.cmp.inboundWebHooks.runGet(
        's3_bucket_browser/get_buckets'
      )
      buckets.value = response.bucket_info
      currentError.value = ''
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      currentError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  }

  const getResourceSelection = async (resource) => {
    try {
      bucketLoading.value = true
      const response = await api.v3.cmp.inboundWebHooks.runPost(
        's3_bucket_browser/get_browser',
        {
          resource_id: resource.id,
          path: ''
        }
      )
      bucketLocation.value = response.location
      bucketResource.value = response.resource
      bucketState.value = response.state
      bucketPath.value = response.state.full_path
      isFlat.value = response.state.flat
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
      const response = await api.v3.cmp.inboundWebHooks.runPost(
        's3_bucket_browser/get_browser',
        formData
      )

      updateResourceSelection(response)
    } catch (error) {
      // When using API calls, it's a good idea to catch errors and meaningfully display them.
      currentError.value = `(${error.code}) ${error.name}: ${error.message}`
    }
  }

  const getFlattenedView = async () => {
    // Flatten form created here to handle the props update delay from the above emit
    try {
      bucketLoading.value = true
      const flattenResponse = await api.v3.cmp.inboundWebHooks.runPost(
        's3_bucket_browser/get_browser',
        {
          resource_id: bucketResource.value.id,
          path: '',
          flat: !isFlat.value ? 'True' : 'False'
        }
      )

      isFlat.value = !isFlat.value
      updateResourceSelection(flattenResponse)
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
