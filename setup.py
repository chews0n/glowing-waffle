import setuptools

setuptools.setup(
    name='glowingwaffle',
    version='0.2',
    package_dir={"": "glowingwaffle"},
    packages=setuptools.find_packages(where="glowingwaffle"),
    entry_points={ 'console_scripts': ['Package = glowingwaffle.__main__:main' ] },
    python_requires=">=3.6",
    url='https://github.com/chews0n/glowing-waffle',
    license='',
    author='chewson',
    author_email='chris@thehewsons.com',
    description='Create, train and run models for determining optimal frac design'
)
