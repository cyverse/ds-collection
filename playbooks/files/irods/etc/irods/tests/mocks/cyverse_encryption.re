# A stub implementation of cyverse_encryption.re for unit testing. All rules
# write a message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

ipcEncryption_api_coll_create_post(*Instance, *Comm, *CollCreateInp) {
	writeLine('serverLog', "ipcEncryption_api_coll_create_post called");
}

ipcEncryption_api_data_obj_copy_pre(*Instance, *Comm, *DataObjCopyInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_copy_pre called");
}

ipcEncryption_api_data_obj_create_and_stat_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_create_and_stat_pre called");
}

ipcEncryption_api_data_obj_create_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_create_pre called");
}

ipcEncryption_api_data_obj_open_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_open_pre called");
}

ipcEncryption_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_put_pre called");
}

ipcEncryption_api_data_obj_rename_pre(*Instance, *Comm, *DataObjRenameInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_rename_pre called");
}

ipcEncryption_api_data_obj_rename_post(*Instance, *Comm, *DataObjRenameInp) {
	writeLine('serverLog', "ipcEncryption_api_data_obj_rename_post called");
}

ipcEncryption_api_struct_file_ext_and_reg_pre(*Instance, *Comm, *StructFileExtAndRegInp) {
	writeLine('serverLog', "ipcEncryption_api_struct_file_ext_and_reg_pre called");
}
