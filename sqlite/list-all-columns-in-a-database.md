# List all columns in a SQLite database

Here's a devious trick for listing ALL columns in a SQLite database, using a SQL query that generates another SQL query.

The first query:

```sql
select group_concat(
  "select '" || name || "' as table_name, * from pragma_table_info('" || name || "')"
, ' union ') || ' order by table_name, cid'
  from sqlite_master where type = 'table';
```
This outputs the second query, which will look something like this:
```sql
select 'simple_primary_key' as table_name, * from pragma_table_info('simple_primary_key') union
select 'primary_key_multiple_columns' as table_name, * from pragma_table_info('primary_key_multiple_columns') union
select 'primary_key_multiple_columns_explicit_label' as table_name, * from pragma_table_info('primary_key_multiple_columns_explicit_label') union
select 'compound_primary_key' as table_name, * from pragma_table_info('compound_primary_key') union
select 'compound_three_primary_keys' as table_name, * from pragma_table_info('compound_three_primary_keys') union
select 'foreign_key_references' as table_name, * from pragma_table_info('foreign_key_references') union
select 'sortable' as table_name, * from pragma_table_info('sortable') union
select 'no_primary_key' as table_name, * from pragma_table_info('no_primary_key') union
select '123_starts_with_digits' as table_name, * from pragma_table_info('123_starts_with_digits') union
select 'Table With Space In Name' as table_name, * from pragma_table_info('Table With Space In Name') union
select 'table/with/slashes.csv' as table_name, * from pragma_table_info('table/with/slashes.csv') union
select 'complex_foreign_keys' as table_name, * from pragma_table_info('complex_foreign_keys') union
select 'custom_foreign_key_label' as table_name, * from pragma_table_info('custom_foreign_key_label') union
select 'units' as table_name, * from pragma_table_info('units') union
select 'tags' as table_name, * from pragma_table_info('tags') union
select 'searchable' as table_name, * from pragma_table_info('searchable') union
select 'searchable_tags' as table_name, * from pragma_table_info('searchable_tags') union
select 'searchable_fts' as table_name, * from pragma_table_info('searchable_fts') union
select 'searchable_fts_content' as table_name, * from pragma_table_info('searchable_fts_content') union
select 'searchable_fts_segments' as table_name, * from pragma_table_info('searchable_fts_segments') union
select 'searchable_fts_segdir' as table_name, * from pragma_table_info('searchable_fts_segdir') union
select 'select' as table_name, * from pragma_table_info('select') union
select 'infinity' as table_name, * from pragma_table_info('infinity') union
select 'facet_cities' as table_name, * from pragma_table_info('facet_cities') union
select 'facetable' as table_name, * from pragma_table_info('facetable') union
select 'binary_data' as table_name, * from pragma_table_info('binary_data') union
select 'roadside_attractions' as table_name, * from pragma_table_info('roadside_attractions') union
select 'attraction_characteristic' as table_name, * from pragma_table_info('attraction_characteristic') union
select 'roadside_attraction_characteristics' as table_name, * from pragma_table_info('roadside_attraction_characteristics')
order by table_name, cid
```
Executing that second query will return results like this:
|table_name|cid|name|type|notnull|dflt_value|pk|
|--- |--- |--- |--- |--- |--- |--- |
|123_starts_with_digits|0|content|text|0||0|
|Table With Space In Name|0|pk|varchar(30)|0||1|
|Table With Space In Name|1|content|text|0||0|
|attraction_characteristic|0|pk|integer|0||1|
|attraction_characteristic|1|name|text|0||0|
|binary_data|0|data|BLOB|0||0|
|complex_foreign_keys|0|pk|varchar(30)|0||1|
|complex_foreign_keys|1|f1|text|0||0|
|complex_foreign_keys|2|f2|text|0||0|
|complex_foreign_keys|3|f3|text|0||0|
|compound_primary_key|0|pk1|varchar(30)|0||1|
|compound_primary_key|1|pk2|varchar(30)|0||2|
|compound_primary_key|2|content|text|0||0|
|compound_three_primary_keys|0|pk1|varchar(30)|0||1|
|compound_three_primary_keys|1|pk2|varchar(30)|0||2|
|compound_three_primary_keys|2|pk3|varchar(30)|0||3|
|compound_three_primary_keys|3|content|text|0||0|
|custom_foreign_key_label|0|pk|varchar(30)|0||1|
|custom_foreign_key_label|1|foreign_key_with_custom_label|text|0||0|
|facet_cities|0|id|integer|0||1|
|facet_cities|1|name|text|0||0|
|facetable|0|pk|integer|0||1|
|facetable|1|created|text|0||0|
|facetable|2|planet_int|integer|0||0|
|facetable|3|on_earth|integer|0||0|
|facetable|4|state|text|0||0|
|facetable|5|city_id|integer|0||0|
|facetable|6|neighborhood|text|0||0|
|facetable|7|tags|text|0||0|
|facetable|8|complex_array|text|0||0|
|facetable|9|distinct_some_null||0||0|
|foreign_key_references|0|pk|varchar(30)|0||1|
|foreign_key_references|1|foreign_key_with_label|varchar(30)|0||0|
|foreign_key_references|2|foreign_key_with_no_label|varchar(30)|0||0|
|infinity|0|value|REAL|0||0|
|no_primary_key|0|content|text|0||0|
|no_primary_key|1|a|text|0||0|
|no_primary_key|2|b|text|0||0|
|no_primary_key|3|c|text|0||0|
|primary_key_multiple_columns|0|id|varchar(30)|0||1|
|primary_key_multiple_columns|1|content|text|0||0|
|primary_key_multiple_columns|2|content2|text|0||0|
|primary_key_multiple_columns_explicit_label|0|id|varchar(30)|0||1|
|primary_key_multiple_columns_explicit_label|1|content|text|0||0|
|primary_key_multiple_columns_explicit_label|2|content2|text|0||0|
|roadside_attraction_characteristics|0|attraction_id|INTEGER|0||0|
|roadside_attraction_characteristics|1|characteristic_id|INTEGER|0||0|
|roadside_attractions|0|pk|integer|0||1|
|roadside_attractions|1|name|text|0||0|
|roadside_attractions|2|address|text|0||0|
|roadside_attractions|3|latitude|real|0||0|
|roadside_attractions|4|longitude|real|0||0|
|searchable|0|pk|integer|0||1|
|searchable|1|text1|text|0||0|
|searchable|2|text2|text|0||0|
|searchable|3|name with . and spaces|text|0||0|
|searchable_fts|0|text1||0||0|
|searchable_fts|1|text2||0||0|
|searchable_fts|2|name with . and spaces||0||0|
|searchable_fts|3|content||0||0|
|searchable_fts_content|0|docid|INTEGER|0||1|
|searchable_fts_content|1|c0text1||0||0|
|searchable_fts_content|2|c1text2||0||0|
|searchable_fts_content|3|c2name with . and spaces||0||0|
|searchable_fts_content|4|c3content||0||0|
|searchable_fts_segdir|0|level|INTEGER|0||1|
|searchable_fts_segdir|1|idx|INTEGER|0||2|
|searchable_fts_segdir|2|start_block|INTEGER|0||0|
|searchable_fts_segdir|3|leaves_end_block|INTEGER|0||0|
|searchable_fts_segdir|4|end_block|INTEGER|0||0|
|searchable_fts_segdir|5|root|BLOB|0||0|
|searchable_fts_segments|0|blockid|INTEGER|0||1|
|searchable_fts_segments|1|block|BLOB|0||0|
|searchable_tags|0|searchable_id|integer|0||1|
|searchable_tags|1|tag|text|0||2|
|select|0|group|text|0||0|
|select|1|having|text|0||0|
|select|2|and|text|0||0|
|select|3|json|text|0||0|
|simple_primary_key|0|id|varchar(30)|0||1|
|simple_primary_key|1|content|text|0||0|
|sortable|0|pk1|varchar(30)|0||1|
|sortable|1|pk2|varchar(30)|0||2|
|sortable|2|content|text|0||0|
|sortable|3|sortable|integer|0||0|
|sortable|4|sortable_with_nulls|real|0||0|
|sortable|5|sortable_with_nulls_2|real|0||0|
|sortable|6|text|text|0||0|
|table/with/slashes.csv|0|pk|varchar(30)|0||1|
|table/with/slashes.csv|1|content|text|0||0|
|tags|0|tag|TEXT|0||1|
|units|0|pk|integer|0||1|
|units|1|distance|int|0||0|
|units|2|frequency|int|0||0|

(I generated that Markdown table by pasting the HTML from Datasette into this tool: https://jmalarcon.github.io/markdowntables/)
