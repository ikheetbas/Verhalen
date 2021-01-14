#!/bin/sh
# -----------------------------------------------------------------------
# Environment settings for NPO Resource Manager when running local in DEV
# to activate: 'source local_settings.sh' on command line
# -----------------------------------------------------------------------

# or to past it in the env settings of your IDE:
# DEBUG=True;SECRET_KEY=bm5d\)*t\)bp95-q*gq85k3-e^=\)r\)+-8grp+\&wu+d#^eji\(enx9;ENVIRONMENT=dev-local;POSTGRES_DB=npo_rm_db;POSTGRES_USER=npo_rm_user;POSTGRES_PASSWORD=testpass123;DB_HOST=localhost
# use 'echo $DEBUG' to check if it works

DEBUG=True
export DEBUG

# ')' has been escaped by '\'
SECRET_KEY=bm5d\)*t\)bp95-q*gq85k3-e^=\)r\)+-8grp+\&wu+d#^eji\(enx9
export SECRET_KEY

ENVIRONMENT=dev-local
export ENVIRONMENT

POSTGRES_DB=npo_rm_db
export POSTGRES_DB

POSTGRES_USER=npo_rm_user
export POSTGRES_USER

POSTGRES_PASSWORD=testpass123
export POSTGRES_PASSWORD

DB_HOST=localhost
export DB_HOST
