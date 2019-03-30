-- DONE
SELECT *
FROM (
  SELECT *
  FROM elements
  WHERE id in (

    -- General locator search
    SELECT id
    FROM elements
    WHERE $(LIKE_COMPARE)
  )
  OR id in (

    -- Tag Search
    SELECT element_id
    FROM map_tags
    WHERE tag_id in (
      SELECT id
      FROM tags
      WHERE $(TAG_COMPARE)
    )

    GROUP BY element_id
    HAVING COUNT(element_id) = $(COMPARE_COUNT)
  )
)
LIMIT $(LIMIT)
