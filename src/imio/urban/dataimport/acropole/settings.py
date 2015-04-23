# -*- coding: utf-8 -*-

from imio.urban.dataimport.acropole.importer import AcropoleDataImporter
from imio.urban.dataimport.acropole.interfaces import IAcropoleDataImporter
from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings

from zope.interface import implements


class AcropoleImporterSettings(ImporterSettings):
    """
    """


class AcropoleImporterFromImportSettings(ImporterFromSettingsForm):

    implements(IAcropoleDataImporter)

    def __init__(self, settings_form, importer_class=AcropoleDataImporter):
        """
        """
        super(AcropoleImporterFromImportSettings, self).__init__(settings_form, importer_class)
