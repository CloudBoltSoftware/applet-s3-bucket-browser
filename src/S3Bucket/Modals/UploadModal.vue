<template>
  <VDialog v-model="uploadDialog" width="1024">
    <template #activator="{ props: uploadProps }">
      <VBtn
        v-bind="uploadProps"
        icon="mdi-file-upload"
        title="Upload New File or Folder"
        size="x-large"
      />
    </template>
    <VCard class="pa-3">
      <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
        <div>
          Upload file or folder to
          <span class="font-italic">{{
            bucketPath ? bucketPath : 'Root folder'
          }}</span>
        </div>
        <VBtn
          icon="mdi-close"
          title="Close this dialog"
          data-dismiss="modal"
          variant="text"
          @click="uploadDialog = false"
        />
      </VCardTitle>
      <VCardActions class="d-flex justify-center ma-2">
        <FileUpload @closeDialog="uploadDialog = false" />
        <FolderUpload @closeDialog="uploadDialog = false" />
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<script setup>
import { ref } from 'vue';
import { useBuckets } from '../../helpers/useBuckets';
import FileUpload from '../Components/FileUpload.vue';
import FolderUpload from '../Components/FolderUpload.vue';

const { bucketPath } = useBuckets()
const uploadDialog = ref(false)
</script>
<style scoped></style>
