# -*- coding: utf-8 -*-

from imio.urban.dataimport.csv.importer import CSVDataImporter
from imio.urban.dataimport.csv.interfaces import ICSVImporter
from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings

from zope.interface import implements


class CSVImporterSettings(ImporterSettings):
    """
    """


class CSVImporterFromImportSettings(ImporterFromSettingsForm):

    implements(ICSVImporter)

    def __init__(self, settings_form, importer_class=CSVDataImporter):
        """
        """
        super(CSVImporterFromImportSettings, self).__init__(settings_form, importer_class)
