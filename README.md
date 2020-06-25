# Firefox Bookmark Extractor

Firefox Bookmark Extractor can be used to extract urls from Firefox bookmarks. Scripts taps to Firefox's internal database and extracts data from required bookmark path.

## Installation

Firefox Bookmark Extractor can be installed from PyPI using `pip` or your package manager of choice:

```
pip install firefox-bookmark-extractor
```

## Usage

You can use Firefox Bookmark Extractor as CLI tool with `firefox-bookmark-extractor` command.

Example:

```console
$ firefox-bookmark-extractor -r "/home/me/.mozilla/firefox/ld84jfm4.default-release" "Bookmark Bar/Favourites/Songs"
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=xaazUgEKuVA
https://www.youtube.com/watch?v=TzXXHVhGXTQ
```

* First parameter is path to Firefox profile directory. This directory contains 'places.sqlite' database.
* Second parameter is path inside Firefox bookmark hierarchy excluding root directory.
* -r/--recursive parameter can be used to extract urls also from directories under the target path.