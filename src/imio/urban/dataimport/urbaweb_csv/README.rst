=======================
New Urbaweb CSV profile
=======================


How it works
============

Create a schema on a local mysql database
Copy required csv files in a folder, configure (user/pass/schema) and execute load_csv.sh
Give to current user the write rights on /var/lib/mysql-files folder
Launch SQL script to create required views and generate csv output (remove csv output file between general query execution)
Use a new classic imio.urban.dataimport CSV profile




