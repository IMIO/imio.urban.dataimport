# -*- coding: utf-8 -*-

from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings
from imio.urban.dataimport.urbaweb.interfaces import IUrbawebDataImporter
from imio.urban.dataimport.urbaweb.importer import UrbawebDataImporter

from zope.interface import implements


class UrbawebImporterSettings(ImporterSettings):
    """
    """


class UrbawebImporterFromImportSettings(ImporterFromSettingsForm):

    implements(IUrbawebDataImporter)

    def __init__(self, settings_form, importer_class=UrbawebDataImporter):
        """
        """
        super(UrbawebImporterFromImportSettings, self).__init__(settings_form, importer_class)
