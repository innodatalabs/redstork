from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
from redstork import __version__

# This forces platform-specific package to be built
# https://stackoverflow.com/questions/45150304/how-to-force-a-python-wheel-to-be-platform-specific-when-building-it
class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False

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
    # cmdclass = {'bdist_wheel': bdist_wheel}
    python_requires='>=3.6',
)
