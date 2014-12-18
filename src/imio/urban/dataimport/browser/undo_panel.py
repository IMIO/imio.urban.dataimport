# -*- coding: utf-8 -*-

from imio.urban.dataimport import _
from imio.urban.dataimport.interfaces import IImportSettingsForm
from imio.urban.dataimport.interfaces import IUrbanDataImporter

from plone import api
from plone.z3cform import layout

from z3c.form import button
from z3c.form import field
from z3c.form import form

from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.interface import Interface
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IUndoImportSchema(Interface):
    """
    """

    undo_import = schema.Choice(
        title=_(u'Undo import'),
        vocabulary='imio.urban.dataimport.ListImportHistoric',
    )


class ListImportHistoric(object):

    def __call__(self, context):
        portal = api.portal.get()
        dataimport_transactions = IAnnotations(portal).get(
            'imio.urban.dataimport.import_historic:UrbawebDataImporter',
            None
        )

        if not dataimport_transactions:
            return SimpleVocabulary([SimpleTerm('no_historic', 'no_historic', _('No imports done'))])

        vocabulary_terms = []
        for import_time in sorted(dataimport_transactions.keys()):
            value = dataimport_transactions[import_time].split('\n')[-1]
            vocabulary_terms.append(SimpleTerm(import_time, import_time, _(value)))

        return SimpleVocabulary(vocabulary_terms)

import_historic_vocabulary = ListImportHistoric()


class UndoImportForm(form.Form):
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

        portal = api.portal.get()

        import_time = data['undo_import']
        portal.manage_undo_transactions(
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
        portal = api.portal.get()
        importer = getAdapter(self, IUrbanDataImporter)
        historic_id = 'imio.urban.dataimport.import_historic:%s' % importer.name
        import_historic = IAnnotations(portal)[historic_id]
        for import_time in import_historic.keys():
            if import_time_to_undo <= import_time:
                import_historic.pop(import_time)


class UndoImportPanel(layout.FormWrapper):
    form = UndoImportForm
