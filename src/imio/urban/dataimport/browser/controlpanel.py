# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from imio.urban.dataimport.browser.import_panel import ImporterSettings


class ImporterControlPanel(BrowserView):
    """
    """

    import_form = ImporterSettings

    def __init__(self, context, request):
        super(ImporterControlPanel, self).__init__(context, request)
        self.import_form_instance = self.import_form(aq_inner(context), request)

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        self.import_form_instance()

    def render(self):
        controlpanel_template = ViewPageTemplateFile('controlpanel.pt')
        return controlpanel_template(self)

    def label(self):
        return self.import_form_instance.label()
