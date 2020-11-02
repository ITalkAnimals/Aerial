# Aerial Self-Host

## Extensions

Extensions can be either in the form of a single file or in the form of a folder.

### Single File

Extensions must first import the `os` module, and then use `os.system` to install the additional requirements for the extension, if any.

### Folder

Folder extensions must have a `main.py` file inside, which is the entry point for the extension. It must also have a `requirements.txt` file, which will automatically be used to install requirements before adding the extension.