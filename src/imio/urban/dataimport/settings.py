# -*- coding: utf-8 -*-

from Products.statusmessages.interfaces import IStatusMessage

from imio.urban.dataimport import _
from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.interfaces import IImportSettingsForm
from imio.urban.dataimport.interfaces import IUrbanDataImporter

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from z3c.form import button

from zope.component import getAdapter
from zope.interface import Interface
from zope.interface import implements
from zope import schema


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


class ImporterSettingsEditForm(RegistryEditForm):
    """
    """

    implements(IImportSettingsForm)

    schema = IImporterSettingsSchema
    label = _(u"Importer settings")
    description = _(u"")

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

        importer = getAdapter(self, IUrbanDataImporter)
        importer.setupImport()
        importer.importData()
        importer.picklesErrorLog()


class ImporterSettings(ControlPanelFormWrapper):
    form = ImporterSettingsEditForm


class ImporterFromSettingsForm(object):

    implements(IUrbanDataImporter)

    def __init__(self, settings_form, importer_factory=UrbanDataImporter):
        self.form_datas, errors = settings_form.extractData()
        importer_settings = self.get_importer_settings()
        self.importer = importer_factory(**importer_settings)

    def importData(self):
        start = self.form_datas.get('start')
        end = self.form_datas.get('end')
        self.importer.importData(start, end)

    def get_importer_settings(self):
        """
        Hook to get dataimporter parameters (can be either on the form or from elsewhere..).
        Should return a dict like {'arg1_name': arg1_value, 'arg2_name': arg2_value, ...}
        To be overrided/implemented.
        """
        return {}

    def __getattr__(self, attr_name):
        """
        Delegate attribute/method call to the wrapped importer.
        """
        return getattr(self.importer, attr_name)