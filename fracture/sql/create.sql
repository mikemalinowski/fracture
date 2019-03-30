CREATE TABLE elements
(
    id INTEGER PRIMARY KEY,
    identifier TEXT NOT NULL
);
CREATE UNIQUE INDEX elements_identifier_uindex ON elements (identifier);

CREATE TABLE tags
(
    id INTEGER PRIMARY KEY,
    tag TEXT NOT NULL
);

CREATE UNIQUE INDEX tags_id_uindex ON tags (id);
CREATE UNIQUE INDEX tags_tag_uindex ON tags (tag);

CREATE TABLE map_tags
(
    element_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY(element_id, tag_id),
    CONSTRAINT map_tags_element_id_fk FOREIGN KEY (element_id) REFERENCES elements (id),
    CONSTRAINT map_tags_tags_id_fk FOREIGN KEY (tag_id) REFERENCES tags (id)
);

CREATE TABLE settings
(
  id INTEGER PRIMARY KEY,
  settings TEXT UNIQUE
);

INSERT into settings (settings)
VALUES ("{}")
