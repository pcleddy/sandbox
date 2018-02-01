from setuptools import setup, find_packages

REQUIREMENTS = ['flask', 'flask-restful', 'nose', 'pymysql', 'celery[redis]']

setup(
    name='mr_api',
    version='1.0',
    description="API for MR (monitor request) infrastructure",
    author='Steve Baker',
    author_email='steven.a.baker@jpl.nasa.gov',
    packages=find_packages(),
    install_requires=REQUIREMENTS
)