<template>
  <VForm 
    @submit.prevent="emit('update:fetch',selectionForm)">
    <VBtn
      variant="text"
      :title="item.name"
      type="submit"
      class="text-none font-weight-regular text-body-1"
      color="blue-darken-3"
    >{{ item.name }}</VBtn>
  </VForm>
</template>

<script setup>
import { computed, onUpdated, ref } from "vue";
/**
 * @typedef {Object} Props
 * @property {Object} Props.item - The current S3 Bucket folder item 
 */
/** @type {Props} */
const props = defineProps({
  item: {
    type: Object,
    default: () => {},
  }
});

const selectedPath = ref('')
const selectedName = ref('')
const emit = defineEmits(["update:fetch"]);
const selectionForm = computed(() => ({
  path: selectedPath.value,  // Encoding path early leads to double encoding '/'
  name: encodeURIComponent(selectedName.value)
  })
)
onUpdated(() => {
  selectedPath.value = encodeURIComponent(props.item.url)
  selectedName.value = encodeURIComponent(props.item.name)

});

</script>
<style scoped></style>
