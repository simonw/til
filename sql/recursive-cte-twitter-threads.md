# Using recursive CTEs to explore hierarchical Twitter threads

This TIL adapted from [a Gist](https://gist.github.com/simonw/656a8c6e4688f720773c474080abe1b0) I put together in 2019, before I started tracking TILs here.

My [twitter-to-sqlite](https://datasette.io/tools/twitter-to-sqlite) tool produced a SQLite table with an `in_reply_to_status` column that referenced another tweet ID, for recording reply-to conversations.

I wanted to find the "deepest" tweets in my database - the tweets at the end of the longest reply-to thread.

I started by adapting [this recipe](https://gist.github.com/robinhouston/f689a4b833dc027a3fd97e3de855927b) by [Robin Houston](https://mobile.twitter.com/robinhouston/status/1180893134265430016). Here's the query I came up with:

```sql
with recursive thread as (
    select id, in_reply_to_status_id, 0 as depth
        from tweets
        where in_reply_to_status_id is null
    union
        select tweets.id, tweets.in_reply_to_status_id, 1 + thread.depth as depth
        from thread join tweets on tweets.in_reply_to_status_id = thread.id)
select * from thread order by depth desc
```
This uses [a recursive CTE](https://www.sqlite.org/lang_with.html#recursive_query_examples) to sythensize a `thread` table.

The result I got looked like this (truncated):

| id | in_reply_to_status_id | depth |
| --- | --- | --- |
| 1576674019239407616 | 1576673163487821824 | 63 |
| 1576673163487821824 | 1576672866770178048 | 62 |
| 1574621292988440580 | 1574379782573531136 | 61 |
| 1574845776152432649 | 1574845672087375873 | 61 |
| 1574846026602713104 | 1574845672087375873 | 61 |
| 1574847148218322954 | 1574845672087375873 | 61 |
| 1574848163017547777 | 1574845672087375873 | 61 |
| 1576672866770178048 | 1574845672087375873 | 61 |
| 1574338300923777024 | 1574268713213210624 | 60 |

Sure enough, [tweet 1576674019239407616](https://twitter.com/wattmaller1/status/1576674019239407616) is a reply to a VERY long Twitter thread I had created about Stable Diffusion.

Matthew Somerville suggested the following improvement, which returns the full path of tweet IDs leading to that tweet:

```sql
with recursive thread as (
    select id, in_reply_to_status_id, 0 as depth, id as ids
        from tweets
        where in_reply_to_status_id is null
    union
        select tweets.id, tweets.in_reply_to_status_id, 1 + thread.depth as depth, thread.ids || ',' || tweets.id as ids
        from thread join tweets on tweets.in_reply_to_status_id = thread.id)
select * from thread where depth > 1 order by depth asc
```
The results look like this:

| id | in_reply_to_status_id | depth | ids |
| --- | --- | --- | --- |
| 4609905293 | 4608871398 | 2 | 4608471362,4608871398,4609905293 |
| 27566142087 | 27564750598 | 2 | 27563022963,27564750598,27566142087 |
| 28392727498 | 28062128369 | 2 | 28048800241,28062128369,28392727498 |
