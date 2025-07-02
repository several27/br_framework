{% macro snowflake_unpivot(
    relation,
    unpivot_columns = ['CA', 'NY', 'WA'],
    field_name = 'key',
    value_name = 'value',
    cast_to='string',
    exclude=['id'],
    remove=[],
    where_condition=None
) %}
  {{
    log("Running snowflake_unpivot for: " ~ relation, info=True)
  }}

  select *
  from maciej.public.for_unpivot
  {{ "where " ~ where_condition if where_condition }}
  unpivot (
    {{ value_name }} for {{ field_name }}
    in ({{ unpivot_columns | join(', ') }})
  )
{% endmacro %}