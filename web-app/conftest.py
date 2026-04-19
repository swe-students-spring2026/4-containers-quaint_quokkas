"""Pytest configuration for the web-app tests."""
# pylint: disable=wrong-import-position

import sys
import os

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
sys.path.insert(0, os.path.dirname(__file__))
