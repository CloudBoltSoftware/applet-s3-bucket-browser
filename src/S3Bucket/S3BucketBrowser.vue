<template>
  <VSheet class="px-3 py-4" rounded>
    <div class="d-inline-flex w-100">
      <div class="w-25 d-inline-flex mt-1">
        <VAvatar :image="avatarUrl" />
        <span class="ml-3 text-h5">S3 Bucket Manager</span>
      </div>
      <VSelect 
        v-if="!preLoadedResource"
        label="Buckets:" 
        :items="buckets"
        item-title="name"
        item-value="id"
        return-object
        class="w-75"
        placeholder="Select S3 Bucket"
        :hide-details="true"
        @update:modelValue="getResourceSelection"
      />
    </div>
    <VProgressLinear v-if="!bucketResource && isLoading" indeterminate class="mt-3" color="blue-darken-4" rounded />
    <VAlert v-if="bucketError" closable type="error" icon="mdi-alert-circle" :text="bucketError" />
    <BucketDisplay 
      v-if="bucketResource"
      :state="bucketState"
      :is-flat="isFlat"
      @update:resource="(res) => updateResourceSelection(res)"
      @update:updateFlatten="() => isFlat = !isFlat" />
  </VSheet>
</template>

<script setup>
import { computed, onMounted, provide, ref, watch } from "vue";
import avatarUrl from '../assets/Icons_Storage_S3.png';
import BucketDisplay from './BucketDisplay.vue';
/**
 * @typedef {Object} Props
 * @property {ReturnType<import("@cloudbolt/js-sdk").createApi>} Props.api - The authenticated API instance
 * @property {Object} Props.context - The applet context (on Resource Tab view contains current resource info)
 */
/** @type {Props} */
const props = defineProps({
  api: {
    type: Object,
    required: true,
  },
  context: {
    type: Object,
    required: true,
  },
});

const buckets = ref()
const bucketState = ref()
const bucketLocation = ref()
const bucketResource = ref()
const bucketPath = ref()
const bucketError = ref()
const isFlat = ref()
const isLoading = ref(false)
const preLoadedResource = computed(() => buckets.value && props.context.resource && buckets.value.find((bucket) => bucket.name === props.context.resource.name))
provide('api', props.api)
provide('location', bucketLocation)
provide('resource', bucketResource)
provide('path', bucketPath)

//  TODO CMP-54 Handle CSRF Token
// Currently users must visit the dashboard before the CUI
let token = sessionStorage.getItem("csrfToken");
if (token) {
  // eslint-disable-next-line vue/no-mutating-props
  props.api.base.instance.defaults.headers.common['X-CSRFTOKEN'] = token
} else {
  bucketError.value = 'Error, no token found. Please navigate to the dashboard to automatically set the token before returning to the CUI'
}

const getBuckets = async () => {
  try {
    const response = await props.api.base.instance.get('http://localhost:8001/ajax/s3-list-buckets/')
    buckets.value = response.data.bucket_info
    bucketError.value = ''
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    bucketError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}

const getResourceSelection = async (resource) => {
  try {
    isLoading.value = true
    const response = await props.api.base.instance.get(`http://localhost:8001/ajax/s3-browser-info/${resource.id}/`)
    bucketLocation.value = response.data.location
    bucketResource.value = response.data.resource
    bucketState.value = response.data.state
    bucketPath.value = response.data.state.full_path
    isFlat.value = response.data.state.flat
    isLoading.value = false
    bucketError.value = ''
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    bucketError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}

const updateResourceSelection = async (newResource) => {
  bucketLocation.value = newResource.location
  bucketResource.value = newResource.resource
  bucketState.value = newResource.state
  bucketPath.value = newResource.state.full_path
}

onMounted(getBuckets)
watch(
  () => preLoadedResource.value,
  (currentResource) => {
    getResourceSelection(currentResource)
  }
)
</script>
<style scoped></style>
