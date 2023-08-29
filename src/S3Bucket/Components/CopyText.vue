<template>
  <VTooltip location="top">
    <template #activator="{ props: activatorProps }">
      <VIcon
        class="mr-1"
        size="small"
        :class="showCopied ? 'green--text' : ''"
        v-bind="{ ...activatorProps, ...$attrs }"
        @click="copyToClipboard"
      >
        {{ showCopied ? 'mdi-check' : 'mdi-content-copy' }}
      </VIcon>
    </template>
    <span>{{ tooltipText }}</span>
  </VTooltip>
</template>

<script setup>
/**
 * This component provides copy-to-clipboard feature
 * It displays an icon along with a tooltip
 * Accepts text-to-copy prop
 * For eg: <CopyText :text-to-copy="test_value" />
 * */
import { computed, ref } from 'vue';

const props = defineProps({
  textToCopy: {
    type: String,
    default: ''
  }
})

const showCopied = ref(false)

const copyToClipboard = () => {
  navigator.clipboard.writeText(props.textToCopy)
  showCopied.value = true
  setTimeout(() => {
    showCopied.value = false
  }, 600)
}

const tooltipText = computed(() => {
  return showCopied.value ? "Copied!" : "Copy to clipboard"
})
</script>

<style scoped>
.green--text {
  color: green !important;
}

.v-tooltip__content {
  white-space: nowrap;
}
</style>
