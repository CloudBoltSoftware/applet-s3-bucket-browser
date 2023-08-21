<template>
  <VDialog v-model="uploadDialog" width="1024">
    <template #activator="{ props: uploadProps }" >
      <VBtn v-bind="uploadProps" icon="mdi-file-upload" title="Upload New File" size="x-large"/>
    </template>
    <VCard class="pa-3">
      <VCardTitle class="w-100 d-inline-flex justify-space-between text-h5">
        <div>
          Upload file or folder to <span class="font-italic">{{ path ? path : 'Root folder'}}</span>
        </div>
        <VBtn icon="mdi-close" title="Close this dialog" data-dismiss="modal" variant="text" @click="uploadDialog = false"/>
      </VCardTitle>
      <VCardActions class="d-flex justify-center ma-2">
        <FileUpload @update:closeDialog="uploadDialog = false" @update:refresh="emit('update:refresh')" />
        <FolderUpload @update:closeDialog="uploadDialog = false" @update:refresh="emit('update:refresh')" />
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<script setup>
import { inject, ref } from "vue";
import FileUpload from "../Components/FileUpload.vue";
import FolderUpload from "../Components/FolderUpload.vue";

const path = inject('path')
const uploadDialog = ref(false)
const emit = defineEmits(["update:refresh"]);
</script>
<style scoped></style>
