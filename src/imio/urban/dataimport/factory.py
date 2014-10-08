# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import normalizeString

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

    def create(self, place=None, line=None, **kwargs):
        portal_type = kwargs.get('portal_type', self.getPortalType(place, **kwargs))
        if not portal_type:
            return
        container = place and place or self.getCreationPlace(**kwargs)
        if 'id' in kwargs:
            kwargs['id'] = kwargs['id'].strip('_')
            if not kwargs['id']:
                return []
            try:
                object_id = container.invokeFactory(portal_type, **kwargs)
            except:
                import ipdb; ipdb.set_trace()
        else:
            proposed_id = self.getDefaultId(**kwargs)
            object_id = container.invokeFactory(portal_type, id=proposed_id, **kwargs)
        obj = getattr(container, object_id)
        obj._renameAfterCreation()
        return [obj]

    def logError(self, factory, line, msg, data={}):
        """ """
        self.importer.logError(factory, line, msg, data)

    def getCreationPlace(self, **kwargs):
        return None

    def getPortalType(self, place=None, **kwargs):
        return self.portal_type

    def getDefaultId(self, place, **kwargs):
        portal_type = self.portal_type and self.portal_type or kwargs['portal_type']
        return normalizeString(self.site.generateUniqueId(portal_type))


class MultiObjectsFactory(BaseFactory):

    def create(self, place=None, line=None, **kwargs):
        objs = []
        for index, args in kwargs.iteritems():
            if 'id' not in args:
                args['id'] = self.getDefaultId(place, **args)
            objs.append(super(MultiObjectsFactory, self).create(place, **args)[0])
        return objs
