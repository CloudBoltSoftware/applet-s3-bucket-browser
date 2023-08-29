<template>
  <VDialog
    v-model="createDialog"
    width="1200"
    @update:model-value="(val) => !val && onCancel()"
  >
    <template #activator="{ props: createProps }">
      <VBtn
        v-bind="createProps"
        icon="mdi-folder-plus"
        title="Add New Folder"
        size="x-large"
      />
    </template>
    <VCard class="pa-3">
      <VForm
        @submit.prevent="submitCreateModal"
        @update:model-value="(val) => (formIsValid = val)"
      >
        <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
          <div>
            Create folder at
            <span class="font-italic">{{
              bucketPath ? bucketPath : 'Root folder'
            }}</span>
          </div>
          <VBtn
            icon="mdi-close"
            title="Close this dialog"
            variant="text"
            @click="onCancel"
          />
        </VCardTitle>
        <VCardText>
          <VCol cols="12">
            <VTextField
              v-model="newFolder"
              label="Folder Name"
              placeholder="Enter folder name"
              prepend-icon="mdi-folder-plus"
              type="text"
              :rules="requiredRule"
              required
            ></VTextField>
            <span class="pl-8">
              <VBtn
                prepend-icon="mdi-information"
                href="https://docs.aws.amazon.com/console/s3/object-keys"
                target="_blank"
                variant="text"
                class="text-capitalize font-weight-regular text-body-1"
                >See rules for naming</VBtn
              >
            </span>
          </VCol>
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
            :loading="isSubmitting"
            :disabled="!formIsValid"
            :width="isSubmitting ? '150' : '100'"
            prepend-icon="mdi-folder-plus"
            type="submit"
            variant="flat"
            color="primary"
            size="large"
            class="pr-4 pl-6"
            >Create
            <template #loader>Submitting…</template>
          </VBtn>
        </VCardAction>
      </VForm>
    </VCard>
  </VDialog>
</template>

<script setup>
import { computed, inject, ref } from 'vue';
import { convertObjectToFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';

const api = inject('api')
const { bucketPath, bucketResource, refreshResource } = useBuckets(api)

const newFolder = ref('')
const createFolderForm = computed(() => ({
  folder_name: newFolder.value,
  path: bucketPath.value,
  bucket_name: bucketResource.value.name
}))

const formIsValid = ref(false)
const formError = ref()
const isSubmitting = ref(false)
const createDialog = ref(false)
const requiredRule = [
  (value) => !!value || 'This field is required',
  (value) => !value.includes('/') || "Folder names can't contain '/''"
]

const onCancel = () => {
  createDialog.value = false
  newFolder.value = ''
  formError.value = ''
}

async function submitCreateModal() {
  try {
    isSubmitting.value = true
    const formData = convertObjectToFormData(createFolderForm.value)
    // Because this function is `async`, we can use `await` to wait for the API call to finish.
    // Alternatively, we could use `.then()` and `.catch()` to handle the response.
    // https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises
    await api.base.instance.post(
      `ajax/s3-create-folder/${bucketResource.value.id}/`,
      formData
    )
    isSubmitting.value = false
    createDialog.value = false
    newFolder.value = ''
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
