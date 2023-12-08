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
    <VProgressLinear
      v-if="!bucketResource && isLoading"
      indeterminate
      class="mt-3"
      color="blue-darken-4"
      rounded
    />
    <VAlert
      v-if="showError"
      closable
      type="error"
      icon="mdi-alert-circle"
      :text="showError"
    />
    <BucketDisplay v-if="bucketResource" />
  </VSheet>
</template>

<script setup>
import { computed, onMounted, provide, watch } from 'vue'
import avatarUrl from '../assets/Icons_Storage_S3.png'
import { useBuckets } from '../helpers/useBuckets'
import BucketDisplay from './BucketDisplay.vue'
/**
 * @typedef {Object} Props
 * @property {ReturnType<import("@cloudbolt/js-sdk").createApi>} Props.api - The authenticated API instance
 * @property {Object} Props.context - The applet context (on Resource Tab view contains current resource info)
 */
/** @type {Props} */
const props = defineProps({
  api: {
    type: Object,
    required: true
  },
  context: {
    type: Object,
    required: true
  }
})

provide('api', props.api)
const {
  getBuckets,
  getResourceSelection,
  currentError,
  buckets,
  bucketResource,
  isLoading
} = useBuckets(props.api)
const preLoadedResource = computed(
  () =>
    buckets.value &&
    props.context.resource &&
    buckets.value.find((bucket) => bucket.name === props.context.resource.name)
)
const showError = computed(() => currentError.value)

onMounted(getBuckets)
watch(
  () => preLoadedResource.value,
  (currentResource) => {
    getResourceSelection(currentResource)
  }
)
</script>
<style scoped></style>
