with NumberedUniqueIndex as (
  select
    tbl.name as "table",
    idx.name as "index",
    row_number() over(partition by tbl.name) as "ordinal"
  from pragma_table_list() tbl
    inner join pragma_index_list(tbl.name) idx
  where idx."unique"),
ColumnSnowflakes as (
  select
    tbl.name as "table",
    iinfo.name as "column",
    group_concat(ni.ordinal, ' ') as "snowflakes"
  from pragma_table_list() tbl
    inner join pragma_index_list(tbl.name) as idx
    inner join pragma_index_info(idx.name) as iinfo
    inner join NumberedUniqueIndex ni
      on ni."table" = "table" and ni."index" = idx.name
  group by "table", "column"
)
select
  tbl.name as "table",
  tinfo.name as "column",
  lower(tinfo.type) || case when tinfo."notnull" then '' else '?' end as "type",
  tinfo.pk as "pk",
  snow.snowflakes as "snowflakes"
from pragma_table_list() tbl
  inner join pragma_table_xinfo(tbl.name) tinfo
  left join ColumnSnowflakes snow
    on snow."table" = tbl.name and snow."column" = tinfo.name
  where tbl.type = 'table' and tbl.name not like 'sqlite_%'
order by tbl.name, tinfo.cid;

