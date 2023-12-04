<template>
  <VContainer>
    <VRow>
      <VCol cols="6">
        <div class="mb-3">
          <div class="text-medium-emphasis">Owner</div>
          <p>{{ ownerName }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">AWS Region</div>
          <p>{{ bucketLocation }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Last Modified</div>
          <p>{{ lastModified }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Size</div>
          <p>{{ size }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Type</div>
          <p>{{ itemType }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Key</div>
          <p><CopyText :text-to-copy="itemKey" />{{ itemKey }}</p>
        </div>
      </VCol>
      <VCol cols="6">
        <div class="mb-3">
          <div class="text-medium-emphasis">S3 URI</div>
          <p><CopyText :text-to-copy="uri" />{{ uri }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Amazon Resource Name (ARN)</div>
          <p><CopyText :text-to-copy="arn" />{{ arn }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Entity Tag (ETag)</div>
          <p><CopyText :text-to-copy="eTag" />{{ eTag }}</p>
        </div>
        <div class="mb-3">
          <div class="text-medium-emphasis">Object URL</div>
          <p>
            <CopyText :text-to-copy="objectUrl" />
            <a
              target="_blank"
              :href="objectUrl"
              class="text-decoration-none text-primary"
              >{{ objectUrl }}</a
            >
          </p>
        </div>
      </VCol>
    </VRow>
  </VContainer>
</template>

<script setup>
import { computed } from 'vue'
import { useBuckets } from '../../helpers/useBuckets'
import CopyText from './CopyText.vue'
/**
 * @typedef {Object} Props
 * @property {String} Props.ownerName - The owner's name or id
 * @property {String} Props.lastModified  - The last modified date of the item
 * @property {String} Props.size - The size as a string with a label
 * @property {String} Props.itemType - The item file type
 * @property {String} Props.name - The name of the item
 * @property {String} Props.itemKey - The key for the item
 * @property {String} Props.uri - The aws s3 uri https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/services/s3/AmazonS3URI.html
 * @property {String} Props.arn - The arn (Amazon Resource Name) https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html
 * @property {String} Props.eTag - The etag (entity tag) of the item https://docs.aws.amazon.com/AmazonS3/latest/API/API_Object.html
 * @property {String} Props.objectUrl - The item object url https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-bucket-intro.html
 */
/** @type {Props} */

const props = defineProps({
  ownerName: {
    type: String,
    default: ''
  },
  lastModified: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: ''
  },
  itemType: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  itemKey: {
    type: String,
    default: ''
  },
  uri: {
    type: String,
    default: ''
  },
  arn: {
    type: String,
    default: ''
  },
  eTag: {
    type: String,
    default: ''
  },
  objectUrl: {
    type: String,
    default: ''
  }
})
const { bucketLocation } = useBuckets()
const eTag = computed(() =>
  props.eTag ? props.eTag.replace(/&quot;/g, '') : ''
)
</script>
<style scoped></style>
