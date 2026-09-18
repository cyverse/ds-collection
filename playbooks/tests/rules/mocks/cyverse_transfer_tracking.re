# A stub implementation of cyverse_transfer_tracking.re used for unit testing.
# All rules write a message to the server log saying they were called.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


cyverse_transfer_tracking_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf) {
	writeLine('serverLog', 'cyverse_transfer_tracking_api_bulk_data_obj_put_post called');
}

cyverse_transfer_tracking_api_data_obj_get_post(
	*Instance, *Comm, *DataObjInp, *PORTAL_OPR, *DATA_OBJ_B_BUF
) {
	writeLine('serverLog', 'cyverse_transfer_tracking_api_data_obj_get_post called');
}

cyverse_transfer_tracking_api_data_obj_put_post(
	*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR
) {
	writeLine('serverLog', 'cyverse_transfer_tracking_api_data_obj_put_post called');
}

cyverse_transfer_tracking_api_data_obj_read_post(
	*Instance, *Comm, *DataObjReadInp, *DATA_OBJ_READ_B_BUF
) {
	writeLine('serverLog', 'cyverse_transfer_tracking_api_data_obj_read_post called');
}

cyverse_transfer_tracking_api_data_obj_write_post(
	*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf
) {
	writeLine('serverLog', 'cyverse_transfer_tracking_api_data_obj_write_post');
}
