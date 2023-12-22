import os
import sys
from ini import IniConfig

path = sys.argv[-1:][0] if sys.argv[-1:][0].endswith('.ini') else os.environ['CONFIG']

if not os.path.exists(path):
    path = './default.ini'

config = IniConfig.read(path)
