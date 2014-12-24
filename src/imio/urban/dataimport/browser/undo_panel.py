# -*- coding: utf-8 -*-

from DateTime import DateTime

from imio.urban.dataimport import _
from imio.urban.dataimport.browser.adapter import ControlPanelSubForm
from imio.urban.dataimport.interfaces import IImportSettingsForm

from plone import api
from plone.z3cform import layout

from z3c.form import button
from z3c.form import field
from z3c.form import form

from zope import schema
from zope.interface import Interface
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import re
import transaction


class BaseUndoImportForm(form.Form, ControlPanelSubForm):
    """
    """
    def __init__(self, context, request):
        super(BaseUndoImportForm, self).__init__(context, request)

    @property
    def portal(self):
        return api.portal.get()

    @property
    def historic(self):
        return self.portal.__urbandataimport__

    @property
    def import_historic_id(self):
        return 'imio.urban.dataimport.import_historic:%s' % self.importer_name

    @property
    def undo_historic_id(self):
        return 'imio.urban.dataimport.undo_historic:%s' % self.importer_name

    def get_import_historic(self):
        historic_id = self.import_historic_id
        if historic_id not in self.historic:
            self.historic[historic_id] = {}
        return self.historic[historic_id]

    def set_import_historic(self, historic):
        self.historic[self.import_historic_id] = dict(historic)

    def get_undo_historic(self):
        historic_id = self.undo_historic_id
        if historic_id not in self.historic:
            self.historic[historic_id] = {}
        return self.historic[historic_id]

    def set_undo_historic(self, historic):
        self.historic[self.undo_historic_id] = dict(historic)

    def redirect(self):
        self.request.response.redirect(
            "%s/@@dataimport-controlpanel/#fieldsetlegend-undo" % (self.context.absolute_url())
        )


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

        new_import_historic, undone_imports = self._get_new_import_historic(import_time)
        new_undo_historic = self._get_new_undo_historic(undone_imports)

        self.portal.manage_undo_transactions(
            self._get_transactions_to_undo(import_time)
        )
        transaction.commit()

        self.set_import_historic(new_import_historic)
        self.set_undo_historic(new_undo_historic)
        self.redirect()

    @button.buttonAndHandler(_('Forget undo'), name=None)
    def handle_remove_undo(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage

        import_time = data['undo_import']

        import_historic = self.get_import_historic()
        import_historic.pop(import_time)
        self.set_import_historic(import_historic)
        self.redirect()

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

    def _get_new_import_historic(self, import_time_to_undo):
        """
        """
        import_historic = self.get_import_historic()
        undone_imports = []
        for import_time in sorted(import_historic.keys()):
            if import_time_to_undo <= import_time:
                undone_imports.append(
                    (import_time, import_historic.pop(import_time))
                )
        return import_historic, undone_imports

    def _get_new_undo_historic(self, undone_imports):
        """
        """
        undo_historic = self.get_undo_historic()
        date = DateTime()
        undo_date = u'{date} - {time}'.format(
            date=date.strftime('%d/%m/%Y'),
            time=date.Time(),
        )
        undo_historic[date.micros()] = {'date': undo_date, 'undone': undone_imports}
        return undo_historic


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

    redo_import = schema.Choice(
        title=_(u'Redo import'),
        vocabulary='imio.urban.dataimport.ListUndoHistoric',
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

        undo_time = data['redo_import']
        new_undo_historic, redone_imports = self._get_new_undo_historic(undo_time)
        new_import_historic = self._get_new_import_historic(redone_imports)

        self.portal.manage_undo_transactions(
            self._get_transactions_to_undo(undo_time)
        )
        transaction.commit()

        self.set_undo_historic(new_undo_historic)
        self.set_import_historic(new_import_historic)
        self.redirect()

    @button.buttonAndHandler(_('Forget redo'), name=None)
    def handle_remove_redo(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage

        undo_time = data['redo_import']

        undo_historic = self.get_undo_historic()
        undo_historic.pop(undo_time)
        self.set_undo_historic(undo_historic)
        self.redirect()

    def _get_transactions_to_undo(self, undo_time):
        """
        """
        portal = api.portal.get()
        transactions_to_redo = []

        for transaction in portal.undoable_transactions():
            transaction_time = transaction['time'].micros()
            if undo_time < transaction_time:
                transactions_to_redo.append(transaction['id'])
            else:
                break

        return transactions_to_redo

    def _get_new_undo_historic(self, undo_time_to_redo):
        """
        """
        undo_historic = self.get_undo_historic()
        redone_imports = []
        for undo_time in undo_historic.keys():
            if undo_time_to_redo <= undo_time:
                redone_imports.append(undo_historic.pop(undo_time)['undone'])
        return undo_historic, redone_imports

    def _get_new_import_historic(self, redone_imports):
        """
        """
        import_historic = self.get_import_historic()
        for imports in redone_imports:
            import_historic.update(dict(imports))
        return import_historic


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
            undos = undo_historic[undo_time]
            date = undos['date']
            value = ', '.join([re.search('line (.+)       ', undo[1]).group(1) for undo in undos['undone']])
            vocabulary_terms.append(SimpleTerm(undo_time, undo_time, _('line %s -  %s' % (value, date))))

        return SimpleVocabulary(vocabulary_terms)

undo_historic_vocabulary = ListUndoHistoric()
