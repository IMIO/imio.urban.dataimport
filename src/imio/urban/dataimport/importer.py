# -*- coding: utf-8 -*-

from imio.urban.dataimport.interfaces import IUrbanDataImporter, IObjectsMapping, \
    IUrbanImportSource, IValuesMapping, IPostCreationMapper, IImportErrorMessage

from zope.interface import implements
import zope

import os
import pickle


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
        self.current_containers_stack = []
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
        self.createUrbanObjects(objects_nesting, dataline)

    def setupImport(self):

        self.datasource = zope.component.getAdapter(self, IUrbanImportSource, 'data source')
        self.objects_mappings = zope.component.getAdapter(self, IObjectsMapping, 'objects mapping')
        self.values_mappings = zope.component.getAdapter(self, IValuesMapping, 'values mapping')

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

    def createUrbanObjects(self, node, line, stack=[]):

        # to be sure to create a different empty list at each new non-recursive call
        stack = stack and stack or []
        self.current_containers_stack = stack

        for object_name, subobjects in node:

            container = stack and stack[-1] or None

            if self.canBecreated(object_name, container):

                factory_args = self.getFactoryArguments(line, object_name, container)
                factory = self.factories[object_name]
                urban_objects = factory.create(place=container, **factory_args)

                # if for some reasons the object creation went wrong, we skip this data line and continue the import
                if urban_objects is None:
                    return

                for obj in urban_objects:
                    # update some fields after creation
                    self.updateObjectFields(line, object_name, obj)

                    stack.append(obj)
                    self.createUrbanObjects(subobjects, line, stack)
                    stack.pop()

    def canBecreated(self, object_name, container):
        if not container:
            return True

        unrestricted_container = object_name not in self.allowed_containers
        allowed_container = self.allowed_containers.get(object_name, '') == container.portal_type

        canbecreated = unrestricted_container or allowed_container

        return canbecreated

    def getFactoryArguments(self, line, object_name, container):
        factory_args = {}
        for mapper in self.mappers[object_name]['pre']:
            factory_args.update(mapper.map(line, container=container))

        return factory_args

    def updateObjectFields(self, line, object_name, urban_object):
        for mapper in self.mappers[object_name]['post']:
            mapper.map(line, plone_object=urban_object, site=self.site)
        urban_object.processForm()

    def logError(self, error_location, line, message, data):

        error_message = zope.component.getMultiAdapter((self, error_location, line, message, data), IImportErrorMessage)
        message = str(error_message)
        print message

        line_num = self.current_line
        if line_num not in self.errors.keys():
            self.errors[line_num] = []
        self.errors[line_num].append(message)

        migration_step = error_location.__class__.__name__
        if migration_step not in self.sorted_errors.keys():
            self.sorted_errors[migration_step] = []
        self.sorted_errors[migration_step].append(message)

    def log(self, migrator_locals, location, message, factory_stack, data):
        pass

    def picklesErrorLog(self, filename='error_log.pickle', where='.'):
        current_directory = os.getcwd()
        os.chdir(where)

        i = 1
        new_filename = filename
        while filename in os.listdir('.'):
            i = i + 1
            new_filename = '%s - %i' % (filename, i)

        errors_export = open(new_filename, 'w')
        os.chdir(current_directory)
        errors = {
            'by_line': self.errors,
            'by_type': self.sorted_errors,
        }
        pickle.dump(errors, errors_export)

        print 'error log "%s" pickled in : %s' % (new_filename, os.getcwd())

        return new_filename