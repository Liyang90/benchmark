import subprocess
import sys


def setup_install():
    subprocess.check_call([sys.executable, 'setup.py', 'develop', '--user'])

if __name__ == '__main__':
    setup_install()
