{% macro set_query_tag_for_dataset() -%}
    
    {{ log("Setting query_tag to PROPHECY_TAG") }}
    {% do run_query("alter session set query_tag = PROPHECY_TAG") %}
        
{% endmacro %}