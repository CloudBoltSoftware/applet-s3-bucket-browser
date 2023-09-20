<template>
  <template v-for="(fileName, index) in fileNames">
    <VChip
      v-if="index < 5"
      :key="fileName"
      variant="outlined"
      class="me-2"
    >
      {{ fileName }}
    </VChip>
    <span
      v-else-if="index === 5"
      :key="`fileCount_${fileName}`"
      class="text-overline text-grey-darken-3 mx-2"
    >
      + {{ fileNames.length - 5 }} File(s)
    </span>
  </template>
</template>


<script setup>
/**
 * @typedef {Object} Props
 * @property {Array} Props.fileNames - Array of files uploaded
 */
/** @type {Props} */
defineProps({
  fileNames: {
    type: Array,
    default: () => [String]
  }
})
</script>
<style scoped></style>
