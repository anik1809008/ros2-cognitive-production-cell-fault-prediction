from setuptools import find_packages, setup

package_name = 'cell_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            'share/' + package_name,
            ['package.xml'],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Anik',
    maintainer_email='anik1809008@example.com',
    description='ROS 2 bringup package for the cognitive production cell project.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = cell_bringup.simple_publisher:main',
            'simple_subscriber = cell_bringup.simple_subscriber:main',
        ],
    },
)
