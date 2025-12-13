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

    # Get Python version info
    version_info = sys.version_info
    python_dll_name = f'python{version_info.major}{version_info.minor}.dll'

    # Possible locations for the Python DLL
    possible_paths = []

    # 1. PyInstaller's _MEIPASS directory (frozen app) - highest priority
    if hasattr(sys, '_MEIPASS'):
        possible_paths.append(os.path.join(sys._MEIPASS, python_dll_name))

    # 2. Same directory as the executable
    if hasattr(sys, 'executable'):
        exe_dir = os.path.dirname(sys.executable)
        possible_paths.append(os.path.join(exe_dir, python_dll_name))
        # Also check _internal folder (PyInstaller onedir mode)
        possible_paths.append(os.path.join(exe_dir, '_internal', python_dll_name))

    # 3. Python installation directory (fallback for development)
    if sys.prefix:
        possible_paths.append(os.path.join(sys.prefix, python_dll_name))
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        possible_paths.append(os.path.join(sys.base_prefix, python_dll_name))

    # Find the first existing DLL
    python_dll_path = None
    for path in possible_paths:
        if os.path.exists(path):
            python_dll_path = path
            break

    if python_dll_path:
        # Set environment variable BEFORE any pythonnet import
        os.environ['PYTHONNET_PYDLL'] = python_dll_path
        print(f'[pythonnet-hook] Set PYTHONNET_PYDLL={python_dll_path}')

        # Also try to configure pythonnet runtime if possible
        try:
            from pythonnet import set_runtime
            set_runtime("netfx")  # Use .NET Framework runtime
            print('[pythonnet-hook] Set pythonnet runtime to netfx')
        except ImportError:
            pass  # pythonnet not yet available, that's OK
        except Exception as e:
            print(f'[pythonnet-hook] Warning: set_runtime failed: {e}')
    else:
        print(f'[pythonnet-hook] WARNING: Could not find {python_dll_name}')
        print(f'[pythonnet-hook] Searched paths: {possible_paths}')
        print(f'[pythonnet-hook] sys._MEIPASS: {getattr(sys, "_MEIPASS", "not set")}')
        print(f'[pythonnet-hook] sys.executable: {sys.executable}')


# Run setup immediately when this hook is loaded
_setup_pythonnet()
