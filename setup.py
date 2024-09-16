from setuptools import setup, find_packages

setup(
    name='lunyamwi',
    version='1.0.5',
    author='Martin Luther Bironga',
    description='Lunyamwi is a data science library that assists one in data generation, pipeline setup, model selection and setup.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/LUNYAMWIDEVS/lunyamwi.git',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
