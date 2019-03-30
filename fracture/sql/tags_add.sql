INSERT INTO tags (tag)
SELECT '$(TAG)'
WHERE NOT EXISTS(
  SELECT 1 FROM tags WHERE tag='$(TAG)'
);

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
WHERE NOT EXISTS (
  SELECT * FROM map_tags
  WHERE element_id=(
    SELECT id as eid
    FROM elements
    WHERE identifier='$(IDENTIFIER)'
    LIMIT 1
  )
        AND tag_id=(
    SELECT id as tid
    FROM tags
    WHERE tag='$(TAG)'
    LIMIT 1
  )
);
