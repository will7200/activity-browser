import importlib
import os
import importlib.resources
from pathlib import Path
from typing import Iterable, Tuple

import requests
from bw_processing import safe_filename
from PySide2 import QtWidgets

import activity_browser
from activity_browser.mod import bw2data as bd

from .settings import ab_settings

STATIC_DIR = importlib.resources.files(activity_browser) / "static"


def get_package_dir() -> Path:
    """Return activity_browser package path"""
    return Path(importlib.util.find_spec("activity_browser").origin).parent


def read_file_text(file_dir: str) -> str:
    if not file_dir:
        raise ValueError("File path passed is empty")
    file = open(file_dir, mode="r", encoding="UTF-8")
    if not file:
        raise ValueError("File does not exist in the passed path:", file_dir)
    text = file.read()
    file.close()
    return text


def savefilepath(
    default_file_name: str = "AB_file", file_filter: str = "All Files (*.*)"
):
    """A central function to get a safe file path."""
    safe_name = safe_filename(default_file_name, add_hash=False)
    filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
        parent=None,
        caption="Choose location for saving",
        dir=os.path.join(ab_settings.data_dir, safe_name),
        filter=file_filter,
    )
    return filepath


def safe_link_fetch(url: str) -> Tuple[object, object]:
    """
    Get a web-page or file from the internet or the error of getting the link.

    Parameters
    ----------
    url: a link

    Returns
    -------
    object: error if any, otherwise None
    object: response if no error, otherwise None
    """
    try:
        response = requests.get(url)  # retrieve the page from the URL
        response.raise_for_status()
    except Exception as error:
        return (None, error)

    return (response, None)


def sort_semantic_versions(versions: Iterable, highest_to_lowest: bool = True) -> list:
    """Return a sorted (default highest to lowest) list of semantic versions.

    Sorts based on the semantic versioning system.
    """
    return list(
        sorted(
            versions,
            key=lambda x: tuple(map(int, x.split("."))),
            reverse=highest_to_lowest,
        )
    )
