# ESIIL project policy
#
# Any data object put in an ESIIL project collection will be stored on the ESIIL
# resource server, and no other data objects may be stored there.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

@include 'esiil-env'


### DYNAMIC PEPS ###

## RESOURCE ##

# RESOLVE HIERARCHY

# This rule is provides the preprocessing logic for determine which storage
# resource to choose for a replica.
#
# This branch restricts the ESIIL resource to files in the ESIIL collection.
#
# Parameters:
#  Instance  (string) unused
#  Context   (`KeyValuePair_PI`) the resource plugin context
#  OUT       (`KeyValuePair_PI`) unused
#  Op        (string) the operation being performed
#  Host      (string) unused
#  PARSER    (`KeyValuePair_PI`) unused
#  VOTE      (float) unused
#
# XXX - Because of https://github.com/irods/irods/issues/6463
# # Error Codes:
# #  -32000 (SYS_INVALID_RESC_INPUT)  this is returned when an error occurred in
# #                                   one of the on branches of this rule
# temporaryStorage:
#  resource_resolve_hierarchy_err  this is used to store an error message when
#                                  an attempt is made to store a replica on the
#                                  ESIIL resource that should be.
# XXX - ^^^
#
pep_resource_resolve_hierarchy_pre(*Instance, *Context, *OUT, *Op, *Host, *PARSER, *VOTE) {
	on (cyverse_blockRescReq(*Op, esiil_RESC, *Context.resc_hier, *Context.logical_path)) {
		*msg = 'CYVERSE ERROR: ' ++ *Op ++ ' on ' ++ *Context.logical_path ++ ' not allowed on '
			++ esiil_RESC ++ '.';
# XXX - Because of https://github.com/irods/irods/issues/6463, an error
# happening in an `ON` condition needs to be captured and sent in the catch-all.
# 		cut;
# 		failmsg(-32000, *msg);
		temporaryStorage.resource_resolve_hierarchy_err = *msg;
		fail;
# XXX - ^^^
	}
}
