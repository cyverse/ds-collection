WITH
	user_lookup AS (SELECT u.user_id AS user_id FROM r_user_main u WHERE u.user_name = ?),
	parent      AS (
		SELECT c.coll_id AS coll_id, c.coll_name AS coll_name
		FROM r_coll_main c
		WHERE c.coll_name = ?)
SELECT p.full_path, p.base_name, p.data_size, p.create_ts, p.modify_ts, p.access_type_id, p.type
FROM (
	SELECT
			c.coll_name                       AS dir_name,
			c.coll_name || '/' || d.data_name AS full_path,
			d.data_name                       AS base_name,
			d.create_ts                       AS create_ts,
			d.modify_ts                       AS modify_ts,
			'dataobject'                      AS type,
			d.data_size                       AS data_size,
			a.access_type_id                  AS access_type_id
		FROM r_data_main d
			JOIN r_coll_main c ON c.coll_id = d.coll_id
			JOIN r_objt_access a ON d.data_id = a.object_id
			JOIN r_user_main u ON a.user_id = u.user_id,
			user_lookup,
			parent
		WHERE u.user_id = user_lookup.user_id AND c.coll_id = parent.coll_id
	UNION SELECT
			c.parent_coll_name                     AS dir_name,
			c.coll_name                            AS full_path,
			regexp_replace(c.coll_name, '.*/', '') AS base_name,
			c.create_ts                            AS create_ts,
			c.modify_ts                            AS modify_ts,
			'collection'                           AS type,
			0                                      AS data_size,
			a.access_type_id                       AS access_type_id
		FROM r_coll_main c
			JOIN r_objt_access a ON c.coll_id = a.object_id
			JOIN r_user_main u ON a.user_id = u.user_id,
			user_lookup,
			parent
		WHERE u.user_id = user_lookup.user_id
			AND c.parent_coll_name = parent.coll_name AND c.coll_type != 'linkPoint'
) AS p
ORDER BY p.type ASC, p.full_path ASC
LIMIT ?
OFFSET ?