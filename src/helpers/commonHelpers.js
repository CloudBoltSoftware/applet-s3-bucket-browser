export const parseSize = (size) => {
  // Formats the size from numerical bytes to either bytes (B), Kilobytes (KB), or Megabytes (MB)
  if (!size) {
    return
  } else if (size < 1024) {
    // less than 1 KB
    return `${size} B`
  } else if (size < 1024 * 1024) {
    // less than 1 MB
    return `${Math.round((size * 10) / 1024) / 10} KB`
  } else {
    // size is 1 MB or more
    return `${Math.round((size * 10) / (1024 * 1024)) / 10} MB`
  }
}

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
