# This rule base contains the workarounds in cve.re that depend on the iRODS
# release. This version is for iRODS 4.3.1.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# There is no workaround for the security hole in `iput -p`, since
# pep_api_data_obj_put_pre has a huge memory leak before 4.3.4:
# https://github.com/irods/irods/issues/8106.
