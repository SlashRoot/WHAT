import sys
from path import path

PROJECT_ROOT = path(__file__).abspath().dirname().dirname()

VIRTUALENV = path(sys.executable).abspath().dirname().dirname()

def set_path():
    sys.path.append(PROJECT_ROOT)
