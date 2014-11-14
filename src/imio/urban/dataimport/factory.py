# -*- coding: utf-8 -*-

from imio.urban.dataimport.errors import IdentifierError
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
            return
        if 'id' in kwargs:
            kwargs['id'] = kwargs['id'].strip('_')
            if not kwargs['id']:
                raise IdentifierError
            try:
                object_id = container.invokeFactory(portal_type, **kwargs)
            except:
                import ipdb; ipdb.set_trace()
        else:
            raise IdentifierError
        obj = getattr(container, object_id)
        obj._renameAfterCreation()
        return obj

    def logError(self, factory, line, msg, data={}):
        """ """
        self.importer.logError(factory, line, msg, data)

    def getCreationPlace(self, factory_args):
        return None

    def getPortalType(self, place=None, **kwargs):
        return self.portal_type

    def objectAlreadyExists(self, object_args, container):
        existing_object = getattr(container, object_args['id'], None)
        return existing_object


class MultiObjectsFactory(BaseFactory):

    def create(self, args, container=None, line=None):
        objs = []
        for object_args in args:
            objs.append(super(MultiObjectsFactory, self).create(object_args, container=container)[0])
        return objs
