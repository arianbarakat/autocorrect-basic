from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(name='autocorrect',
      version='0.1',
      description='A python module for learning and  estimate the narrative arcs in literature',
      url='',
      author='Arian Barakat',
      long_description=long_description,
      author_email='arianbarakat@gmail.com',
      license='-',
      packages=find_packages(),
      package_dir={'autocorrect': 'autocorrect'},
      #package_data={'autocorrect': ['data/']},
      include_package_data=False,
      install_requires=[
                'sortedcollections>=0.6.1',
                'nltk>=3.3',
                'regex>=2018.1.10'],
      zip_safe=False)
