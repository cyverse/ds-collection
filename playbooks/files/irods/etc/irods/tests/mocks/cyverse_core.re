# A stub implementation of cyverse_encryption.re for unit testing. All rules
# write a message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

pep_api_data_obj_copy_pre(*Instance, *Comm, *DataObjCopyInp, *TransStat) {
	writeLine('serverLog', "cyverse_core: pep_api_data_obj_copy_pre called");
}

pep_api_data_obj_put_pre(*Instance, *Comm, *DataObjInp, *DataObjInpBBuf, *PORTAL_OPR_OUT) {
	writeLine('serverLog', "cyverse_core: pep_api_data_obj_put_pre called");
}
