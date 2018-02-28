# -*- coding: utf-8 -*-

from Products.statusmessages.interfaces import IStatusMessage

from imio.urban.dataimport import _
from imio.urban.dataimport.browser.adapter import ControlPanelSubForm
from imio.urban.dataimport.interfaces import IImportSettingsForm
from imio.urban.dataimport.interfaces import IUrbanDataImporter

from plone import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from z3c.form import button

from zope import schema
from zope.component import getAdapters
from zope.interface import Interface
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import collective.noindexing

import os
import ConfigParser as configparser


class IImporterSettingsSchema(Interface):
    """
    """
    selected_importer = schema.Choice(
        title=_(u'Importer'),
        vocabulary='imio.urban.dataimport.AvailableImporters',
        required=True,
    )

    start = schema.Int(
        title=_(u'Start line'),
        required=True,
    )

    end = schema.Int(
        title=_(u'End line'),
        required=True,
    )

    fragmentation_range = schema.Int(
        title=_(u'Fragmentation range'),
        default=1,
        required=False,
    )

    fragmentation_target = schema.Int(
        title=_(u'Fragmentation target'),
        default=0,
        required=False,
    )


class ImporterSettingsForm(RegistryEditForm, ControlPanelSubForm):
    """
    """

    implements(IImportSettingsForm)

    schema = IImporterSettingsSchema
    description = _(u"Importer schema")

    def updateWidgets(self):
        super(ImporterSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name=None)
    def handle_save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.context.REQUEST.RESPONSE.redirect("@@dataimport-controlpanel")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_('Start import'), name=None)
    def handle_start_import(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage

        start = data.get('start')
        end = data.get('end')
        selected_importer = data.get('selected_importer')
        importer = self.new_importer(selected_importer)
        importer.setupImport()
        # parse option
        config = configparser.ConfigParser()
        config.read(os.path.join(os.getcwd(), 'var/urban.dataimport', 'utils.cfg'))
        self.no_index = int(config.get("no_index", "active"))
        if self.no_index:
            collective.noindexing.patches.apply()
        importer.importData(start, end)
        if self.no_index:
            collective.noindexing.patches.unapply()
        importer.picklesErrorLog()


class ImporterSettings(ControlPanelFormWrapper):
    form = ImporterSettingsForm


class AvailableImporters(object):

    def __call__(self, context):

        site = api.portal.get()
        panel_view = site.restrictedTraverse('@@dataimport-controlpanel')
        if hasattr(panel_view, 'import_form_instance'):
            import_form = getattr(panel_view, 'form_instance', panel_view.import_form_instance.form_instance)
        else:
            import_form = panel_view.form_instance

        adapters = list(getAdapters((import_form,), IUrbanDataImporter))

        vocabulary_terms = []
        for name, adapter in adapters:
            vocabulary_terms.append(
                SimpleTerm(name, name, name)
            )

        vocabulary = SimpleVocabulary(vocabulary_terms)
        return vocabulary
