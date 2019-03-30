DELETE FROM map_tags
WHERE element_id IN (
  SELECT id
  FROM elements
  WHERE identifier='$(IDENTIFIER)'
)
AND tag_id IN (
  SELECT id
  FROM tags
  WHERE tag='$(TAG)'
);
