SELECT a.access_type_id, u.user_name
FROM r_coll_main c
	JOIN r_objt_access a ON c.coll_id = a.object_id
	JOIN r_user_main u ON a.user_id = u.user_id
WHERE c.parent_coll_name = ? AND c.coll_name = ?
LIMIT ?
OFFSET ?