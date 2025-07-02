WITH for_unpivot AS (

  SELECT * 
  
  FROM {{ ref('for_unpivot')}}

),

SnowflakeUnpivot_1 AS (

  {{ br_framework.SnowflakeUnpivot( ref('for_unpivot'), 'key', 'value', 'string', ['ID'], [], "") }}

)

SELECT *

FROM SnowflakeUnpivot_1
