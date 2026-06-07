"""Ensure the project root is on sys.path so pytest can import local packages."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
