<template>
  <VForm @submit.prevent="fetchSelection(selectionForm)">
    <VBtn
      variant="text"
      :title="name"
      type="submit"
      class="text-none font-weight-regular text-body-1"
      color="blue-darken-3"
      :class="isDeleted ? 'dim' : ''"
      >{{ name }}</VBtn
    >
  </VForm>
</template>

<script setup>
import { computed, inject, onUpdated, ref } from 'vue'
import { useBuckets } from '../../helpers/useBuckets'
/**
 * @typedef {Object} Props
 * @property {Object} Props.url - The current S3 Bucket folder url
 * @property {Object} Props.name - The current S3 Bucket folder name
 */
/** @type {Props} */
const props = defineProps({
  url: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  isDeleted: {
    type: Boolean,
    default: false
  }
})

const selectedPath = ref('')
const selectedName = ref('')
const api = inject('api')
const { bucketResource, fetchSelection } = useBuckets(api)

const selectionForm = computed(() => ({
  resource_id: bucketResource.value.id,
  path: selectedPath.value, // Encoding path early leads to double encoding '/'
  name: encodeURIComponent(selectedName.value)
}))
onUpdated(() => {
  selectedPath.value = encodeURIComponent(props.url)
  selectedName.value = encodeURIComponent(props.name)
})
</script>
<style scoped>
.dim {
  opacity: 0.6;
}
</style>
