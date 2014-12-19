# -*- coding: utf-8 -*-

from Products.statusmessages.interfaces import IStatusMessage

from imio.urban.dataimport import _
from imio.urban.dataimport.browser.adapter import ControlPanelSubForm
from imio.urban.dataimport.interfaces import IImportSettingsForm

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from z3c.form import button

from zope import schema
from zope.interface import Interface
from zope.interface import implements


class IImporterSettingsSchema(Interface):
    """
    """

    start = schema.Int(
        title=_(u'Start line'),
        required=True,
    )

    end = schema.Int(
        title=_(u'End line'),
        required=True,
    )

    savepoint_length = schema.Int(
        title=_(u'Savepoint every nth object imported'),
        required=True,
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
        importer = self.new_importer()
        importer.setupImport()
        importer.importData(start, end)
        importer.picklesErrorLog()


class ImporterSettings(ControlPanelFormWrapper):
    form = ImporterSettingsForm
