{% macro SnowflakeUnpivot(
    relation = ref('test_data'),
    field_name='key',
    value_name='value',
    cast_to='string',
    exclude=['ID'],
    remove=[],
    where_condition=None
) %}
  
  {# ──────────────────────────────────────────────────────────────
     1. Get all column names for the relation
     ─────────────────────────────────────────────────────────── #}
  {% set cols_query %}
    select column_name
    from {{ relation.database }}.information_schema.columns
    where table_schema = '{{ relation.schema.upper() }}'
      and table_name   = '{{ relation.identifier.upper() }}'
  {% endset %}

  {% set results = run_query(cols_query) %}
  {% if execute %}
    {% set columns = results.columns[0].values() %}
  {% else %}
    {% set columns = [] %}
  {% endif %}

  {# ──────────────────────────────────────────────────────────────
     2. Build the list of columns to UNPIVOT
     ─────────────────────────────────────────────────────────── #}
  {% set unpivot_columns = [] %}
  {% for col in columns %}
    {% if col.upper() not in exclude and col.upper() not in remove %}
      {% do unpivot_columns.append(col.upper()) %}
    {% endif %}
  {% endfor %}

  {# ──────────────────────────────────────────────────────────────
     3. Select + optional filter (sub-query) ➜ UNPIVOT
     ─────────────────────────────────────────────────────────── #}
  select *
  from (
      select *
      from {{ relation }}
      {% if where_condition %}
        where {{ where_condition }}   {# filter runs *before* unpivot #}
      {% endif %}
  ) src
  unpivot (
      {{ value_name }} for {{ field_name }}
      in ({{ unpivot_columns | join(', ') }})
  )

{% endmacro %}