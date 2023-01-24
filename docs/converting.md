Mandown supports converting comics in the form of folders of images to CBZ, EPUB, and PDF.

## Basic usage

For Mandown-created comics, the process is extremely simple:

```
mandown convert epub /path/to/comic
```

A new file will be created in the same directory as the comic, with the same name as the comic, but with the appropriate extension. If you want to change the destination file, you can use the `--dest` flag:

```
mandown convert epub /path/to/comic -d /path/to/destination/
```

In the library, conversion is exposed through the `mandown.convert` command.

```python
import mandown

data = mandown.init_parse_comic("/path/to/comic")
mandown.convert(comic, "/path/to/comic", "epub")
```

The possible formats that Mandown accepts as conversion targets are available in the `mandown.ConvertFormats` enum.

The library also exposes an extra option: `remove_after`, which deletes the original directory after conversion completes, for convenience.

```python
import mandown

data = mandown.init_parse_comic("/path/to/comic")
mandown.convert(comic, "/path/to/comic", "epub", remove_after=True)
```

## Converting external comics

If you just want to convert one comic file to another (e.g., CBZ to EPUB), Mandown supports that natively too!

```
mandown convert epub path/to/comic.cbz
```

If you want to manage your old comic completely through Mandown (including getting updates), see below.

## Converting external comics (OLD)

If you have a folder of images that you want to convert to CBZ/EPUB/PDF, you can still use Mandown's converter, as long as you initialize the folder with a `md-metadata.json` file. This can be generated with the *interactive* `init-metadata` command:

```
mandown init-metadata
```

Mandown will try to match as many of your chapters and metadata as possible, and will prompt you for the rest. If you can find your comic on any of the supported sites, you can instead try to automatically fill in the information by providing a source URL in `init-metadata`.

```
mandown init-metadata --source-url https://example.com/comic --download-cover
```

After this point, it is usually safe to convert the comic.

```
mandown convert pdf /path/to/comic
```

### Library usage

An exactly equivalent action is not provided in the default API, but a minimal version is available as `mandown.init_parse_comic`. This function will parse a comic folder and return a `Comic` object, which can then be passed to `mandown.convert`.

```python
import mandown

comic = mandown.init_parse_comic("/path/to/comic")
mandown.convert(comic, "epub")
```

If you have a `Comic` object, you may be able to hack it together by passing it to `init_parse_comic` and then calling `convert` on the result. This is not recommended, as it may break in the future. But it *might* work, you know?

```python
import mandown

data = mandown.query("https://example.com/comic")
comic = mandown.init_parse_comic("/path/to/comic", donor_comic=data, download_cover=True)
mandown.convert(comic, "epub")
```

If you have a `md-metadata.json` file, you can also use `mandown.parse_comic` to parse the comic without initializing it.

```python
import mandown

comic = mandown.parse_comic("/path/to/comic")
mandown.convert(comic, "epub")
```
