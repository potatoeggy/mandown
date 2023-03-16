import os
import pytest


skip_in_ci = pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true", reason="Do not run network tests in CI"
)
