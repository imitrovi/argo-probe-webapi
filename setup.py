from distutils.core import setup
import glob
import sys

NAME = 'argo-probe-webapi'
NAGIOSPLUGINS = '/usr/libexec/argo/probes/webapi'


def get_ver():
    try:
        for line in open(NAME+'.spec'):
            if "Version:" in line:
                return line.split()[1]
    except IOError:
        print ("Make sure that %s is in directory")  % (NAME+'.spec')
        sys.exit(1)


setup(name=NAME,
      version=get_ver(),
      license='ASL 2.0',
      author='SRCE, GRNET',
      author_email='dvrcic@srce.hr, kzailac@srce.hr, dhudek@srce.hr',
      description='Package includes probe for checking ARGO WEB-API',
      platforms='noarch',
      url='https://github.com/ARGOeu-Metrics/argo-probe-webapi',
      data_files=[(NAGIOSPLUGINS, glob.glob('src/*'))],
      packages=['argo_probe_webapi'],
      package_dir={'argo_probe_webapi': 'modules/'},
      )
