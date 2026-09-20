# Link Preview

A plugin for [Zim Desktop Wiki](https://zim-wiki.org/) that shows a small preview when the mouse pointer is placed over a link.

The preview appears after a short delay and allows you to quickly see the beginning of the linked note without opening it.

## Features

### Internal Zim links

For a link to another page in the current notebook, the popup shows a configurable part of the target note.

The preview can be configured with:

* **First non-empty preview line** — the first non-empty line to display.
* **Number of preview lines** — how many lines to show.
* **Maximum characters per line** — lines longer than this value are truncated and followed by `...`.

The preview uses the same font as the ordinary Zim note text.

Empty lines are not counted when determining the first and subsequent preview lines.

### External links

The plugin recognizes several types of links:

* `http://` and `https://` — displayed as **Internet link**.
* `zotero://` — displayed as **Zotero link**.
* Zim interwiki links — displayed using the configured notebook name.

No external content is loaded.

## Configuration

The plugin provides the following settings:

| Setting                      | Default | Description                                     |
| ---------------------------- | ------: | ----------------------------------------------- |
| First non-empty preview line |       1 | First non-empty line included in the preview    |
| Number of preview lines      |       5 | Number of lines displayed                       |
| Maximum characters per line  |     100 | Maximum number of characters shown on each line |

## How it works

Move the mouse pointer over a link and wait briefly. If the pointer remains over the link, the preview popup appears.

The popup disappears when the pointer leaves the link.

For internal links, the target page is read through Zim's normal page/parsetree and text-buffer mechanisms, so the preview displays text after Zim markup has been processed rather than raw contents of the `.txt` file.

## Requirements

* Zim Desktop Wiki
* Python 3
* GTK 3 / PyGObject

The plugin is currently developed and tested with **Zim 0.77.2**.

## Installation

Copy the `link_preview` directory into the Zim user plugins directory:

```text
~/.local/share/zim/plugins/
```

The resulting directory should be:

```text
~/.local/share/zim/plugins/link_preview/
```

Restart Zim and enable **Link Preview** in:

**Edit → Preferences → Plugins**

## License

MIT
