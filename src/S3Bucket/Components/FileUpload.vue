<template>
  <VDialog
    v-model="fileDialog"
    width="1200"
    @update:model-value="(val) => !val && onCancel()"
  >
    <template #activator="{ props: fileProps }">
      <VBtn
        prepend-icon="mdi-file-upload"
        v-bind="fileProps"
        variant="flat"
        color="primary"
        size="x-large"
        title="Upload New File"
        class="px-4 flex-grow-1"
        >Upload a File</VBtn
      >
    </template>
    <VCard class="pa-3">
      <VForm
        @submit.prevent="fileUploadModal"
        @update:model-value="(val) => (formIsValid = val)"
      >
        <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
          <div>
            Upload file to
            <span class="font-italic">{{
              bucketPath ? bucketPath : 'Root folder'
            }}</span>
          </div>
          <VBtn
            icon="mdi-close"
            title="Close"
            data-dismiss="modal"
            variant="text"
            @click="onCancel"
          />
        </VCardTitle>
        <VCardText>
          <VFileInput
            v-model="uploadFile"
            :rules="requiredRule"
            clearable
            label="Upload File"
          />
        </VCardText>
        <VCardActions class="d-flex justify-end px-3 mb-1">
          <ErrorIcon size="large" :error="formError" />
          <VBtn
            prepend-icon="mdi-close"
            variant="flat"
            size="large"
            class="px-4 mx-2"
            @click="onCancel"
            >Cancel</VBtn
          >
          <VBtn
            :loading="isUploading"
            prepend-icon="mdi-file-upload"
            :disabled="!formIsValid"
            variant="flat"
            color="primary"
            size="large"
            class="px-4"
            type="submit"
            >Upload to S3
            <template #loader>Uploading...</template>
          </VBtn>
        </VCardActions>
      </VForm>
    </VCard>
  </VDialog>
</template>

<script setup>
import { inject, ref } from 'vue';
import { convertObjectToMultiFormData } from '../../helpers/axiosHelper';
import { useBuckets } from '../../helpers/useBuckets';
import ErrorIcon from './ErrorIcon.vue';

const api = inject('api')
const { bucketPath, bucketResource, refreshResource } = useBuckets(api)
const emit = defineEmits(['closeDialog'])
const isUploading = ref(false)
const uploadFile = ref([])
const uploadFileForm = ref({
  bucket_name: bucketResource.value.name,
  path: bucketPath.value
})
const formIsValid = ref(false)
const formError = ref()
const fileDialog = ref(false)
const requiredRule = [(value) => value.length > 0 || 'This field is required']

const onCancel = () => {
  emit('closeDialog')
  fileDialog.value = false
  formError.value = ''
  uploadFile.value = []
}

async function fileUploadModal() {
  try {
    isUploading.value = true
    const formData = convertObjectToMultiFormData(
      uploadFileForm.value,
      uploadFile.value,
      'file'
    )
    // Because this function is `async`, we can use `await` to wait for the API call to finish.
    // Alternatively, we could use `.then()` and `.catch()` to handle the response.
    // https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises
    await api.base.instance.post(
      `ajax/s3-upload-new-object/${bucketResource.value.id}/`,
      formData
    )
    emit('closeDialog')
    isUploading.value = false
    fileDialog.value = false
    uploadFile.value = []
    refreshResource()
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    formError.value = error
    formIsValid.value = false
    isUploading.value = false
  }
}
</script>
<style scoped></style>
