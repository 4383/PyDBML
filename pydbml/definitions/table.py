import pyparsing as pp

from pydbml.parser.blueprints import TableBlueprint

from .column import table_column
from .common import _
from .common import _c
from .common import end
from .common import note
from .common import note_object
from .generic import name
from .index import indexes

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

alias = pp.WordStart() + pp.Literal('as').suppress() - pp.WordEnd() - name


hex_char = pp.Word(pp.srange('[0-9a-fA-F]'), exact=1)
hex_color = ("#" - (hex_char * 3 ^ hex_char * 6)).leaveWhitespace()
header_color = (
    pp.CaselessLiteral('headercolor:').suppress() + _
    - pp.Combine(hex_color)('header_color')
)
table_setting = _ + (note('note') | header_color) + _
table_settings = '[' + table_setting + (',' + table_setting)[...] + ']'


def parse_table_settings(s, l, t):
    '''
    [headercolor: #cccccc, note: 'note']
    '''
    result = {}
    if 'note' in t:
        result['note'] = t['note']
    if 'header_color' in t:
        result['header_color'] = t['header_color']
    return result


table_settings.setParseAction(parse_table_settings)


note_element = note | note_object

table_element = _ + (note_element('note') | indexes('indexes')) + _

table_body = table_column[1, ...]('columns') + _ + table_element[...]

table_name = (name('schema') + '.' + name('name')) | (name('name'))

table = _c + (
    pp.CaselessLiteral("table").suppress()
    + table_name
    + alias('alias')[0, 1]
    + table_settings('settings')[0, 1] + _
    + '{' - table_body + _ + '}'
) + end


def parse_table(s, l, t):
    '''
    Table bookings as bb [headercolor: #cccccc] {
      id integer
      country varchar [NOT NULL, ref: > countries.country_name]
      booking_date date unique pk
      created_at timestamp

      indexes {
          (id, country) [pk] // composite primary key
      }
    }
    '''
    init_dict = {
        'name': t['name'],
    }
    if 'schema' in t:
        init_dict['schema'] = t['schema']
    if 'settings' in t:
        init_dict.update(t['settings'])
    if 'alias' in t:
        init_dict['alias'] = t['alias'][0]
    if 'note' in t:
        # will override one from settings
        init_dict['note'] = t['note'][0]
    if 'indexes' in t:
        init_dict['indexes'] = t['indexes']
    if 'columns' in t:
        init_dict['columns'] = t['columns']
    if'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment
    result = TableBlueprint(**init_dict)

    return result


table.setParseAction(parse_table)
