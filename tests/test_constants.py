"""Tests for the `constants` module."""

from scandeval import constants
from scandeval.data_models import Task


def test_all_objects_in_constants_are_constants() -> None:
    """Test that all objects in the `constants` module are constants."""
    for name in dir(constants):
        if name.startswith("__") or name in {"TaskGroup"}:
            continue
        assert name.isupper() and isinstance(
            getattr(constants, name), (Task, int, str, list, dict)
        )
