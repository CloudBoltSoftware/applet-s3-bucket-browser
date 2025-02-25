<template>
  <VDialog
    v-model="deleteDialog"
    width="1024"
    @update:model-value="(val) => !val && onCancel()"
  >
    <template #activator="{ props: deleteProps }">
      <VBtn
        v-bind="deleteProps"
        :disabled="isDisabled"
        icon="mdi-delete"
        title="Delete"
        size="x-large"
      />
    </template>
    <VForm @submit.prevent="deleteModal">
      <VCard class="pa-3" density="compact">
        <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
          <span>Delete Confirmation</span>
          <VBtn
            icon="mdi-close"
            title="Close this dialog"
            data-dismiss="modal"
            variant="text"
            @click="onCancel"
          />
        </VCardTitle>
        <VCardText class="py-0 ml-3">
          <p class="text-h6">
            <VIcon color="error" icon="mdi-alert" class="text-h5" />
            Are you sure you want to delete?
          </p>
          <p class="text-body-1">
            Note: If you have selected a folder, all objects in that folder will
            also be deleted.
          </p>
        </VCardText>
        <VCardAction class="d-flex justify-end px-3 mb-1">
          <VTooltip location="start" :text="formError">
            <template #activator="{ props: activatorProps }">
              <VIcon
                v-if="formError"
                v-bind="activatorProps"
                color="error"
                size="large"
                icon="mdi-alert-circle"
                class="mt-1"
              />
            </template>
          </VTooltip>
          <VBtn
            prepend-icon="mdi-close"
            variant="flat"
            size="large"
            class="px-4 mx-2"
            @click="onCancel"
            >Cancel</VBtn
          >
          <VBtn
            :loading="isDeleting"
            :width="isDeleting ? '175' : '150'"
            prepend-icon="mdi-delete"
            variant="flat"
            color="primary"
            size="large"
            class="px-4"
            type="submit"
            >Delete
            <template #loader>Deleting...</template>
          </VBtn>
        </VCardAction>
      </VCard>
    </VForm>
  </VDialog>
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { convertObjectToFormData } from '../../helpers/axiosHelper'
import { useBuckets } from '../../helpers/useBuckets'

/**
 * @typedef {Object} Props
 * @property {Array} Props.selectedItems - The selected S3 Bucket items
 */
/** @type {Props} */
const props = defineProps({
  selectedItems: {
    type: Array,
    default: () => []
  }
})
const api = inject('api')
const { bucketResource, refreshResource } = useBuckets(api)
const formError = ref()
const deleteDialog = ref(false)
const isDeleting = ref(false)
const isDisabled = computed(() => {
  if (
    props.selectedItems.length === 0 ||
    props.selectedItems.find((entry) => entry.is_delete_marker)
  ) {
    return true
  }
  return false
})

const filePath = computed(() => {
  const allFiles = []
  props.selectedItems.forEach((item) => {
    allFiles.push({
      file_path: item.url,
      object_type: item.item_type
    })
  })

  return allFiles
})
const deleteForm = computed(() => ({
  resource_id: bucketResource.value.id,
  all_files_path: JSON.stringify(filePath.value)
}))

const onCancel = () => {
  deleteDialog.value = false
  formError.value = ''
}

async function deleteModal() {
  try {
    isDeleting.value = true
    const formData = convertObjectToFormData(deleteForm.value)
    // Because this function is `async`, we can use `await` to wait for the API call to finish.
    // Alternatively, we could use `.then()` and `.catch()` to handle the response.
    // https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises
    await api.v3.cmp.inboundWebHooks.runPost(
      's3_bucket_browser/delete_item',
      formData
    )
    isDeleting.value = false
    deleteDialog.value = false
    refreshResource()
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    // In this case, we'll just log the error to the console.
    formError.value = `(${error.code}) ${error.name}: ${error.message}`
    isDeleting.value = false
  }
}
</script>
<style scoped></style>
