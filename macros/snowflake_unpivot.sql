{% macro snowflake_unpivot(
    relation,
    field_name='key',
    value_name='value',
    cast_to='string',
    exclude=['ID'],
    remove=[],
    where_condition=None
) %}
  
  {{ log("relation: " ~ relation, info=True) }}
  {{ log("relation.db: " ~ relation.database, info=True) }}
  {{ log("relation.sc: " ~ relation.schema, info=True) }}
  {{ log("relation.id: " ~ relation.identifier, info=True) }}

  {% set cols_query %}
    select column_name
    from {{ relation.database }}.information_schema.columns
    where table_schema = '{{ relation.schema.upper() }}'
      and table_name = '{{ relation.identifier.upper() }}'
  {% endset %}
  {% set results = run_query(cols_query) %}
  
  {% if execute %} 
    {% set columns = results.columns[0].values() %}
  {% else %}
    {% set columns = [] %}
  {% endif %}
  
  {% set unpivot_columns = [] %}

  {% for col in columns %}
    {% if col not in exclude and col not in remove %}
      {% do unpivot_columns.append(col) %}
    {% endif %}
  {% endfor %}

  select *
  from {{ relation }}
  {{ "where " ~ where_condition if where_condition }}
  unpivot (
    {{ value_name }} for {{ field_name }}
    in ({{ unpivot_columns | join(', ') }})
  )
{% endmacro %}