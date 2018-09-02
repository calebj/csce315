from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="gamedb",
    version="0.1.0",
    author="Caleb Johnson",
    author_email="me@calebj.io",
    description="A gamer information database with a console UI",
    license="GPL",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={"console_scripts": ["gamedb = gamedb.command:main"]},
    package_data={"gamedb": ["data/init.sql"]},
    python_requires='>=3.6',
)
