import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'cell_bringup'

setup(
    name=package_name,
    version='0.1.0',
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
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py'),
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.sdf'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Anik',
    maintainer_email='anik1809008@example.com',
    description='ROS 2 digital twin package for resilience-aware adaptive workload reallocation in a two-cell production system.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = cell_bringup.simple_publisher:main',
            'simple_subscriber = cell_bringup.simple_subscriber:main',
            'cell_state_simulator = cell_bringup.cell_state_simulator:main',
            'delay_detector = cell_bringup.delay_detector:main',
            'adaptive_reallocator = cell_bringup.adaptive_reallocator:main',
            'resilience_score = cell_bringup.resilience_score:main',
            'experiment_logger = cell_bringup.experiment_logger:main',
            'gazebo_workpiece_animator = cell_bringup.gazebo_workpiece_animator:main',
            'continuous_workpiece_animator = cell_bringup.continuous_workpiece_animator:main',
            'fault_predictor = cell_bringup.fault_predictor:main',
            'rl_reallocator = cell_bringup.rl_reallocator:main',
        ],
    },
)
