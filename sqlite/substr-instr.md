# Combining substr and instr to extract text

Derek Willis has [a Datasette instance full of political campaign emails](https://political-emails.herokuapp.com/) running on Heroku.

Matt Hodges [pointed out](https://twitter.com/hodgesmr/status/1493359553488076802) that [a lot of these emails](https://political-emails.herokuapp.com/emails?sql=select%0D%0A++body%0D%0Afrom%0D%0A++emails%0D%0Awhere%0D%0A++body+LIKE+%27%25refcode%25%27) include `refcode=` codes, which are used by ActBlue campaigns to track clicks.

They look like this:

- `...c-email?refcode=220210_FR_midmonth1kavin_plain] Jessica Mason...`
- `...hmp-footer?refcode=2021_footer&amount=25&a...`

I thought it would be fun to extract just the codes.

The [datasette-rure](https://datasette.io/plugins/datasette-rure) plugin adds regular expression support which can be used for this kind of thing, but in the absence of a plugin like that the only way to do it is with the SQLite [instr()](https://www.sqlite.org/lang_corefunc.html#instr) and [substr()](https://www.sqlite.org/lang_corefunc.html#substr) functions.

Here's the query I figured out:

```sql
with snippets as (
  select
    substr(body, instr(body, 'refcode=') + 8, 128) as snippet
  from
    emails
  where
    body LIKE '%refcode%'
),
refcodes as (
  select
    snippet,
    substr(
      snippet,
      0,
      min(
        case
          when instr(snippet, '&') > 0 then instr(snippet, '&')
          else 128
        end,
        case
          when instr(snippet, ']') > 0 then instr(snippet, ']')
          else 128
        end,
        case
          when instr(snippet, ' ') > 0 then instr(snippet, ' ')
          else 128
        end,
        case
          when instr(snippet, '.') > 0 then instr(snippet, '.')
          else 128
        end
      )
    ) as refcode
  from
    snippets
)
select
  refcode,
  count(*) as n
from
  refcodes
group by
  refcode
order by
  n desc
```

I started by pulling out just the 128 characters following each `refcode=` - I picked 128 characters at random just to make the data easier to look at:
```sql
    substr(body, instr(body, 'refcode=') + 8, 128) as snippet
```
`instr(body, 'refcode=') + 8` gives the character after the `=` sign, because `refcode=` is 8 characters long.

Next I needed to find the first character following the refcode that was either a `&`, a `]`, a `  space or a `.`. That's what this bit does:
```sql
    substr(
      snippet,
      0,
      min(
        case
          when instr(snippet, '&') > 0 then instr(snippet, '&')
          else 128
        end,
        case
          when instr(snippet, ']') > 0 then instr(snippet, ']')
          else 128
        end,
        case
          when instr(snippet, ' ') > 0 then instr(snippet, ' ')
          else 128
        end,
        case
          when instr(snippet, '.') > 0 then instr(snippet, '.')
          else 128
        end
      )
    ) as refcode
```
I'm trying to find the first instance of any of those characters - so I use `instr` to find them, but ignore any results where that returns `0` for "character not found" - in those cases I use the number `128` picked earlier. I can then grab the minimum of those scores.

Then finally I do a group-by/count to find the most common refcodes:

```sql
select
  refcode,
  count(*) as n
from
  refcodes
group by
  refcode
order by
  n desc
```

Top results were:

| refcode                                            |   n |
|----------------------------------------------------|-----|
| email_footer                                       | 527 |
| em_pt                                              | 352 |
| em_fr_2020                                         | 285 |
| pt                                                 | 254 |
| emfooter                                           | 242 |
| em_fr_2021                                         | 242 |
| footer-bio                                         | 198 |
| footer_button                                      | 192 |
| em_footer                                          | 173 |
| email-footer                                       | 168 |
|                                                    | 168 |
| footer                                             | 164 |
| em2021                                             | 135 |
| em_jc_fr_footer_link                               | 107 |
| em_fr_2019                                         | 107 |
| em-footer                                          | 104 |
| em_fr_2018                                         |  84 |
| ABD_EM_FR_2021                                     |  67 |
