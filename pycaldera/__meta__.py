# `name` is the name of the package as used for `pip install package`
name = "pycaldera"
# `path` is the name of the package for `import package`
path = name.lower().replace("-", "_").replace(" ", "_")
# Your version number should follow https://python.org/dev/peps/pep-0440 and
# https://semver.org
version = "0.1.dev0"
author = "Mark Watson"
author_email = "markwatson@cantab.net"
description = "Unofficial Python client for Caldera Spa API"  # One-liner
url = "https://github.com/mwatson2/pycaldera"  # Add your GitHub repo URL
license = "MIT"  # See https://choosealicense.com
