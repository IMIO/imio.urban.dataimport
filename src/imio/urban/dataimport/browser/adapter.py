# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IUrbanDataImporter
from imio.urban.dataimport.importer import UrbanDataImporter

from zope.component import getAdapter
from zope.interface import implements


class ImporterFromSettingsForm(object):

    implements(IUrbanDataImporter)

    def __init__(self, settings_form, importer_class=UrbanDataImporter):
        self.form = settings_form
        self.importer_class = importer_class

    def get_importer_settings(self):
        settings = {
            'split_division_range': self.form_datas.get('fragmentation_range'),
            'split_division_target': self.form_datas.get('fragmentation_target'),
        }
        return settings

    def __call__(self):
        self.form_datas, errors = self.form.extractData()
        importer_settings = self.get_importer_settings()
        importer = self.importer_class(**importer_settings)
        return importer


class ControlPanelSubForm(object):
    """
    """

    @property
    def importer_name(self):
        importer_factory = getAdapter(self, IUrbanDataImporter)
        importer_name = importer_factory.importer_class.__name__
        return importer_name

    def new_importer(self, name):
        importer_factory = getAdapter(
            self,
            IUrbanDataImporter,
            name=name
        )
        return importer_factory()
