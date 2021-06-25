from setuptools import setup, find_packages

setup(
    name="libjari",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["pyyaml", "maya"],
    zip_safe=False,
)