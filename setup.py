# -*- coding: utf-8 -*-
'''
setup.py

installation script

'''
from pathlib import Path
from setuptools import setup, find_packages


long_description = (Path(__file__).parent / 'README.md').read_text()


def run():
   setup(
      name='pyplayscheduler',
      version='0.1',
      description='python library and webapp for scheduling pickleball games',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Eric Truett',
      author_email='sansbacon@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={'pyscheduler': ['data/*.json']},
      zip_safe=False,
      classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
      ],
      python_requires='>=3.8'
   )


if __name__ == '__main__':
    run()