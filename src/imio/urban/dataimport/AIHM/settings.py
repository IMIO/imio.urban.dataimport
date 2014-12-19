# -*- coding: utf-8 -*-

from imio.urban.dataimport.AIHM.importer import AIHMDataImporter
from imio.urban.dataimport.AIHM.interfaces import IAIHMDataImporter
from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings

from zope.interface import implements


class AIHMImporterSettings(ImporterSettings):
    """
    """


class AIHMImporterFromSettingsForm(ImporterFromSettingsForm):

    implements(IAIHMDataImporter)

    def __init__(self, settings_form, importer_class=AIHMDataImporter):
        """
        """
        super(AIHMImporterFromSettingsForm, self).__init__(settings_form, importer_class)
