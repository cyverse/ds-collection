# A stub implementation of cyverse_trash.re for unit testing. All rules write a
# message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

cyverse_trash_api_data_obj_unlink_pre(*Instance, *Comm, *DataObjUnlinkInp) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_unlink_pre called");
}

cyverse_trash_api_data_obj_unlink_post(*Instance, *Comm, *DataObjUnlinkInp) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_unlink_post called");
}

cyverse_trash_api_data_obj_unlink_except(*Instance, *Comm, *DataObjUnlinkInp) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_unlink_except called");
}

cyverse_trash_api_data_obj_put_post(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PortalOprOut) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_put_post called");
}

cyverse_trash_api_rm_coll_pre(*Instance, *Comm, *RmCollInp, *CollOprStat) {
	writeLine('serverLog', "cyverse_trash_api_rm_coll_pre called");
}

cyverse_trash_api_rm_coll_except(*Instance, *Comm, *RmCollInp, *CollOprStat) {
	writeLine('serverLog', "cyverse_trash_api_rm_coll_except called");
}

cyverse_trash_api_coll_create_post(*Instance, *Comm, *CollCreateInp) {
	writeLine('serverLog', "cyverse_trash_api_coll_create_post called");
}

cyverse_trash_api_data_obj_rename_pre(*Instance, *Comm, *DataObjRenameInp) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_rename_pre called");
}

cyverse_trash_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_rename_post called");
}

cyverse_trash_api_data_obj_copy_post(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_copy_post called");
}

cyverse_trash_api_data_obj_create_post(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "cyverse_trash_api_data_obj_create_post called");
}