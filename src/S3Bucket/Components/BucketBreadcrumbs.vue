<template>
  <VBreadcrumbs class="pl-0 my-1">
    <VBreadcrumbsItem v-for="(entry, idx) in breadcrumbs" :key="entry.title">
      <div
        v-if="entry.disabled"
        class="text-grey-darken-3 text-none text-h6 pb-1"
      >
        {{ entry.title }}
      </div>
      <VBtn
        v-else
        class="text-blue-darken-3 text-none text-h6 px-0 pt-0 pb-1"
        variant="plain"
        density="default"
        @click="fetchSelection(entry.path)"
        >{{ entry.title }}</VBtn
      >
      <VBreadcrumbsDivider
        v-if="breadcrumbs.length - 1 > idx && breadcrumbs.length > 1"
        class="pr-0"
      >
        <VIcon icon="mdi-slash-forward" />
      </VBreadcrumbsDivider>
    </VBreadcrumbsItem>
  </VBreadcrumbs>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useBuckets } from '../../helpers/useBuckets'

const api = inject('api')
const { bucketResource, bucketState, fetchSelection } = useBuckets(api)
const breadcrumbs = computed(() => {
  let crumbsArray = [
    {
      title: bucketResource.value.name,
      disabled: false,
      path: {
        resource_id: bucketResource.value.id,
        name: bucketResource.value.name,
        path: ''
      }
    }
  ]
  if (bucketState.value.path_dirs.length > 0) {
    for (let entry of bucketState.value.path_dirs) {
      if (entry.name) {
        crumbsArray.push({
          title: entry.name,
          disabled: false,
          path: {
            resource_id: bucketResource.value.id,
            name: entry.name,
            path: entry.path
          }
        })
      }
    }
  }
  // Disable the last link
  const lastLink = crumbsArray[crumbsArray.length - 1]
  lastLink.disabled = true
  return crumbsArray
})
</script>
<style scoped></style>
