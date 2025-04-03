from setuptools import setup, find_packages

setup(
    name='thinkfastquiz',
    packages=find_packages(),
    install_requires=[
        'fastapi[standard]==0.115.12',
        'sqlalchemy==2.0.40'
    ],
    zip_safe=False
)
