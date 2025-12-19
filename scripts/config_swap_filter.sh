#!/bin/bash

SUFFIX=$1

# NOTE: filter runs in the repo root.

lead='^### BEGIN GENERATED CONTENT$'
tail='^### END GENERATED CONTENT$'
sed -e "/$lead/,/$tail/{ /$lead/{p; r hardware/configuration.py.$SUFFIX
        }; /$tail/p; d }"
