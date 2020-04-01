# exit on error and do long report
set -ex

# location of this script
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# which version of PDFium to use
version=`cat $dir/pdfium_version.txt`

git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=$PATH:/depot_tools

gclient config --name pdfium --unmanaged https://pdfium.googlesource.com/pdfium.git

# checkout the right branch
cd pdfium
git fetch origin $version
git checkout $version

# resolve third-party deps and download everything
gclient sync
