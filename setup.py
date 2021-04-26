import setuptools

setuptools.setup(
    name='glowingwaffle',
    version='0.2',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['glowingwaffle=glowingwaffle.__main__:main']},
    python_requires=">=3.6",
    url='https://github.com/chews0n/glowing-waffle',
    license='',
    author='chewson',
    author_email='chris@thehewsons.com',
    description='Create, train and run models for determining optimal frac design'
)
