from setuptools import setup
from setuptools.command.install import install
import subprocess
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Run your post install script here
        print("Running post-install steps...")

        # Change directory to shakermaker
        os.chdir('shakermaker')

        # Install shakermaker by running its setup.py
        subprocess.run(["python", "setup.py", "install"])

        # Change directory back to the root
        os.chdir('..')

        # Install Python dependencies for fk-syn
        subprocess.run(["pip", "install", "matplotlib", "obspy", "scipy"])

        # Continue with the installation process
        install.run(self)

setup(
    name="YourProjectName",
    version="0.1",
    cmdclass={
        'install': PostInstallCommand,
    },
    install_requires=[
        "mpi4py",
        "h5py",
        # Remove libopenmpi-dev and mpich from here since they are system packages
        # Remove python3-numpy since we will use pip to install numpy which is compatible with the environment
        "scipy",
        "matplotlib",
        # Add any other packages that your project depends on
    ]
)
