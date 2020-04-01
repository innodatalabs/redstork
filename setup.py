from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

# This forces platform-specific package to be built
# https://stackoverflow.com/questions/45150304/how-to-force-a-python-wheel-to-be-platform-specific-when-building-it
class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False


setup(
    name    = 'red',
    version = '0.0.1',
    description= 'Parsing PDF files with PDFium',
    long_description='TODO',

    license='Commercial',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    package_data = {'': ['linux/*.so', 'win/*.dll']},
    cmdclass = {'bdist_wheel': bdist_wheel}
)
