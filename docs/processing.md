Unlike other functions of Mandown, this one does not rely on any Mandown-specific features, so can be indiscriminately used on any folder containing images.

## Basic usage

The following possible arguments passed to the `process` command will be run **in sequence**.

- `rotate_double_pages`
- `split_double_pages`
- `none`: if this is present at any point in the sequence, the entire sequence will be ignored
- `trim_borders`
- `resize`

For example, the following command will rotate double pages and then trim their borders:

```
mandown process rotate_double_pages trim_borders /path/to/comic
```

In the library, this is done through the `mandown.process` API, which accepts a Path and a list of operations. The following code will do the same thing:

```python
import mandown

mandown.process("/path/to/comic", ["rotate_double_pages", "trim_borders"])
```

A full list of operations is available in the `mandown.ProcessOps` enum.

## Resizing images

The `resize` argument is used to fit images to a specific resolution.

It has some special options that must be passed as flags: Either `--target-size` or `--profile` must be specified, but not both.

### To a target size

`--target-size`: The target size of the images, in pixels. Specified as (width, height)

For example, to resize all images in the target path to 1000x1000:

```
mandown process resize --target-size 1000 1000 /path/to/comic
```

In the library, these are passed via a `ProcessConfig` object:

```python
import mandown
from mandown import ProcessConfig

config = ProcessConfig(target_size=(1000, 1000))
mandown.process("/path/to/comic", ["resize"], config)
```

### To a device profile

`--profile`: The name of the device profile to use. See [Device profiles](#device-profiles) for more information.

For example, to resize all images in the target path to fit the Kobo Aura:

```
mandown process resize --profile aura /path/to/comic
```

In the library, these are also passed via `ProcessConfig`:

```python
import mandown
from mandown import ProcessConfig

config = ProcessConfig(profile="aura")
mandown.process("/path/to/comic", ["resize"], config)
```


## Device profiles

Mandown comes with a number of device profiles that can be used to resize images to fit a specific device.

A full list can be found by calling `mandown --list-profiles` in the CLI or `mandown.all_profiles` in the library. Alternatively, they may be shown by your IDE as autocomplete suggestions.
