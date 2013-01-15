from distutils.core import setup
import py2exe
 
includes = []
excludes = []
packages = []
dll_excludes = []
 
setup(
    options = {"py2exe": {
                          "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          "bundle_files": 3,
                          "custom_boot_script": '',
                         }
              },
    console=['server.py']
)