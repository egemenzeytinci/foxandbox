import os
import sys
from util.config.config import ConfigParser

path = os.environ['CONFIG'] if 'CONFIG' in os.environ else sys.argv[-1:][0]

if not os.path.exists(path):
    path = './default.ini'

config = ConfigParser.load(path)
