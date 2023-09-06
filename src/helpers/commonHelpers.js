export const parseDate = (entry) => {
  // Converting from database UTC values to local string
  const modifiedDate = new Date(entry.last_modified).toDateString()
  const modifiedTime = new Date(entry.last_modified).toLocaleTimeString('en-US')

  return `${modifiedDate}  ${modifiedTime}`
}

export const findLastActiveVersion = (versions) =>
  versions.find((version) => !version.is_delete_marker)

export const downloadFile = (url) => {
  const adjustedUrl = url.replace(/&amp;/g, '&')
  window.open(adjustedUrl, '_blank')
}
