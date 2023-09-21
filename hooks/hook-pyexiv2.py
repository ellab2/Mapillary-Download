import sysconfig
from PyInstaller.utils.hooks import collect_data_files

# Collect the required binary files
binaries = []

# Get the system Python library path
python_lib_path  = './mly_venv/lib/python3.10/site-packages/'
libexiv2_path = f"{python_lib_path}/pyexiv2/lib/libexiv2.so"
exiv2api_path = f"{python_lib_path}/pyexiv2/lib/py3.10-linux/exiv2api.so"

# Append the binary files and their destination paths to the binaries list
binaries.append((libexiv2_path, "pyexiv2/lib"))
binaries.append((exiv2api_path, "pyexiv2/lib/py3.10-linux"))

# Collect any data files if needed
datas = collect_data_files('pyexiv2')
