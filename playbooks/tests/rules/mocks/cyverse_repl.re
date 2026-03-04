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

cyverse_repl_dataObjCreated(*User, *Zone, *DataObjInfo) {
	writeLine('serverLog', 'cyverse_repl_dataObjCreated(*User, *Zone, DataObjInfo) called');
}

cyverse_repl_dataObjModified(*User, *Zone, *DataObjInfo) {
	writeLine('serverLog', 'cyverse_repl_dataObjModified(*User, *Zone, DataObjInfo) called');
}