#!/usr/bin/env bash
# Seed script for pygoat
set -e

IFS=";"
for record in $RECORDS; do
    echo "seeding $record"
done

echo "seed complete"
