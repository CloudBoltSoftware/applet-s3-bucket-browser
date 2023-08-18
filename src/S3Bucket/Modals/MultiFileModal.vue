<template>
  <VDialog v-model="fileDialog" width="1024" @update:model-value="(val) => !val && onCancel()" >
    <VCard class="pa-3">
      <VForm @submit.prevent="multiFileUploadModal" @update:model-value="(val) => formIsValid = val">
        <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
          <div>Upload {{uploadFile.length > 1 ? uploadFile.length : ''}} file(s) to <span class="font-italic">{{dropFilesForm.path ? dropFilesForm.path : 'Root folder'}}</span></div>
          <VBtn icon="mdi-close" title="Close" data-dismiss="modal" variant="text" @click="onCancel" />
        </VCardTitle>
        <VCardText>
          <VFileInput v-model="uploadFile" multiple disabled label="Selected Files" class="showInput"/>
        </VCardText>
        <VCardActions class="d-flex justify-end px-3">
          <VTooltip location="start" :text="formError" >
            <template #activator="{ props: activatorProps }">
              <VIcon v-if="formError" v-bind="activatorProps" color="error" size="large" icon="mdi-alert-circle" class="mt-1"/>
            </template>
          </VTooltip>
          <VBtn prepend-icon="mdi-close" variant="flat" size="large" class="px-4 mx-2" @click="onCancel" >Cancel</VBtn>
          <VBtn :loading="isUploading" prepend-icon="mdi-file-upload" :disabled="!formIsValid" variant="flat" color="primary" size="large" class="px-4" type=submit >Upload to S3
            <template #loader>Uploading...</template>
          </VBtn>
        </VCardActions>
      </VForm>
    </VCard>
  </VDialog>
</template>

<script setup>
import { computed, inject, onUpdated, ref, toValue } from "vue";
import { convertObjectToMultiFormData } from '../../helpers/axiosHelper';
/**
 * @typedef {object} Props
 * @property {Boolean} Props.dropModal - Boolean for enabling the file-drop modal
 * @property {Array} Props.dropFiles - Array of files from the file-drop
 * @property {Object} Props.dropFilesForm - Form for the file-drop upload
 * 
 */
/** @type {Props} */
const props = defineProps({
  dropModal: {
    type: Boolean,
    default: false
  },
  dropFiles: {
    type: Array,
    default: () => []
  },
  dropFilesForm: {
    type: Object,
    default: () => {}
  }
});
const api = inject('api')
const resource = toValue(inject('resource'))
const emit = defineEmits(["update:submitted", "update:clear"]);
const isUploading = ref(false)
const uploadFile = ref([])
const formIsValid = ref(false)
const formError = ref()
const fileDialog = ref(false)
const isMultiFileDrop = computed(() => props.dropFiles && props.dropFiles.length > 0)

const onCancel = () => {
  emit("update:clear")
  fileDialog.value = false
  formError.value = ''
  uploadFile.value = []
}

onUpdated(() => {
  if (isMultiFileDrop.value && props.dropFilesForm && props.dropModal) {
    fileDialog.value = true
    uploadFile.value = props.dropFiles
  }
})

async function multiFileUploadModal() {
  try {
    isUploading.value = true
    for (const file of props.dropFiles) {
      const formData = convertObjectToMultiFormData(props.dropFilesForm, [file], 'file')
      // Because this function is `async`, we can use `await` to wait for the API call to finish.
      // Alternatively, we could use `.then()` and `.catch()` to handle the response.
      // https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises
      await api.base.instance.post(`http://localhost:8001/ajax/s3-upload-new-object/${resource.id}/`,  formData)
    }
    emit("update:submitted")
    emit("update:clear")
    isUploading.value = false
    fileDialog.value = false
    uploadFile.value = []
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    formError.value = `(${error.code}) ${error.name}: ${error.message}`
    formIsValid.value = false
    isUploading.value = false
  }
}
</script>
<style scoped></style>
