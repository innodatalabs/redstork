import sys
from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
from redstork import __version__

# This forces platform-specific package to be built
# https://stackoverflow.com/questions/45150304/how-to-force-a-python-wheel-to-be-platform-specific-when-building-it
class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        print(sys.platform)
        if sys.platform == 'linux':
            self.plat_name = 'manylinux1_x86_64'
        elif sys.platform == 'win32':
            self.plat_name = 'win64'
        elif sys.platform == 'darwin':
            self.plat_name = 'macosx_10_9_intel'
        else:
            assert False, sys.platform
        self.python_tag = 'py3'
        self.plat_name_supplied = True

with open('README.md') as f:
    long_description = f.read()

setup(
    name        = 'redstork',
    version     = __version__,
    description = 'Parsing PDF files with PDFium',
    author      ='Mike Kroutikov',
    author_email='mkroutikov@innodata.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url         ='https://github.com/innodatalabs/redstork',
    license     ='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    package_data = {'': ['linux/*.so', 'win/*.dll', 'darwin/*.so', 'pdfium_version.txt']},
    cmdclass = {'bdist_wheel': bdist_wheel},
    python_requires='>=3.6',
)
