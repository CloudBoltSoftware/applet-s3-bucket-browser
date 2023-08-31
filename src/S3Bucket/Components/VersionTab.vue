<template>
  <VProgressCircular v-if="isLoading" indeterminate />
  <div v-else>
    <VBanner v-if="!hasVersions || !versionInfo">
      <template #prepend>
        <VIcon color="error" icon="mdi-alert" class="text-h3" />
      </template>
      <VBannerText class="d-inline-flex justify-space-between pa-0">
        <div class="mr-6">
          <p class="text-h5 mb-2">
            Bucket
            <span class="font-weight-medium">{{ bucketResource.name }}</span>
            doesn't have Bucket Versioning enabled
          </p>
          <p class="text-body-1">
            We recommend that you enable Bucket Versioning to help protect
            against unintentionally overwriting or deleting objects.
            <VBtn
              append-icon="mdi-information"
              href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html"
              target="_blank"
              variant="text"
              class="text-capitalize font-weight-regular text-body-1"
              >Learn more</VBtn
            >
          </p>
        </div>
        <VBtn
          title="Enable Bucket Versioning"
          color="primary"
          variant="flat"
          size="large"
          @click="enableVersioning"
          >Enable Bucket Versioning</VBtn
        >
      </VBannerText>
    </VBanner>
    <VBanner v-if="versionMessage">
      <template #prepend>
        <VIcon color="success" icon="mdi-check-circle" class="text-h3" />
      </template>
      <VBannerText class="text-h5 mt-1">
        {{ versionMessage }}
      </VBannerText>
    </VBanner>
    <VDataTable
      :headers="versionHeaders"
      :items="versions"
      :show-expand="false"
    >
      <template #[`item.name`]>
        {{ name }}
      </template>
      <template #[`item.item_type`]>
        {{ itemType }}
      </template>
      <template #[`item.last_modified`]="{ item }">
        {{ parseDate(item.raw) }}
      </template>
      <template #[`item.actions`]="{ item }">
        <ErrorIcon size="large" :error="formError" />
        <VBtnGroup>
          <VBtn
            icon="mdi-file-download"
            title="Download"
            :disabled="item.raw.is_delete_marker"
            @click="() => downloadFile(item.raw.download_url)"
          />
          <RestoreButton
            :item-key="item.raw.key"
            :path="item.raw.path"
            :version-id="item.raw.version_id"
          />
        </VBtnGroup>
      </template>
    </VDataTable>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, onUnmounted, ref } from 'vue'
import { convertObjectToFormData } from '../../helpers/axiosHelper'
import { useBuckets } from '../../helpers/useBuckets'
import ErrorIcon from './ErrorIcon.vue'
import RestoreButton from './RestoreButton.vue'

/**
 * @typedef {Object} Props
 * @property {Boolean} Props.hasVersions - Boolean if the item has versioning enabled
 * @property {String} Props.name - The name of the item
 * @property {Array} Props.versions - The versions of the S3 Bucket item
 * @property {String} Props.itemType - The type of the S3 Bucket item
 * @property {String} Props.itemKey - The key for the item
 * @property {String} Props.eTag - The etag (entity tag) of the item https://docs.aws.amazon.com/AmazonS3/latest/API/API_Object.html
 */
/** @type {Props} */

const props = defineProps({
  hasVersions: {
    type: Boolean,
    default: false
  },
  name: {
    type: String,
    default: ''
  },
  versions: {
    type: Array,
    default: () => []
  },
  itemType: {
    type: String,
    default: ''
  },
  itemKey: {
    type: String,
    default: ''
  },
  eTag: {
    type: String,
    default: ''
  }
})
const api = inject('api')
const { bucketResource } = useBuckets()
const isLoading = ref(false)
const formError = ref()
const versionInfo = ref(true)
const versionMessage = ref('')

const adjustedETag = computed(() =>
  props.eTag ? props.eTag.replace(/&quot;/g, '') : ''
)
const versionForm = computed(() => ({
  e_tag: encodeURIComponent(adjustedETag.value),
  key: encodeURIComponent(props.itemKey)
}))
const versionEnableForm = computed(() => ({
  bucket_name: encodeURIComponent(bucketResource.value.name)
}))
const parseDate = (entry) => {
  // Converting from database UTC values to local string
  const modifiedDate = new Date(entry.last_modified).toDateString()
  const modifiedTime = new Date(entry.last_modified).toLocaleTimeString()

  return `${modifiedDate}  ${modifiedTime}`
}

const versionHeaders = [
  { title: 'Name', align: 'start', key: 'name' },
  { title: 'Version ID', align: 'start', key: 'version_id' },
  { title: 'Type', align: 'start', key: 'item_type' },
  { title: 'Last Modified', align: 'start', key: 'last_modified' },
  { title: 'Size', align: 'start', key: 'size' },
  { title: 'Storage Class', align: 'start', key: 'storage_class' },
  { title: 'Actions', align: 'start', key: 'actions', sortable: false }
]

const fetchVersionInfo = async () => {
  try {
    const formData = convertObjectToFormData(versionForm.value)
    const response = await api.base.instance.post(
      `ajax/s3-get-versions/${bucketResource.value.id}/`,
      formData
    )
    isLoading.value = false
    versionInfo.value = response.data?.status
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    formError.value = `(${error.code}) ${error.name}: ${error.message}`
  }
}

const enableVersioning = async () => {
  try {
    const formData = convertObjectToFormData(versionEnableForm.value)
    const response = await api.base.instance.post(
      `ajax/s3-enable-versioning/${bucketResource.value.id}/`,
      formData
    )
    versionMessage.value = response.data.message
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    formError.value = error
  }
}

const downloadFile = (url) => {
  // TODO Better Decoding needed
  const adjustedUrl = url.replace(/&amp;/g, '&')
  window.open(adjustedUrl, '_blank')
}

onMounted(fetchVersionInfo)
onUnmounted((formError.value = ''))
</script>
<style scoped></style>
