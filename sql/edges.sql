select
  tbl.name as "from_table",
  fk."from" as "from_column",
  fk."table" as "to_table",
  fk."to" as "to_column"
from pragma_table_list() tbl
  inner join pragma_foreign_key_list(tbl.name) fk
order by "from_table", fk.id;

