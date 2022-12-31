Mandown's primary function is to download comics.

## Basic usage

The easiest way to get started is to download all the chapters of a comic from a supported site to the current folder:

```
mandown get https://example.com/comic
```

This will create a new folder in the current directory, with the name of the comic, and download all the chapters to it. If you want to change the destination folder, you can append it at the end:

```
mandown get https://example.com/comic /path/to/destination/
```

You can also specify a range of chapters to download with the `--start` and `--end` flags, which are inclusive and one-indexed. The following command will download the first through tenth chapters:

```
mandown get https://example.com/comic --start 1 --end 10
```

You can also configure the number of threads your system will use to download chapters with the `--threads` flag. The default is 4, but you can increase or decrease it as needed:

```
mandown get https://example.com/comic --threads 8
```

## Combining multiple functions

Mandown also supports combining multiple functions into a single command. For example, you can download a comic and convert it to CBZ in one command:

```
mandown get https://example.com/comic --convert cbz
```

You can also apply image processing prior to conversion:

```
mandown get https://example.com/comic --convert cbz -p rotate_double_pages
```

Lastly, if all you want is to download and convert a comic, you can apply the `--remove-after` flag to clean up afterward:

```
mandown get https://example.com/comic --convert epub --remove-after
```

### Library usage

Mandown's downloader is exposed through the `mandown.download` command.

```python
import mandown

mandown.download("https://example.com/comic", "/path/to/destination/")
```

The same CLI flags can also be applied:

```python
import mandown

mandown.download("https://example.com/comic", "/path/to/destination", start=1, end=10, threads=8)
```

In addition, the `only_download_missing` flag, which is on by default to prevent redownloading existing images, can be turned off to force a refresh each time.

```python
import mandown

mandown.download("https://example.com/comic", "/path/to/destination", only_download_missing=False)
```
