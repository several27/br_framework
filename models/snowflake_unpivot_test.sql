WITH Macro_1 AS (

  {{ br_framework.snowflake_unpivot(relation = 'maciej.public.for_unpivot') }}

)

SELECT *

FROM Macro_1
