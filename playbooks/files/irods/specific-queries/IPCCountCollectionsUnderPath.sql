WITH
	user_lookup AS (SELECT u.user_id AS user_id FROM r_user_main u WHERE u.user_name = ?),
	parent      AS (
		SELECT c.coll_id AS coll_id, c.coll_name AS coll_name
		FROM r_coll_main c
		WHERE c.coll_name = ?)
SELECT COUNT(*)
FROM r_coll_main c
	JOIN r_objt_access a ON c.coll_id = a.object_id
	JOIN r_user_main u ON a.user_id = u.user_id,
	user_lookup,
	parent
WHERE u.user_id = user_lookup.user_id
	AND c.parent_coll_name = parent.coll_name AND c.coll_type != 'linkPoint'