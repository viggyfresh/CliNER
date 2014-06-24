from setuptools import setup, find_packages


setup(
	name='clicon',
	version='0.1dev',
	packages=find_packages(),
	install_requires=[
		'click',
	],
	entry_points='''
		[console_scripts]
		clicon=clicon.cli:clicon
	''',
)