#!/usr/bin/env python3

from setuptools import setup, find_packages

requires = [
    "equations (>=1.0,<2.0)",
    # "discord.py (>=1.0,<2.0)",
    "sqlalchemy (>=1.2,<2.0)",
    "psycopg2 (>=2.7,<3.0)",
]

setup(name='Dice-bot',
      version='1.0.1',
      description='Discord bot for managing D&D characters',
      author='BHodges',
      url='https://github.com/b-hodges/dice-bot',
      install_requires=requires,
      scripts=['dice-bot.py'],
      packages=find_packages())
