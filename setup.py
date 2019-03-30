import os
import setuptools

short_description = 'Fracture is a lightweight and flexible data management system'
if os.path.exists('README.md'):
    with open('README.md', 'r') as fh:
        long_description = fh.read()

else:
    long_description = short_description

setuptools.setup(
    name='fracture',
    version='0.9.1',
    author='Mike Malinowski',
    author_email='mike@twisted.space',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikemalinowski/fracture',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['factories'],
    package_data={
        '': ['sql/*.sql', '_res/*.png'],
    },
    keywords="fracture data composite",
)
