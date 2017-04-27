from setuptools import setup

setup(
    name='vm_monitor',
    packages=['vm_monitor'],
    include_package_data=True,
    install_requires=[
        'flask',
        'azure>=2.0.0rc6',
        'pytz',
        'tzlocal',
    ],
)