from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Run your post install script here
        print("Running post-install steps...")

        # Install shakermaker by running its setup.py
        subprocess.run(["python", "./shakermaker/setup.py", "install"])

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
        "libopenmpi-dev",
        "mpich",
        "mpi4py",
        "python3-numpy",
        "scipy",
        "matplotlib",
        # Add any other packages that your project depends on
    ]
)
