DELETE FROM map_tags
WHERE element_id = (
    SELECT id
    FROM elements
    WHERE identifier='$(IDENTIFIER)'
);
DELETE FROM map_dependencies
WHERE element_id = (
    SELECT id
    FROM elements
    WHERE identifier='$(IDENTIFIER)'
)
OR requirement_id = (
    SELECT id
    FROM elements
    WHERE identifier='$(IDENTIFIER)'
);
DELETE FROM elements
WHERE identifier='$(IDENTIFIER)';
