# -*- coding: utf-8 -*-

import os
import subprocess


def isNotCurrentProfile(context):
    return context.readDataFile("imiourbandataimport_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return

    # create dir to put the raw source files to import (database, csv, ...)
    if 'dataimport' not in os.listdir('var'):
        subprocess.Popen(['mkdir', 'var/urban.dataimport'])
