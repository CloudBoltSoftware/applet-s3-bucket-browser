export const parseDate = (entry) => {
  // Converting from database UTC values to local string
  const modifiedDate = new Date(entry.last_modified).toDateString()
  const modifiedTime = new Date(entry.last_modified).toLocaleTimeString('en-US')

  return `${modifiedDate}  ${modifiedTime}`
}

export const findLastActiveVersion = (versions) =>
  versions.find((version) => version.is_latest)

export const downloadFile = (url) => {
  const adjustedUrl = url.replace(/&amp;/g, '&')
  window.open(adjustedUrl, '_blank')
}

// Handles change on Vuetify@v3.3.18 which moved the props item.raw to internalItem
export const rawItemData = (row) => row?.item?.raw ?? row.internalItem.raw
