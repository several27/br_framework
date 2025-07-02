WITH Macro_1 AS (

  {{ br_framework.snowflake_unpivot(relation =  ref('for_unpivot')) }}

)

SELECT *

FROM Macro_1
