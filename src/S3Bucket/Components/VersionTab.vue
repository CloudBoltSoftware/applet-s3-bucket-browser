<template>
  <VProgressCircular v-if="isLoading" indeterminate />
  <div v-else>
    <VBanner v-if="!bucketVersioningEnabled">
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
        >
          <ErrorIcon size="small" :error="versioningError" />
          Enable Bucket Versioning
        </VBtn>
      </VBannerText>
    </VBanner>
    <VBanner v-if="versionMessage">
      <template #prepend>
        <VIcon color="success" icon="mdi-check-circle" class="text-h2 mt-1" />
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
      <template #[`item.last_modified`]="row">
        {{ parseDate(rawItemData(row)) }}
      </template>
      <template #[`item.actions`]="row">
        <ErrorIcon size="large" :error="formError" />
        <VBtnGroup variant="text">
          <VBtn
            icon="mdi-file-download"
            title="Download"
            :disabled="rawItemData(row).is_delete_marker"
            @click="() => downloadFile(rawItemData(row).download_url)"
          />
          <RestoreButton
            :item-key="name"
            :version-id="rawItemData(row).version_id"
            :is-delete-marker="rawItemData(row).is_delete_marker"
          />
        </VBtnGroup>
      </template>
    </VDataTable>
  </div>
</template>

<script>
import {
  downloadFile,
  parseDate,
  rawItemData
} from '../../helpers/commonHelpers'

export default {
  rawItemData,
  downloadFile,
  parseDate
}
</script>
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
  }
})
const api = inject('api')
const { bucketResource, refreshResource } = useBuckets(api)
const isLoading = ref(false)
const formError = ref()
const versioningError = ref()
const versionStatus = ref(false)
const versionMessage = ref('')
const bucketVersioningEnabled = computed(() =>
  props.hasVersions ? props.hasVersions : versionStatus.value
)

const versionForm = computed(() => ({
  resource_id: bucketResource.value.id,
  key: encodeURIComponent(props.itemKey)
}))
const versionEnableForm = computed(() => ({
  resource_id: bucketResource.value.id
}))

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
    const response = await api.v3.cmp.inboundWebHooks.runPost(
      's3_bucket_browser/get_versions',
      formData
    )
    isLoading.value = false
    versionStatus.value = response?.status
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    versioningError.value = error
  }
}

const enableVersioning = async () => {
  try {
    const formData = convertObjectToFormData(versionEnableForm.value)
    const response = await api.v3.cmp.inboundWebHooks.runPost(
      's3_bucket_browser/enable_versioning',
      formData
    )
    versionMessage.value = response.message
    versionStatus.value = response.status
    refreshResource()
  } catch (error) {
    // When using API calls, it's a good idea to catch errors and meaningfully display them.
    versioningError.value = error
  }
}

onMounted(fetchVersionInfo)
onUnmounted((formError.value = ''))
</script>
<style scoped></style>
