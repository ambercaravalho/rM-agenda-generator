from setuptools import setup, find_packages

setup(
    name='kivy-desktop-app',
    version='0.1.0',
    description='A Kivy application for desktop platforms',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'kivy',
        # Add other dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Kivy',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)