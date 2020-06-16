# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#
#  Author: Forrest Xiong
#  Email:  forrestisagoodman@gmail.com
#  wechat: ARealGoodGuy

import sys
import os
from lib.core.Controller import ControllerClass
from lib.common.Util import *

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, Spider-AUProperty requires Python 3.x\n")
    sys.exit(1)


class Program:
    def __init__(self):
        ControllerClass(get_parser().parse_args()).start_job()


if __name__ == '__main__':
    main = Program()
