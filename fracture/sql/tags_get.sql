SELECT tag
FROM tags
WHERE id IN (
    SELECT tag_id
    FROM map_tags
    WHERE element_id = (
        SELECT id
        FROM elements
        WHERE identifier='$(IDENTIFIER)'
    )
)
