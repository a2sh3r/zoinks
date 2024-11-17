from setuptools import setup

setup(
    name='tsa-zoinks',
    version='0.1.1',
    packages=['zoinks'],
    entry_points={
        'console_scripts': [
            'zoinks = zoinks.main:main',
        ],
    },
    install_requires=['colorama'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitflic.ru/project/a2sh3r/zoinks',
    author='Zainutdinov Mikhail',
    author_email='michaelzainutdinov@ya.ru',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
