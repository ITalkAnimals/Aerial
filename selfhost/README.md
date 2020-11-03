# Aerial Self-Host

## Running

1. Download this folder.
2. Run the `main.py` file inside of the folder. Requirements will be automatically installed.

## Extensions

Extensions can be either in the form of a single file or in the form of a folder.

### Simple / Single File

Single file extensions are quite basic. These are recommended for adding basic functionality to the bot with no configuration.

Single file extensions **must** have the following:
- One or more "Cogs" - subclassed from `fortnitepy.ext.commands.Cog`.
- A `setup_extension` function that takes `client` and does `client.add_cog(Cog)` for every "Cog".

Single file extensions **must not** have the following:
- Any `print()` statements - instead use `logging.getLogger()` and `logger.info()`.
- Any module that isn't system or `fortnitepy` or `yaml` - for compatibility between systems.
- Any external files.

### Advanced / Folder (Recommended)

Folder extensions are more advanced, and, as the name suggests, have a dedicated folder inside the `extensions` folder. These are expected to be better organized.

Folder extensions **must** have the following:
- One or more "Cogs" - subclassed from `fortnitepy.ext.commands.Cog`, typically in separate files.
- A `main.py` file with a `setup_extension` function that takes `client` and does `client.add_cog(Cog)` for every "Cog".

Folder extensions **can** have any module from `pip`, but they must be inside a `requirements.txt` file. The modules will be automatically installed and kept up-to-date.

Folder extensions **must not** have any `print()` statements - instead use `logging.getLogger()` and `logger.info()`.

For an example of a folder extension, look at the built in `core` and `socket` extensions.
