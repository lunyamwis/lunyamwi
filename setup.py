from setuptools import setup, find_packages

setup(
    name='lunyamwi',
    version='1.0.0',
    author='Martin Luther Bironga',
    description='Lunyamwi is a data science library that assists one in model selection and data pipeline creation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/LUNYAMWIDEVS/lunyamwi.git',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
