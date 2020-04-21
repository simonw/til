# Null case comparisons in SQLite

I wanted to say "output this transformed value if it's not null, otherwise nothing". The recipe I figured out was:

```sql
  case
    when (media_url_https is not null) then json_object('img_src', media_url_https, 'width', 300)
  end as photo
```

Full query example:

```sql
select
  created_at,
  regexp_match('.*?(\d+(\.\d+))lb.*', full_text, 1) as lbs,
  full_text,
  case
    when (media_url_https is not null) then json_object('img_src', media_url_https, 'width', 300)
  end as photo
from
  tweets
  left join media_tweets on tweets.id = media_tweets.tweets_id
  left join media on media.id = media_tweets.media_id
where
  full_text like '%lb%'
  and user = 3166449535
  and lbs is not null
group by
  tweets.id
order by
  created_at
```
