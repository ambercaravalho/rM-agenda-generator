from setuptools import setup, find_packages

setup(
    name='remarkable-agenda-generator',
    version='0.1.0',
    description='A tool for generating agenda PDFs for reMarkable devices',
    author='Amber Caravalho',
    author_email='hello@ambercaravalho.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'kivy>=2.1.0',
        'reportlab>=3.6.12',
        'pdf2image>=1.16.3',
        'python-dateutil>=2.8.2',
        'Pillow>=9.4.0',
        'poppler-utils>=0.1.0',
        'plyer>=2.1.0',
        'pygments>=2.10.0',
        'kivy-garden.contextmenu>=0.1.0.dev0',
        'watchdog>=2.1.6',
        'kivymd>=1.0.0',
        'weasyprint>=54.0',
        'pdfrw>=0.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Kivy',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'remarkable-agenda=src.main:main',
        ],
    },
)