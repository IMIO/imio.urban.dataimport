#!/bin/bash

echo "***START***"
echo "***LOAD TABLE***"
csvsql --db mysql://root:root@localhost:3306/locality_urbacsv_YYYYMMDD?charset=utf8  --create-if-not-exists  --insert *.csv
echo "***DONE***"
echo "***END***"
