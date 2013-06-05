# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IUrbanDataImporter, IObjectsMapping, \
    IUrbanImportSource, IValuesMapping, IPostCreationMapper

from zope.interface import implements
import zope


class UrbanDataImporter(object):
    """
    """

    implements(IUrbanDataImporter)

    def __init__(self, context):
        """ """

        self.site = context.getSite()
        self.datasource = None
        self.objects_mappings = None
        self.values_mappings = None

        # attributes to be set up before running import
        self.factories = {}
        self.mappers = {}
        self.allowed_containers = {}

        # log and tracing vars
        self.current_line = 1
        self.errors = {}
        self.sorted_errors = {}

    def importData(self, start=1, end=0):
        """ import data from line 'start' to line 'end' """

        self.setupImport()

        for dataline in self.datasource.iterdata():
            if end and self.current_line > end:
                break
            elif start <= self.current_line:
                self.importDataLine(dataline)
            self.current_line += 1

    def importDataLine(self, dataline):
        print "PROCESSING LINE %i" % self.current_line
        objects_nesting = self.objects_mappings.getObjectsNesting()
        self.createPloneObjects(objects_nesting, dataline)

    def setupImport(self):

        self.datasource = zope.component.getAdapter(self, IUrbanImportSource, 'data source')
        self.objects_mappings = zope.component.getAdapter(self, IObjectsMapping, 'objects mapping')
        # self.values_mappings = zope.component.getAdapter(self, IValuesMapping, 'values mapping')

        fields_mappings = self.objects_mappings.getFieldsMapping()

        for objectname, mapping in fields_mappings.iteritems():
            self.setupFactory(objectname, mapping)
            self.setupObjectMappers(objectname, mapping)
            self.setupAllowedContainer(objectname, mapping)

    def setupFactory(self, objectname, mapping):
        factory_settings = mapping['factory']
        factory_class = factory_settings[0]
        factory_args = {}
        if len(factory_settings) == 2:
            factory_args = factory_settings[1]
        factory = factory_class(self.site, **factory_args)
        self.factories[objectname] = factory

    def setupObjectMappers(self, objectname, mapping):
        mappers = {
            'pre': [],
            'post': [],
        }

        for mapper_class, mapper_args in mapping['mappers'].iteritems():
            #initialize the mapper
            mapper = mapper_class(self, mapper_args)
            if IPostCreationMapper.implementedBy(mapper_class):
                mappers['post'].append(mapper)
            else:
                mappers['pre'].append(mapper)

        self.mappers[objectname] = mappers

    def setupAllowedContainer(self, objectname, mapping):
        allowed_containers = mapping.get('allowed_containers', None)
        if allowed_containers:
            self.allowed_containers[objectname] = allowed_containers

    def createPloneObjects(self, node, line, stack=[]):
        for object_name, subobjects in node:
            factory_args = {}
            container = stack and stack[-1] or None
            # next line means, we create the object if we have no explicit container or if we have a legal one
            allowcreation = not container or self.allowed_containers.get(object_name, '') == container.portal_type
            if allowcreation:
                #collect all the data(s) that will be passed to the factory
                for mapper in self.mappers[object_name]['pre']:
                    factory_args.update(mapper.map(line, container=container))
                #create the object(s)
                factory = self.factories[object_name]
                objs = factory.create(place=container, **factory_args)
                # if for some reasons the object creation went wrong, we skip this line and continue the import
                if objs is None:
                    return
                #update some fields after creation
                for obj in objs:
                    for mapper in self.mappers[object_name]['post']:
                        mapper.map(line, plone_object=obj, site=self.site)
                    obj.processForm()
                    stack.append(obj)
                    # recursive call
                    self.createPloneObjects(subobjects, line, stack)
                    stack.pop()

    def logError(self, migrator_locals, location, message, factory_stack, data):
        pass

    def log(self, migrator_locals, location, message, factory_stack, data):
        pass
