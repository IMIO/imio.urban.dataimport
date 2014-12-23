# -*- coding: utf-8 -*-

from persistent.mapping import PersistentMapping

import os
import subprocess


def isNotCurrentProfile(context):
    return context.readDataFile("imiourbandataimport_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return

    portal = context.getSite()
    if not hasattr(portal, '__urbandataimport__'):
        context.getSite().__urbandataimport__ = PersistentMapping()

    # create dir to put the raw source files to import (database, csv, ...)
    if 'dataimport' not in os.listdir('var'):
        subprocess.Popen(['mkdir', 'var/urban.dataimport'])
