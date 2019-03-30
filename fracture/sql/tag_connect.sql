INSERT INTO
  map_tags(element_id, tag_id)
SELECT
    (
    SELECT id as eid
    FROM elements
    WHERE identifier='$(IDENTIFIER)'
    LIMIT 1
  ),
  (
    SELECT id as tid
    FROM tags
    WHERE tag='$(TAG)'
    LIMIT 1
  )
