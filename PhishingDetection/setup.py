from setuptools import setup, find_packages

setup (
    name='your_package',  # Name of your package
    version='0.1.0',  # Initial release version
    packages=find_packages(where='src'),  # Automatically find packages in 'src'
    package_dir={'': 'src'},  # Specify that packages are under 'src'
    author='Chloe Coursey',
    author_email='cpcours2@ncsu.edu',
    description='A package to manage user accounts and authentication for various email services.',
    long_description=open('README.md').read(),
    url='https://github.com/cpcours2/PhishingDetection',
    install_requires=[
        # List any package dependencies here
        'requests',
        're',
        'os'
        # Add 'google-api-python-client' if you're using Google APIs
        ],
    python_requires='>=3.6',  # Minimum Python version required
    test_suite='tests',  # Specify the tests directory
)
