# -*- coding: utf-8 -*-

from imio.urban.dataimport.access.importer import AccessDataImporter
from imio.urban.dataimport.access.interfaces import IAccessImporter
from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings

from zope.interface import implements


class AccessImporterSettings(ImporterSettings):
    """
    """


class AccessImporterFromImportSettings(ImporterFromSettingsForm):

    implements(IAccessImporter)

    def __init__(self, settings_form, importer_class=AccessDataImporter):
        """
        """
        super(AccessImporterFromImportSettings, self).__init__(settings_form, importer_class)
