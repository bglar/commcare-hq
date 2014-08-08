from jsonobject import JsonObject, StringProperty
from sqlagg import SumColumn
from sqlagg.columns import SimpleColumn
from corehq.apps.reports.sqlreport import DatabaseColumn
from corehq.apps.reports_core.filters import DatespanFilter
from corehq.apps.userreports.exceptions import BadSpecError
from corehq.apps.userreports.reports.data_source import ConfigurableReportDataSource


def _build_date_filter(spec):
    # todo: flesh out / clean up
    return DatespanFilter(
        name=spec['slug'],
        required=spec.get('required', False),
    )


class ReportFilterFactory(object):
    constructor_map = {
        'date': _build_date_filter,
    }

    @classmethod
    def from_spec(cls, spec):
        return cls.constructor_map[spec['type']](spec)

    @classmethod
    def validate_spec(self, spec):
        if spec['type'] not in self.constructor_map:
            raise BadSpecError(_('Illegal report filter type: "{0}", must be one of the following choice: ({1})'.format(
                spec['type'],
                ', '.join(self.constructor_map.keys())
            )))


class ReportFactory(object):

    @classmethod
    def from_spec(cls, spec):
        # todo: validation and what not
        return ConfigurableReportDataSource(
            domain=spec['domain'],
            table_id=spec['table_id'],
            aggregation_columns=spec['aggregation_columns'],
            columns=[ReportColumnFactory.from_spec(colspec) for colspec in spec['columns']],
        )

class ReportColumnFactory(object):

    @classmethod
    def from_spec(cls, spec):
        # todo: type convert to runtime object
        return ReportColumn.wrap(spec)


class ReportColumn(JsonObject):
    type = StringProperty(required=True)
    display = StringProperty()
    field = StringProperty(required=True)
    aggregation = StringProperty(required=True)

    def get_sql_column(self):
        # todo: find a better home for this
        sqlagg_column_map = {
            'sum': SumColumn,
            'simple': SimpleColumn,
        }
        return DatabaseColumn(self.display, sqlagg_column_map[self.aggregation](self.field),
                              sortable=False, data_slug=self.field)
