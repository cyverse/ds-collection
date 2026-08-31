# A stub implementation of cyverse_repl.re for unit testing. All rules
# write a message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

cyverse_repl_acSetRescSchemeForCreate(*DataPath) {
	writeLine('serverLog', 'cyverse_repl_acSetRescSchemeForCreate(*DataPath) called');
	msiSetDefaultResc('ingestRes', '');
}

cyverse_repl_acSetRescSchemeForRepl(*DataPath) {
	writeLine('serverLog', 'cyverse_repl_acSetRescSchemeForRepl(*DataPath) called');
	msiSetDefaultResc('replRes', '');
}

cyverse_repl_api_bulk_data_obj_put_post(*Instance, *Comm, *BulkOpInp, *BulkOpInpBBuf) {
	writeLine(
		'serverLog',
		'cyverse_repl_api_bulk_data_obj_put_post(*Instance, Comm, BulkOpInp, BulkOpInpBBuf) called' );
}

cyverse_repl_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	writeLine(
		'serverLog',
		'cyverse_repl_api_data_obj_copy_post(*Instance, Comm, DataObjCopyInp, TransStat) called' );
}

cyverse_repl_api_data_obj_put_post(
	*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT
) {
	*msg = 'cyverse_repl_api_data_obj_put_post('
		++ '*Instance, Comm, DataObjInp, DataObjInpBBuf, PORTAL_OPR_OUT)'
		++ ' called';

	writeLine('serverLog', *msg);
}

cyverse_repl_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
	writeLine(
		'serverLog',
		'cyverse_repl_api_data_obj_rename_post(*Instance, Comm, DataObjRenameInp) called' );
}

cyverse_repl_api_phy_path_reg_post(*Instance, *Comm, *PhyPathRegInp) {
	writeLine(
		'serverLog', 'cyverse_repl_api_phy_path_reg_post(*Instance, Comm, PhyPathRegInp) called' );
}

cyverse_repl_api_touch_post(*Instance, *Comm, *JsonInput) {
	writeLine('serverLog', 'cyverse_repl_api_touch_post(*Instance, Comm, JsonInput) called');
}

cyverse_repl_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) {
	writeLine(
		'serverLog', 'cyverse_repl_api_data_obj_create_post(*Instance, Comm, DataObjInp) called' );
}

cyverse_repl_api_data_obj_open_post(*Instance, *Comm, *DataObjInp) {
	writeLine(
		'serverLog', 'cyverse_repl_api_data_obj_open_post(*Instance, Comm, DataObjInp) called' );
}

cyverse_repl_api_data_obj_write_post(*Instance, *Comm, *DataObjWriteInp, *DataObjWriteInpBBuf) {
	*msg = 'cyverse_repl_api_data_obj_write_post('
		++ '*Instance, Comm, DataObjWriteInp, DataObjWriteInpBBuf)'
		++ ' called';

	writeLine('serverLog', *msg);
}

cyverse_repl_api_data_obj_close_post(*Instance, *Comm, *DataObjCloseInp) {
	writeLine(
		'serverLog',
		'cyverse_repl_api_data_obj_close_post(*Instance, Comm, DataObjCloseInp) called' );
}

cyverse_repl_api_replica_open_post(*Instance, *Comm, *DataObjInp, *JSON_OUTPUT) {
	writeLine(
		'serverLog',
		'cyverse_repl_api_replica_open_post(*Instance, Comm, DataObjInp, JSON_OUTPUT) called' );
}

cyverse_repl_api_replica_close_post(*Instance, *Comm, *JsonInput) {
	writeLine('serverLog', 'cyverse_repl_api_replica_close_post(*Instance, Comm, JsonInput) called');
}

cyverse_repl_dataObjCreated(*User, *Zone, *DataObjInfo) {
	writeLine('serverLog', 'cyverse_repl_dataObjCreated(*User, *Zone, DataObjInfo) called');
}
