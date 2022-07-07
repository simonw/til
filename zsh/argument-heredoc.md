# Passing command arguments using heredoc syntax

This trick works for both Bash and zsh.

I wanted to pass the following as an argument to the sqlite-utils CLI tool:

```
insert into documents select
  substr(s3_ocr_etag, 2, 8) as id,
  key as title,
  key as path,
  replace(s3_ocr_etag, '"', '') as etag
from
  index2.ocr_jobs;
```

Problem: this contains both single AND double quotes, which makes string escaping a tiny bit tricky.

Solution: use heredoc syntax:
```
sqlite-utils sfms.db --attach index2 index.db "$(cat <<EOF
insert into documents select
  substr(s3_ocr_etag, 2, 8) as id,
  key as title,
  key as path,
  replace(s3_ocr_etag, '"', '') as etag
from
  index2.ocr_jobs;
EOF
)"
```
Breaking that apart: the main trick here is to use `cat <<EOF ... EOF` to wrap the literal chunk of text:
```
$(cat <<EOF
insert into documents select
  substr(s3_ocr_etag, 2, 8) as id,
  key as title,
  key as path,
  replace(s3_ocr_etag, '"', '') as etag
from
  index2.ocr_jobs;
EOF
)
```
Then to pass it as an argument to the `sqlite-utils` command use `"$(cat ...)"` - the double quotes around that ensure that tokens in that input are not treated as separate arguments by zsh/bash.
