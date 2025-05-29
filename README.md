EPC Viewer & Inspector (WIP)
This is a test tool for analyzing and reverse engineering .epc files used in
Doctor Who: The Adventure Games, a 3D adventure game series developed by Sumo Digital and published by the BBC.

🔍 What it does (for now)
Opens .epc files through a simple UI

Lists all embedded ASCII strings (like filenames and paths)

Displays offsets and surrounding hex for each string

Detects and lists index records pointing to resource data

Allows exporting binary data blocks (e.g. models, textures)*

*Note: Some models or other resources may not export correctly due to incomplete format understanding. Just a heads-up!

⚠️ This tool is still in development
Please do not expect full functionality yet.
It’s experimental and being built through ongoing reverse engineering of the EPC file format.
Many assumptions are still being tested and verified.

🛠️ Vision for the Future
This tool aims to become a full-featured modding utility for Doctor Who: The Adventure Games,
allowing fans to inspect, extract, and eventually modify or inject new content into the game.

Future plans include:

Full automatic extraction of all assets

Recognition of embedded file formats (.mb, .tga, .scene, etc.)

Optional model/texture previewing

Repacking and patching support for modding workflows

This is a fan-made utility provided for educational and archival purposes.
All rights to Doctor Who and related assets belong to the BBC.
