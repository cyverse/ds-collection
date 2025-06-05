# A stub implementation of microservices used for unit testing. All rules write
# a message to the server log saying they were called.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.


msiSetReServerNumProc(*MaxNumReProcs) {
	writeLine('serverLog', 'msiSetReServerNumProc(*MaxNumReProcs) called');
}