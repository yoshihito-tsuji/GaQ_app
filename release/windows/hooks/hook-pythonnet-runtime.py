# -*- coding: utf-8 -*-
"""
PyInstaller runtime hook for pythonnet
pythonnet 3.x requires PYTHONNET_PYDLL environment variable to be set
before importing clr module.

This hook sets the environment variable to point to the bundled python DLL.
"""

import os
import sys


def _setup_pythonnet():
    """Setup PYTHONNET_PYDLL environment variable for pythonnet 3.x"""

    # Skip if already set
    if os.environ.get('PYTHONNET_PYDLL'):
        return

    # Get Python version info
    version_info = sys.version_info
    python_dll_name = f'python{version_info.major}{version_info.minor}.dll'

    # Possible locations for the Python DLL
    possible_paths = []

    # 1. PyInstaller's _MEIPASS directory (frozen app)
    if hasattr(sys, '_MEIPASS'):
        possible_paths.append(os.path.join(sys._MEIPASS, python_dll_name))

    # 2. Same directory as the executable
    if hasattr(sys, 'executable'):
        exe_dir = os.path.dirname(sys.executable)
        possible_paths.append(os.path.join(exe_dir, python_dll_name))
        # Also check _internal folder
        possible_paths.append(os.path.join(exe_dir, '_internal', python_dll_name))

    # 3. Python installation directory (fallback)
    if sys.prefix:
        possible_paths.append(os.path.join(sys.prefix, python_dll_name))

    # Find the first existing DLL
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['PYTHONNET_PYDLL'] = path
            print(f'[pythonnet-hook] Set PYTHONNET_PYDLL={path}')
            return

    # If no DLL found, log warning but don't fail
    print(f'[pythonnet-hook] WARNING: Could not find {python_dll_name}')
    print(f'[pythonnet-hook] Searched paths: {possible_paths}')


# Run setup immediately when this hook is loaded
_setup_pythonnet()
