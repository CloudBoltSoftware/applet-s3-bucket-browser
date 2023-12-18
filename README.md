# CB Applet

This is a forked version of the standard CB Applet. Please refer to the [README](https://github.com/CloudBoltSoftware/cb-applet) on the main branch of the CloudBoltSoftware/cb-applet repo.

# Inbound Web Hooks

This applet has inbound web hook (iwh) dependencies listed as an array under `met_inbound_web_hook_dependencies` in the `package.json`. The corresponding zip files should be placed in `xui/additional_files`. Unzipped copies of the files are present in `xui/additional_files_unzipped` to show the code and track changes, but the zipped versions will be what the applet uses.
