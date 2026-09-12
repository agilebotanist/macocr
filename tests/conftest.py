import sys

import pytest


def pytest_collection_modifyitems(config, items):
    if sys.platform == "darwin":
        return
    skip_integration = pytest.mark.skip(reason="Vision framework is only available on macOS")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
