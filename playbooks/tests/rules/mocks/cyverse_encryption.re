# A stub implementation of cyverse_encryption.re for unit testing. All rules
# write a message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

cyverse_encryption_api_coll_create_post(*Instance, *Comm, *CollCreateInp) {
	writeLine('serverLog', "cyverse_encryption_api_coll_create_post called");
}

cyverse_encryption_api_data_obj_copy_pre(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_copy_pre called");
}

cyverse_encryption_api_data_obj_create_and_stat_pre(*Instance, *Comm, *DataObjInp, *OpenStat) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_create_and_stat_pre called");
}

cyverse_encryption_api_data_obj_create_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_create_pre called");
}

cyverse_encryption_api_data_obj_open_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_open_pre called");
}

cyverse_encryption_api_data_obj_open_and_stat_pre(*Instance, *Comm, *DataObjInp, *OpenStat) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_open_pre called");
}

cyverse_encryption_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_put_pre called");
}

cyverse_encryption_api_data_obj_rename_pre(*Instance, *Comm, *DataObjRenameInp) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_rename_pre called");
}

cyverse_encryption_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
	writeLine('serverLog', "cyverse_encryption_api_data_obj_rename_post called");
}

cyverse_encryption_api_struct_file_ext_and_reg_pre(*Instance, *Comm, *StructFileExtAndRegInp) {
	writeLine('serverLog', "cyverse_encryption_api_struct_file_ext_and_reg_pre called");
}
