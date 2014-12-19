# -*- coding: utf-8 -*-

from imio.urban.dataimport import _
from imio.urban.dataimport.browser.adapter import ControlPanelSubForm
from imio.urban.dataimport.interfaces import IImportSettingsForm

from plone import api
from plone.z3cform import layout

from z3c.form import button
from z3c.form import field
from z3c.form import form

from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class BaseUndoImportForm(form.Form, ControlPanelSubForm):
    """
    """
    def __init__(self, context, request):
        super(BaseUndoImportForm, self).__init__(context, request)

    @property
    def portal(self):
        return api.portal.get()

    def get_import_historic(self):
        historic_id = 'imio.urban.dataimport.import_historic:%s' % self.importer_name
        import_historic = IAnnotations(self.portal)[historic_id]
        return import_historic

    def get_undo_historic(self):
        historic_id = 'imio.urban.dataimport.undo_historic:%s' % self.importer_name
        undo_historic = IAnnotations(self.portal)[historic_id]
        return undo_historic


class IUndoImportSchema(Interface):
    """
    """

    undo_import = schema.Choice(
        title=_(u'Undo import'),
        vocabulary='imio.urban.dataimport.ListImportHistoric',
    )


class UndoImportForm(BaseUndoImportForm):
    """
    """

    implements(IImportSettingsForm)

    fields = field.Fields(IUndoImportSchema)
    description = _(u"Undo import")
    ignoreContext = True

    @button.buttonAndHandler(_('Undo import'), name=None)
    def handle_undo_import(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage

        import_time = data['undo_import']
        self.portal.manage_undo_transactions(
            self._get_transactions_to_undo(import_time)
        )
        self._update_import_historic_records(import_time)
        self.request.response.redirect("%s/@@dataimport-controlpanel" % (self.context.absolute_url()))

    def _get_transactions_to_undo(self, import_time):
        """
        """
        portal = api.portal.get()
        transactions_to_undo = []

        for transaction in portal.undoable_transactions():
            transaction_time = transaction['time'].micros()
            if import_time < transaction_time:
                transactions_to_undo.append(transaction['id'])
            else:
                break

        return transactions_to_undo

    def _update_import_historic_records(self, import_time_to_undo):
        """
        """
        import_historic = self.get_import_historic()
        for import_time in import_historic.keys():
            if import_time_to_undo <= import_time:
                import_historic.pop(import_time)


class UndoImportPanel(layout.FormWrapper):
    form = UndoImportForm


class ListImportHistoric(object):

    def __call__(self, context):
        controlpanel_view = context.restrictedTraverse(context.REQUEST.steps[-1])
        import_historic = controlpanel_view.undo_form_instance.form_instance.get_import_historic()

        if not import_historic:
            return SimpleVocabulary([SimpleTerm('no_historic', 'no_historic', _('No imports done'))])

        vocabulary_terms = []
        for import_time in sorted(import_historic.keys(), reverse=True):
            value = import_historic[import_time].split('\n')[-1]
            vocabulary_terms.append(SimpleTerm(import_time, import_time, _(value)))

        return SimpleVocabulary(vocabulary_terms)

import_historic_vocabulary = ListImportHistoric()


class IRedoImportSchema(Interface):
    """
    """

    undo_import = schema.Choice(
        title=_(u'Redo import'),
        vocabulary='imio.urban.dataimport.ListImportUndoHistoric',
    )


class RedoImportForm(BaseUndoImportForm):
    """
    """

    implements(IImportSettingsForm)

    fields = field.Fields(IRedoImportSchema)
    description = _(u"Redo import")
    ignoreContext = True

    @button.buttonAndHandler(_('Redo import'), name=None)
    def handle_redo_import(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage

        portal = api.portal.get()

        import_time = data['redo_import']
        portal.manage_redo_transactions(
            self._get_transactions_to_redo(import_time)
        )
        self._update_import_historic_records(import_time)
        self.request.response.redirect("%s/@@dataimport-controlpanel" % (self.context.absolute_url()))

    def _get_transactions_to_redo(self, import_time):
        """
        """
        portal = api.portal.get()
        transactions_to_redo = []

        for transaction in portal.redoable_transactions():
            transaction_time = transaction['time'].micros()
            if import_time < transaction_time:
                transactions_to_redo.append(transaction['id'])
            else:
                break

        return transactions_to_redo

    def _update_import_historic_records(self, import_time_to_redo):
        """
        """
        portal = api.portal.get()
        importer = self.new_importer()
        historic_id = 'imio.urban.dataimport.import_historic:%s' % importer.name
        import_historic = IAnnotations(portal)[historic_id]
        for import_time in import_historic.keys():
            if import_time_to_redo <= import_time:
                import_historic.pop(import_time)


class RedoImportPanel(layout.FormWrapper):
    form = RedoImportForm


class ListUndoHistoric(object):

    def __call__(self, context):
        controlpanel_view = context.restrictedTraverse(context.REQUEST.steps[-1])
        undo_historic = controlpanel_view.undo_form_instance.form_instance.get_undo_historic()

        if not undo_historic:
            return SimpleVocabulary([SimpleTerm('no_historic', 'no_historic', _('No undo done'))])

        vocabulary_terms = []
        for undo_time in sorted(undo_historic.keys(), reverse=True):
            value = undo_historic[undo_time].split('\n')[-1]
            vocabulary_terms.append(SimpleTerm(undo_time, undo_time, _(value)))

        return SimpleVocabulary(vocabulary_terms)

undo_historic_vocabulary = ListImportHistoric()
