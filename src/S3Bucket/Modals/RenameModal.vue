<template>
  <VDialog
    v-model="renameDialog"
    width="1200"
    @update:model-value="(val) => !val && onCancel()"
  >
    <template #activator="{ props: renameProps }">
      <VBtn v-bind="renameProps" :disabled="isDeleted" icon="mdi-pencil-circle" title="Rename" />
    </template>
    <VCard class="pa-3">
      <VForm
        @submit.prevent="renameObject"
        @update:model-value="(val) => (formIsValid = val)"
      >
        <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
          Rename Object
          <VBtn
            icon="mdi-close"
            title="Close this dialog"
            variant="text"
            @click="onCancel"
          />
        </VCardTitle>
        <VCardText>
          <VTextField
            v-model="renameNew"
            label="New Object Name"
            placeholder="Enter name here"
            type="text"
            :rules="requiredRule"
            required
          />
        </VCardText>
        <VCardActions class="d-flex justify-end px-3 mb-1">
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
            :loading="isSubmitting"
            :disabled="!formIsValid"
            type="submit"
            variant="flat"
            color="primary"
            size="large"
            :width="isSubmitting ? '150' : '100'"
            class="px-4"
            >Rename
            <template #loader>Submitting…</template>
          </VBtn>
        </VCardActions>
      </VForm>
    </VCard>
  </VDialog>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue';
import { convertObjectToFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';

/**
 * @typedef {Object} Props
 * @property {String} Props.name - The selected S3 Bucket item's name
 * @property {Boolean} Props.isDeleted - Boolean if the item has a delete marker
 */
/** @type {Props} */

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  isDeleted: {
    type: Boolean,
    default: false
  }
})

const api = inject('api')
const { bucketPath, bucketResource, refreshResource } = useBuckets(api)
const isSubmitting = ref(false)
const renameDialog = ref(false)
const formIsValid = ref(false)
const formError = ref()
const renameOld = ref('')
const renameNew = ref('')

const renameForm = computed(() => ({
  old_object_name: renameOld.value,
  new_object_name: renameNew.value,
  path: bucketPath.value,
  bucket_name: bucketResource.value.name
}))

const requiredRule = [
  (value) => !!value || 'This field is required',
  (value) => value !== renameOld.value || 'New name needs to be different'
]

const onCancel = () => {
  renameDialog.value = false
  renameNew.value = renameOld.value
  formError.value = ''
}

watch(
  () => renameDialog.value === true,
  () => {
    ;(renameOld.value = props?.name), (renameNew.value = props?.name)
  }
)

async function renameObject() {
  try {
    isSubmitting.value = true
    const formData = convertObjectToFormData(renameForm.value)
    // Because this function is `async`, we can use `await` to wait for the API call to finish.
    // Alternatively, we could use `.then()` and `.catch()` to handle the response.
    // https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises
    await api.base.instance.post(
      `ajax/s3-rename-object/${bucketResource.value.id}/`,
      formData
    )
    isSubmitting.value = false
    renameDialog.value = false
    refreshResource()
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    formError.value = `(${error.code}) ${error.name}: ${error.message}`
    formIsValid.value = false
    isSubmitting.value = false
  }
}
</script>
<style scoped></style>
