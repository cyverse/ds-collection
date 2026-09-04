# A stub implementation of cyverse_transfer_tracking.re used for unit testing.
# All rules write a message to the server log saying they were called.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


cyverse_transfer_tracking_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf) {
	*msg = "cyverse_transfer_tracking_api_bulk_data_obj_put_post("
		++ "*Instance, Comm, BulkOpInp, BulkOpInpBBuf)"
		++ " called";

	writeLine('serverLog', *msg);
}

cyverse_transfer_tracking_api_data_obj_get_post(
	*Instance, *Comm, *DataObjInp, *PORTAL_OPR, *DATA_OBJ_B_BUF
) {
	*msg = "cyverse_transfer_tracking_api_data_obj_get_post("
		++ "*Instance, Comm, DataObjInp, PORTAL_OPR, DATA_OBJ_B_BUF)"
		++ " called";

	writeLine('serverLog', *msg);
}

cyverse_transfer_tracking_api_data_obj_put_post(
	*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR
) {
	*msg = "cyverse_transfer_tracking_api_data_obj_put_post("
		++ "*Instance, Comm, DataObjInp, DataObjInpBBuf, PORTAL_OPR)"
		++ " called";

	writeLine('serverLog', *msg);
}

cyverse_transfer_tracking_api_data_obj_read_post(
	*Instance, *Comm, *DataObjReadInp, *DATA_OBJ_READ_B_BUF
) {
	*msg = "cyverse_transfer_tracking_api_data_obj_read_post("
		++ "*Instance, Comm, DataObjReadInp, DATA_OBJ_READ_B_BUF)"
		++ " called";

	writeLine('serverLog', *msg);
}

cyverse_transfer_tracking_api_data_obj_write_post(
	*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf
) {
	*msg = "cyverse_transfer_tracking_api_data_obj_write_post("
		++ "*Instance, Comm, DataObjWriteInp, DataObjWriteInpBBuf)"
		++ " called";

	writeLine('serverLog', *msg);
}

cyverse_logic_api_replica_open_post(*Instance, *Comm, *DataObjInp, *JSON_OUTPUT) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_replica_open_post(*Instance, Comm, DataObjInp, JSON_OUTPUT) called" );
}

cyverse_transfer_tracking_api_replica_close_post(*Instance, *Comm, *JsonInput) {
	writeLine(
		'serverLog',
		"cyverse_logic_api_replica_close_post(*Instance, Comm, *JsonInput) called" );
}