# A stub implementation of coge.re used for unit testing. All rules write a
# message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

coge_acPostProcForCollCreate(*CollPath) {
	writeLine('serverLog', "coge_acPostProcForCollCreate(*CollPath) called");
}

coge_acPostProcForObjRename(*SrcEntity, *DestEntity) {
	writeLine("serverLog", "coge_acPostProcForObjRename(*SrcEntity, *DestEntity) called");
}

coge_dataObjCreated(*User, *Zone, *DataObjInfo) {
	writeLine("serverLog", "coge_dataObjCreated(*User, *Zone, DataObjInfo) called");
}