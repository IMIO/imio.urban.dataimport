# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import BaseMapper, Mapper, SimpleMapper,\
    PostCreationMapper, FinalMapper
from imio.urban.dataimport.exceptions import NoObjectToCreateException
from imio.urban.dataimport.access.interfaces import IAccessMapper

from zope.interface import implements

import subprocess
import csv


class AccessBaseMapper(BaseMapper):

    implements(IAccessMapper)

    def __init__(self, access_importer, args, table_name=None):
        super(AccessBaseMapper, self).__init__(access_importer, args)
        self.db_path = self.importer.db_path
        self.table_name = table_name or self.importer.table_name


class AccessMapper(AccessBaseMapper, Mapper):
    """ """


class AccessSimpleMapper(AccessBaseMapper, SimpleMapper):
    """ """


class AccessPostCreationMapper(AccessMapper, PostCreationMapper):
    """" """


class AccessFinalMapper(AccessMapper, FinalMapper):
    """" """


class SubQueryMapper(AccessMapper):

    def _query(self, query, withheader=False):
        table = subprocess.Popen(['mdb-sql', self.db_path, '-p', '-d', ';'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        temp = open('temp', 'w')
        pos = withheader and 1 or 2
        temp.write('\n'.join(table.communicate(query)[0].split('\n')[pos:-2]))
        temp = open('temp', 'r')
        result = csv.reader(temp, delimiter=';')
        return result


class JoinTableMapper(AccessMapper):
    """
    """

    def __init__(self, access_importer, args):
        args['from'] = args.get('from', [k for k in args['KEYS']])
        args['to'] = args.get('to', [])
        super(JoinTableMapper, self).__init__(access_importer, args)
        self.secondary_table = args['table']
        self.key = args['KEYS']
        self.key_column = self.key[1]
        self.lines = self._extract_by_key(self.secondary_table, self.key_column)

    def get_db_path(self):
        return self.db_path

    def _extract_by_key(self, table, key_name):
        """
        """
        command_line = ['mdb-export', self.get_db_path(), table, '-d', ';']
        csv_export = subprocess.Popen(command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        lines = csv.reader(csv_export.stdout, delimiter=';')
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
        return mapped


class SecondaryTableMapper(JoinTableMapper):

    def __init__(self, access_importer, args):
        super(SecondaryTableMapper, self).__init__(access_importer, args)
        self.mappers = self._setMappers(args['mappers'])

    def _setMappers(self, mappers_dscr):
        mappers = []
        for mapper_class, mapper_args in mappers_dscr.iteritems():
            if IAccessMapper.implementedBy(mapper_class):
                mapper = mapper_class(self.importer, mapper_args, table_name=self.secondary_table)
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
        objects_args = []
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
                objects_args.append(object_args)
        return objects_args
