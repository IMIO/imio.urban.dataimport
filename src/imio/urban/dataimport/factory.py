# -*- coding: utf-8 -*-

from imio.urban.dataimport.errors import IdentifierError
from imio.urban.dataimport.errors import NoPortalTypeError
from imio.urban.dataimport.interfaces import IFactory

from plone import api

from zope.interface import implements


#
# Factories
#


class BaseFactory(object):

    implements(IFactory)

    def __init__(self, importer, portal_type=''):
        self.importer = importer
        self.site = api.portal.get()
        self.portal_type = portal_type

    def create(self, kwargs, container=None, line=None):
        portal_type = kwargs.get('portal_type', self.getPortalType(container, **kwargs))
        if not portal_type:
            raise NoPortalTypeError
        if 'id' in kwargs:
            kwargs['id'] = kwargs['id'].strip('_')
            if not kwargs['id']:
                raise IdentifierError
            object_id = container.invokeFactory(portal_type, **kwargs)
        else:
            raise IdentifierError
        obj = getattr(container, object_id)
        if obj:
            for field_name, val in kwargs.iteritems():
                if field_name.lower() not in ['id', 'title', 'portal_type']:
                    field = obj.getField(field_name)
                    if field:
                        field.getMutator(obj)(val)
        return obj

    def logError(self, factory, line, msg, data={}):
        """ """
        self.importer.logError(factory, line, msg, data)

    def getCreationPlace(self, factory_args):
        return None

    def getPortalType(self, container=None, **kwargs):
        return self.portal_type

    def objectAlreadyExists(self, object_args, container):
        existing_object = container.get(object_args.get('id', ''), None)
        return existing_object


class UrbanEventFactory(BaseFactory):
    """
    Base class for urbanEvent factory.
    """

    def create(self, kwargs, container, line):
        eventtype_uid = kwargs.pop('eventtype')
        if 'eventDate' not in kwargs:
            kwargs['eventDate'] = None
        main_args = {'eventDate': kwargs.pop('eventDate')}
        urban_event = container.createUrbanEvent(eventtype_uid, **main_args)
        for k, v in kwargs.iteritems():
            field = urban_event.getField(k)
            if field:
                setter = field.getMutator(urban_event)
                setter(v)
        return urban_event
