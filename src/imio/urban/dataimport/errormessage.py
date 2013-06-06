# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IImportErrorMessage

from zope.interface import implements


class ImportErrorMessage:
    """
    """

    implements(IImportErrorMessage)

    def __init__(self, importer, error_location, line, message, data):
        self.importer = importer
        self.error_location = error_location
        self.line = line
        self.message = message
        self.data = data

    def __str__(self):
        migration_step = self.error_location.__class__.__name__
        factory_stack = self.importer.current_containers_stack
        stack_display = '\n'.join(['%sid: %s Title: %s' % (''.join(['    ' for i in range(factory_stack.index(obj))]), obj.id, obj.Title()) for obj in factory_stack])

        message = [
            'line %s ' % self.importer.current_line,
            'migration substep: %s' % migration_step,
            'error message: %s' % self.message,
            'data: %s' % self.data,
            'plone containers stack:\n  %s' % stack_display,
        ]
        message = '\n'.join(message)

        return message
