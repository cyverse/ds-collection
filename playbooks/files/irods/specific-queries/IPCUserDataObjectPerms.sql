SELECT DISTINCT o.access_type_id, u.user_name
FROM r_user_main u, r_data_main d, r_coll_main c, r_tokn_main t, r_objt_access o
WHERE c.coll_name = ?
	AND d.data_name = ?
	AND c.coll_id = d.coll_id
	AND o.object_id = d.data_id
	AND t.token_namespace = 'access_type'
	AND u.user_id = o.user_id
	AND o.access_type_id = t.token_id
LIMIT ?
OFFSET ?