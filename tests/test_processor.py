from pathlib import Path

import pytest

from mandown import ProcessConfig, ProcessOptionMismatchError, Processor

SMALL_IMAGE = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01D\x00;"


def test_resize_requires_profile_xor_dims(tmp_path: Path) -> None:
    small_image_path = tmp_path / "test.gif"
    small_image_path.write_bytes(SMALL_IMAGE)

    # both target_size and output_profile
    with pytest.raises(ValueError) as _:
        bad_config = ProcessConfig(target_size=(100, 100), output_profile="kindle")

    # invalid output_profile
    with pytest.raises(KeyError) as _:
        bad_config = ProcessConfig(output_profile="invalid")

    # resize without target_size or output_profile
    bad_config = ProcessConfig()
    with pytest.raises(ProcessOptionMismatchError) as _:
        Processor(small_image_path, config=bad_config).process(["resize"])

    # target_size or output_profile without resize
    bad_config = ProcessConfig(target_size=(100, 100))
    with pytest.raises(ProcessOptionMismatchError) as _:
        Processor(small_image_path, config=bad_config).process(["split_double_pages"])

    # setting "none" anywhere should return immediately
    Processor(small_image_path, config=bad_config).process(
        ["resize", "rotate_double_pages", "split_double_pages", "none"]
    )
