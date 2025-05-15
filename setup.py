from setuptools import setup, find_packages

setup(
    name='chat_threads',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'pytz',
        'pydantic'
    ],
    author='Mitanshu Bhatt',
    author_email='mitanshubhatt@gofynd.com',
    description='Common utilities for Fex projects',
    url='https://github.com/mitanshu610/chat_threads.git',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',  # Assuming MIT License, change if different
        'Programming Language :: Python :: 3.10',  # Specify the exact versions you support
        'Programming Language :: Python :: 3.11'
    ],
    python_requires='>=3.10',
)
