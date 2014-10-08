# -*- coding: utf-8 -*-

from imio.urban.dataimport.urbaweb.interfaces import IUrbawebDataImporter
from imio.urban.dataimport.settings import ImporterSettings
from imio.urban.dataimport.settings import ImporterFromSettingsForm
from imio.urban.dataimport.urbaweb.importer import UrbawebDataImporter

from zope.interface import implements


class UrbawebImporterSettings(ImporterSettings):
    """
    """


class UrbawebImporterFromSettingsForm(ImporterFromSettingsForm):

    implements(IUrbawebDataImporter)

    def __init__(self, settings_form, importer_factory=UrbawebDataImporter):
        """
        """
        super(UrbawebImporterFromSettingsForm, self).__init__(settings_form, importer_factory)
