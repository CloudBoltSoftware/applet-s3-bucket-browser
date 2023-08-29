<template>
  <VDialog v-model="overviewDialog" width="1024">
    <template #activator="{ props: overviewProps }">
      <VBtn v-bind="overviewProps" icon="mdi-information" title="Details" />
    </template>
    <VCard class="pa-3">
      <VCardTitle class="d-inline-flex justify-space-between pb-0">
        <VTabs
          v-model="tab"
          slider-color="black"
          height="50px"
          selected-class="bg-primary text-white"
        >
          <VTab class="active tab-btn" value="overview" size="x-large"
            >Overview</VTab
          >
          <VTab
            v-if="hasVersionMode"
            class="tab-btn"
            value="versions"
            size="x-large"
            >Versions</VTab
          >
        </VTabs>
        <VBtn
          icon="mdi-close"
          title="Close this dialog"
          variant="text"
          @click="overviewDialog = false"
        />
      </VCardTitle>
      <VCardText class="pt-0">
        <VWindow v-model="tab">
          <VWindowItem value="overview">
            <OverviewTab :source-item="sourceItem" />
          </VWindowItem>
          <VWindowItem value="versions">
            <VersionTab :source-item="sourceItem" />
          </VWindowItem>
        </VWindow>
      </VCardText>
      <VCardActions class="d-flex justify-end px-3 mb-1">
        <VBtn
          color="primary"
          variant="flat"
          size="large"
          class="px-4"
          @click="overviewDialog = false"
          >OK</VBtn
        >
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<script setup>
import { ref } from 'vue';
import OverviewTab from '../Components/OverviewTab.vue';
import VersionTab from '../Components/VersionTab.vue';

/**
 * @typedef {Object} Props
 * @property {Object} Props.sourceItem - The selected S3 Bucket item
 */
/** @type {Props} */

defineProps({
  sourceItem: {
    type: Object,
    default: () => {}
  }
})

const tab = ref(null)
const overviewDialog = ref(false)
// TODO CMP-127 - Re-enable once Version updates are fixed.
const hasVersionMode = ref(false)
</script>
<style scoped></style>
