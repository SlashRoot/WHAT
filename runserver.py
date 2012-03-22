#!/usr/bin/env python
from django.core.management import execute_manager

import settings.common as settings

if __name__ == "__main__":
    execute_manager(settings)
