<template>
  <VTooltip location="start" :text="errorMessage">
    <template #activator="{ props: activatorProps }">
      <VIcon
        v-if="errorMessage"
        v-bind="activatorProps"
        color="error"
        :size="size"
        icon="mdi-alert-circle"
        class="mt-1"
      />
    </template>
  </VTooltip>
</template>

<script setup>
import { computed } from 'vue'
/**
 * @typedef {Object} Props
 * @property {Array} Props.error - Error object passed from api request
 * @property {Array} Props.size - Optional string for icon size
 */
/** @type {Props} */
const props = defineProps({
  error: {
    type: Object,
    default: () => {}
  },
  size: {
    type: String,
    default: 'x-small'
  }
})

const errorMessage = computed(() =>
  props.error
    ? `(${props.error.code}) ${props.error.name}: ${props.error.message}`
    : ''
)
</script>
<style scoped></style>
