<template>
  <VContainer>
    <VRow>
      <VCol cols="6">
        <div class="mb-3">
          <div class="text-medium-emphasis">Owner</div>
          <p>{{ owner }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">AWS Region</div>
          <p>{{ bucketLocation }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Last Modified</div>
          <p>{{ new Date(sourceItem.last_modified).toString() }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Size</div>
          <p>{{ file_size }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Type</div>
          <p>{{ sourceItem.item_type }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Key</div>
          <p><CopyText :text-to-copy="sourceItem.name" />{{ sourceItem.name }}</p>
        </div>
        <div id="kfp-parent" class="d-none">
          <p>{{ sourceItem.key }}</p>
        </div>
      </VCol>
      <VCol cols="6">
        <div class="mb-3">
          <div class="text-medium-emphasis">S3 URI</div>
          <p><CopyText :text-to-copy="sourceItem.s3_uri" />{{ sourceItem.s3_uri }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Amazon Resource Name (ARN)</div>
          <p><CopyText :text-to-copy="sourceItem.arn" />{{ sourceItem.arn }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Entity Tag (ETag)</div>
          <p><CopyText :text-to-copy="eTag" />{{ eTag }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Object URL</div>
          <p><CopyText :text-to-copy="object_url" /><a
            target="_blank"
            :href="object_url"
            class="text-decoration-none text-primary"
            >{{ object_url }}</a
          ></p>
        </div>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script setup>
import { computed } from 'vue';
import { useBuckets } from '../../helpers/useBuckets';
import CopyText from './CopyText.vue';
/**
 * @typedef {Object} sourceItem
 * @property {String} owner_name
 * @property {String} last_modified
 * @property {String} size
 * @property {String} item_type
 * @property {String} name
 * @property {String} key
 * @property {String} keyFilePath
 * @property {String} s3_uri
 * @property {String} arn
 * @property {String} e_tag
 * @property {String} object_url
 * @property {Object} latest_version // 
 * @property {String} version_id // 
 * @property {Array} versions //
 */

/**
 * @typedef {Object} Props
 * @property {Object} Props.sourceItem - The selected S3 Bucket item
 * @property {Boolean} Props.hasVersions - Boolean if the item has versioning
 */
/** @type {Props} */

const props = defineProps({
  sourceItem: {
    type: Object,
    default: () => {}
  },
  hasVersions: {
    type: Boolean,
    default: false
  },
})

const { bucketLocation } = useBuckets()
const existVersion = computed(() => props.sourceItem?.versions.find((version) => version.is_delete_marker === false))
const eTag = computed(() =>
  props.hasVersions ? existVersion.value.e_tag.replace(/&quot;/g, '') : props.sourceItem?.e_tag ? props.sourceItem.e_tag.replace(/&quot;/g, '') : ''
)
const object_url = computed(() => 
  props.hasVersions && props.sourceItem.is_delete_marker ? `${existVersion.value.object_url}?versionId=${existVersion.value.version_id}` : props.sourceItem.object_url
)
const file_size = computed(() => 
  props.hasVersions ? existVersion.value.size : props.sourceItem.size
)
const owner = computed(() => 
  props.hasVersions ? existVersion.value.owner_name : props.sourceItem.owner_name
)
</script>
<style scoped></style>
