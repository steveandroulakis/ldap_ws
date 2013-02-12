from setuptools import setup, find_packages

setup(
    name = "ldap_ws",
    version = "1.0",
    url = 'http://github.com/steveandroulakis/ldap_ws',
    license = 'BSD',
    description = "Simple web service on top of LDAP",
    author = 'Steve Androulakis',
    packages = find_packages(),
    install_requires = ['setuptools',
                        'django==1.4.3',
                        'south==0.7.6'],
)
