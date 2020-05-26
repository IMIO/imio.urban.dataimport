# -*- coding: utf-8 -*-

from imio.urban.dataimport.config import IMPORT_FOLDER_PATH
from imio.urban.dataimport.csv.interfaces import ICSVMapper
from imio.urban.dataimport.exceptions import NoObjectToCreateException
from imio.urban.dataimport.mapper import BaseMapper
from imio.urban.dataimport.mapper import FinalMapper
from imio.urban.dataimport.mapper import Mapper
from imio.urban.dataimport.mapper import PostCreationMapper
from imio.urban.dataimport.mapper import SimpleMapper

from zope.interface import implements

import csv


class CSVBaseMapper(BaseMapper):

    implements(ICSVMapper)

    def __init__(self, csv_importer, args, csv_filename=None, key_column=None):
        super(CSVBaseMapper, self).__init__(csv_importer, args)
        self.csv_filename = csv_filename or self.importer.csv_filename
        self.key_column = key_column or self.importer.key_column


class CSVMapper(CSVBaseMapper, Mapper):
    """ """


class CSVSimpleMapper(CSVBaseMapper, SimpleMapper):
    """ """


class CSVPostCreationMapper(CSVMapper, PostCreationMapper):
    """" """


class CSVFinalMapper(CSVMapper, FinalMapper):
    """" """


class JoinTableMapper(CSVMapper):
    """
    """

    def __init__(self, csv_importer, args):
        args['from'] = args.get('from', [k for k in args['KEYS']])
        args['to'] = args.get('to', [])
        super(JoinTableMapper, self).__init__(csv_importer, args)
        self.secondary_table = args['table']
        self.key = args['KEYS']
        self.key_column = self.key[1]
        self.lines = self._extract_by_key(self.secondary_table, self.key_column)

    def get_csv_filename(self):
        return self.csv_filename

    def _extract_by_key(self, csv_filename, key_name):
        """
        """
        csv_filepath = '{}/{}.csv'.format(IMPORT_FOLDER_PATH, csv_filename)
        csv_file = open(csv_filepath)
        delimiter = getattr(self.importer, 'delimiter', ';')
        quotechar = getattr(self.importer, 'quotechar', '"')
        escapechar = getattr(self.importer, 'escapechar', '\\')
        lines = csv.reader(csv_file, delimiter=delimiter, quotechar=quotechar, escapechar=escapechar)
        header = lines.next()
        key_index = header.index(key_name)
        lines_by_key = {}
        for line in lines:
            key = line[key_index]
            if key not in lines_by_key:
                lines_by_key[key] = [line]
            else:
                lines_by_key[key].append(line)

        return lines_by_key

    def query_secondary_table(self, line):
        key_value = self.getData(self.key[0], line)
        return self.lines.get(key_value, [])


class MultivaluedFieldSecondaryTableMapper(JoinTableMapper):
    """ """

    def map(self, line, **kwargs):
        mapped = {}
        self.main_line = line
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for dest in self.destinations:
                mapping_method = 'map%s' % dest.capitalize()
                if hasattr(self, mapping_method):
                    result = getattr(self, mapping_method)(secondary_line)
                    if dest in mapped:
                        mapped[dest].extend(result)
                    else:
                        mapped[dest] = result
                else:
                    print ('%s: NO MAPPING METHOD FOUND' % self)
                    print ('target field : %s' % dest)
        for k, v in mapped.iteritems():
            mapped[k] = list(set(v))
        return mapped


class SecondaryTableMapper(JoinTableMapper):

    def __init__(self, csv_importer, args):
        super(SecondaryTableMapper, self).__init__(csv_importer, args)
        self.mappers = self._setMappers(args['mappers'])

    def _setMappers(self, mappers_dscr):
        mappers = []
        for mapper_class, mapper_args in mappers_dscr.iteritems():
            if ICSVMapper.implementedBy(mapper_class):
                mapper = mapper_class(self.importer, mapper_args, csv_filename=self.secondary_table)
            else:
                mapper = mapper_class(self.importer, mapper_args)
            setattr(mapper, 'key_column', self.key_column)
            mappers.append(mapper)
        return mappers

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for mapper in self.mappers:
                objects_args.update(mapper.map(secondary_line, **kwargs))
            break
        return objects_args


class MultiLinesSecondaryTableMapper(SecondaryTableMapper):

    def map(self, line, **kwargs):
        all_objects_args = []
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            object_args = {}
            skip = False
            for mapper in self.mappers:
                mapper.line = secondary_line
                try:
                    object_args.update(mapper.map(secondary_line, **kwargs))
                except NoObjectToCreateException:
                    skip = True
                    break
            if not skip:
                all_objects_args.append(object_args)
        return all_objects_args
