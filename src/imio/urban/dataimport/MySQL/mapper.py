# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import BaseMapper, Mapper, SimpleMapper,\
    PostCreationMapper, FinalMapper, SimpleStringMapper
from imio.urban.dataimport.MySQL.interfaces import IMySQLMapper
from imio.urban.dataimport.exceptions import NoObjectToCreateException


from zope.interface import implements


class MySQLBaseMapper(BaseMapper):

    implements(IMySQLMapper)

    def __init__(self, MySQL_importer, args, table_name=None):
        super(MySQLBaseMapper, self).__init__(MySQL_importer, args)
        self.db_name = self.importer.db_name
        self.table_name = table_name or self.importer.table_name

    def getData(self, valuename, line=''):
        data = super(MySQLBaseMapper, self).getData(valuename, line)
        if data and type(data) is str:
            data = data.decode('iso-8859-1')
        return data


class MySQLMapper(MySQLBaseMapper, Mapper):
    """ """


class MySQLSimpleMapper(MySQLBaseMapper, SimpleMapper):
    """ """


class MySQLSimpleStringMapper(MySQLBaseMapper, SimpleStringMapper):
    """ """


class MySQLPostCreationMapper(MySQLMapper, PostCreationMapper):
    """" """


class MySQLFinalMapper(MySQLMapper, FinalMapper):
    """" """


class SubQueryMapper(MySQLMapper):

    def __init__(self, mysql_importer, args):
        super(SubQueryMapper, self).__init__(mysql_importer, args)
        self.table = args['table']
        self.query = self.init_query(self.table)

    def init_query(self, table):
        datasource = self.importer.datasource
        query = datasource.session.query(datasource.get_table(table))
        return query


class SecondaryTableMapper(SubQueryMapper):

    def __init__(self, mysql_importer, args):
        args['from'] = args.get('from', [args['KEYS']])
        args['to'] = args.get('to', [])
        super(SecondaryTableMapper, self).__init__(mysql_importer, args)
        self.key = args['KEYS']
        self.key_column = self.key[1]
        self.mappers = self._setMappers(args.get('mappers', {}))

    def _setMappers(self, mappers_dscr):
        mappers = []
        for mapper_class, mapper_args in mappers_dscr.iteritems():
            if IMySQLMapper.implementedBy(mapper_class):
                mapper = mapper_class(self.importer, mapper_args, table_name=self.table)
            else:
                mapper = mapper_class(self.importer, mapper_args)
            setattr(mapper, 'key_column', self.key_column)
            mappers.append(mapper)
        return mappers

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query_secondary_table(line)
        if lines:
            secondary_line = lines[0]
            for mapper in self.mappers:
                mapper.line = secondary_line
                objects_args.update(mapper.map(secondary_line, **kwargs))
        else:
            raise NoObjectToCreateException
        return objects_args

    def query_secondary_table(self, line):
        lines = self.query.filter_by(**{self.key[1]: self.getData(self.key[0], line=line)}).all()
        return lines


class MultiLinesSecondaryTableMapper(SecondaryTableMapper):

    def map(self, line, **kwargs):
        objects_args = []
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for mapper in self.mappers:
                mapper.line = secondary_line
                objects_args.append(mapper.map(line, **kwargs))
        return objects_args


class FieldMultiLinesSecondaryTableMapper(SecondaryTableMapper):

    def map(self, line, **kwargs):
        mapped = {}
        lines = self.query_secondary_table(line)
        for dest in self.destinations:
            values = []
            for secondary_line in lines:
                mapping_method = 'map%s' % dest.capitalize()
                if hasattr(self, mapping_method):
                    value = getattr(self, mapping_method)(secondary_line)
                    if value not in values:
                        values.append(value)
                else:
                    print ('NO MAPPING METHOD FOUND' % self)
                    print ('target field : %s' % dest)
            mapped[dest] = values
        return mapped
