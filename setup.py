from setuptools import find_packages, setup
setup(
    name='libdgus',
    packages=find_packages(include=['dgus*']),
    version='0.0.2',
    description='Library to control DGUS Displays',
    author='Sebastian Holzgreve',
    license='GPLv3',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)