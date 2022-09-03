# Loading Twitter Birdwatch into SQLite for analysis with Datasette

[Twitter Birdwatch](https://twitter.github.io/birdwatch/) is "a collaborative way to add helpful context to Tweets and keep people better informed".

Data collected by the program is [made available for download](https://twitter.github.io/birdwatch/download-data/) as a trio of TSV files.

You can obtain those files from [this page](https://twitter.com/i/birdwatch/download-data) (Twitter login required). The files are:

- `notes-0000.tsv`
- `ratings-0000.tsv`
- `noteStatusHistory-0000.tsv`

As far as I can tell they only include notes and ratings from the past 48 hours. This means the files are quite small - when I downloaded them on 3rd September 2022 they were:

```
2.7M  noteStatusHistory-00000.tsv
16M   notes-00000.tsv
45M   ratings-00000.tsv
```

## Import into SQLite

I used [sqlite-utils insert](https://sqlite-utils.datasette.io/en/stable/cli.html#inserting-csv-or-tsv-data) to insert the data into a `birdwatch.db` SQLite database:

```
sqlite-utils insert birdwatch.db notes notes-00000.tsv --tsv --detect-types
sqlite-utils insert birdwatch.db ratings ratings-00000.tsv --tsv --detect-types
sqlite-utils insert birdwatch.db noteStatusHistory noteStatusHistory-00000.tsv --tsv --detect-types
```
The `--detect-types` option ensures we get a mix of `integer` and `text` columns - without this we would just get `text`.

Having run this, the schema of the resulting database file looks like this:

```
sqlite-utils schema birdwatch.db
```
```sql
CREATE TABLE "notes" (
   [noteId] INTEGER,
   [participantId] TEXT,
   [createdAtMillis] INTEGER,
   [tweetId] INTEGER,
   [classification] TEXT,
   [believable] TEXT,
   [harmful] TEXT,
   [validationDifficulty] TEXT,
   [misleadingOther] INTEGER,
   [misleadingFactualError] INTEGER,
   [misleadingManipulatedMedia] INTEGER,
   [misleadingOutdatedInformation] INTEGER,
   [misleadingMissingImportantContext] INTEGER,
   [misleadingUnverifiedClaimAsFact] INTEGER,
   [misleadingSatire] INTEGER,
   [notMisleadingOther] INTEGER,
   [notMisleadingFactuallyCorrect] INTEGER,
   [notMisleadingOutdatedButNotWhenWritten] INTEGER,
   [notMisleadingClearlySatire] INTEGER,
   [notMisleadingPersonalOpinion] INTEGER,
   [trustworthySources] INTEGER,
   [summary] TEXT
);
CREATE TABLE "ratings" (
   [noteId] INTEGER,
   [participantId] TEXT,
   [createdAtMillis] INTEGER,
   [version] INTEGER,
   [agree] INTEGER,
   [disagree] INTEGER,
   [helpful] INTEGER,
   [notHelpful] INTEGER,
   [helpfulnessLevel] TEXT,
   [helpfulOther] INTEGER,
   [helpfulInformative] INTEGER,
   [helpfulClear] INTEGER,
   [helpfulEmpathetic] INTEGER,
   [helpfulGoodSources] INTEGER,
   [helpfulUniqueContext] INTEGER,
   [helpfulAddressesClaim] INTEGER,
   [helpfulImportantContext] INTEGER,
   [helpfulUnbiasedLanguage] INTEGER,
   [notHelpfulOther] INTEGER,
   [notHelpfulIncorrect] INTEGER,
   [notHelpfulSourcesMissingOrUnreliable] INTEGER,
   [notHelpfulOpinionSpeculationOrBias] INTEGER,
   [notHelpfulMissingKeyPoints] INTEGER,
   [notHelpfulOutdated] INTEGER,
   [notHelpfulHardToUnderstand] INTEGER,
   [notHelpfulArgumentativeOrBiased] INTEGER,
   [notHelpfulOffTopic] INTEGER,
   [notHelpfulSpamHarassmentOrAbuse] INTEGER,
   [notHelpfulIrrelevantSources] INTEGER,
   [notHelpfulOpinionSpeculation] INTEGER,
   [notHelpfulNoteNotNeeded] INTEGER
);
CREATE TABLE "noteStatusHistory" (
   [noteId] INTEGER,
   [participantId] TEXT,
   [createdAtMillis] INTEGER,
   [timestampMillisOfFirstNonNMRStatus] INTEGER,
   [firstNonNMRStatus] TEXT,
   [timestampMillisOfCurrentStatus] INTEGER,
   [currentStatus] TEXT,
   [timestampMillisOfMostRecentNonNMRStatus] INTEGER,
   [mostRecentNonNMRStatus] TEXT
);
```

## Enabling search

The `summary` column in the `notes` table is the most interesting with respect to search. We can enable SQLite full-text search on it like this:

```
sqlite-utils enable-its birdwatch.db notes summary
```

## Downloading the full tweets

The Birdwatch data includes plenty of tweet IDs - in the `tweetId` column in the `notes` table - but it doesn't include the full details of those tweets.

If you have old credentials for v1 of the Twitter API you can use [twitter-to-sqlite](https://datasette.io/tools/twitter-to-sqlite) to download the full details of those tweets like this:

    twitter-to-sqlite statuses-lookup birdwatch.db --sql 'select distinct tweetId from notes'

This fetches full tweets (and authors and attachments and suchlike) for every tweet with an ID matching one from the SQL query `select distinct tweetId from notes`.

This command shows a progress bar while it works:

    Importing 27,909 tweets  [#####-------------------]   17%  00:10:26

If you don't have Twitter APIv1 credentials consider using [twarc](https://twarc-project.readthedocs.io/) instead (maybe with [this plugin](https://github.com/DocNow/twarc-csv)).

The final database schema looks like this:

```sql
CREATE TABLE "notes" (
   [noteId] INTEGER,
   [participantId] TEXT,
   [createdAtMillis] INTEGER,
   [tweetId] INTEGER,
   [classification] TEXT,
   [believable] TEXT,
   [harmful] TEXT,
   [validationDifficulty] TEXT,
   [misleadingOther] INTEGER,
   [misleadingFactualError] INTEGER,
   [misleadingManipulatedMedia] INTEGER,
   [misleadingOutdatedInformation] INTEGER,
   [misleadingMissingImportantContext] INTEGER,
   [misleadingUnverifiedClaimAsFact] INTEGER,
   [misleadingSatire] INTEGER,
   [notMisleadingOther] INTEGER,
   [notMisleadingFactuallyCorrect] INTEGER,
   [notMisleadingOutdatedButNotWhenWritten] INTEGER,
   [notMisleadingClearlySatire] INTEGER,
   [notMisleadingPersonalOpinion] INTEGER,
   [trustworthySources] INTEGER,
   [summary] TEXT
);
CREATE TABLE "ratings" (
   [noteId] INTEGER,
   [participantId] TEXT,
   [createdAtMillis] INTEGER,
   [version] INTEGER,
   [agree] INTEGER,
   [disagree] INTEGER,
   [helpful] INTEGER,
   [notHelpful] INTEGER,
   [helpfulnessLevel] TEXT,
   [helpfulOther] INTEGER,
   [helpfulInformative] INTEGER,
   [helpfulClear] INTEGER,
   [helpfulEmpathetic] INTEGER,
   [helpfulGoodSources] INTEGER,
   [helpfulUniqueContext] INTEGER,
   [helpfulAddressesClaim] INTEGER,
   [helpfulImportantContext] INTEGER,
   [helpfulUnbiasedLanguage] INTEGER,
   [notHelpfulOther] INTEGER,
   [notHelpfulIncorrect] INTEGER,
   [notHelpfulSourcesMissingOrUnreliable] INTEGER,
   [notHelpfulOpinionSpeculationOrBias] INTEGER,
   [notHelpfulMissingKeyPoints] INTEGER,
   [notHelpfulOutdated] INTEGER,
   [notHelpfulHardToUnderstand] INTEGER,
   [notHelpfulArgumentativeOrBiased] INTEGER,
   [notHelpfulOffTopic] INTEGER,
   [notHelpfulSpamHarassmentOrAbuse] INTEGER,
   [notHelpfulIrrelevantSources] INTEGER,
   [notHelpfulOpinionSpeculation] INTEGER,
   [notHelpfulNoteNotNeeded] INTEGER
);
CREATE TABLE "noteStatusHistory" (
   [noteId] INTEGER,
   [participantId] TEXT,
   [createdAtMillis] INTEGER,
   [timestampMillisOfFirstNonNMRStatus] INTEGER,
   [firstNonNMRStatus] TEXT,
   [timestampMillisOfCurrentStatus] INTEGER,
   [currentStatus] TEXT,
   [timestampMillisOfMostRecentNonNMRStatus] INTEGER,
   [mostRecentNonNMRStatus] TEXT
);
CREATE TABLE 'notes_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'notes_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'notes_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'notes_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE [migrations] (
   [name] TEXT PRIMARY KEY,
   [applied] TEXT
);
CREATE TABLE [places] (
   [id] TEXT PRIMARY KEY
, [url] TEXT, [place_type] TEXT, [name] TEXT, [full_name] TEXT, [country_code] TEXT, [country] TEXT, [contained_within] TEXT, [bounding_box] TEXT, [attributes] TEXT);
CREATE TABLE [sources] (
   [id] TEXT PRIMARY KEY,
   [name] TEXT,
   [url] TEXT
);
CREATE TABLE [users] (
   [id] INTEGER PRIMARY KEY,
   [screen_name] TEXT,
   [name] TEXT,
   [description] TEXT,
   [location] TEXT
, [url] TEXT, [protected] INTEGER, [followers_count] INTEGER, [friends_count] INTEGER, [listed_count] INTEGER, [created_at] TEXT, [favourites_count] INTEGER, [utc_offset] TEXT, [time_zone] TEXT, [geo_enabled] INTEGER, [verified] INTEGER, [statuses_count] INTEGER, [lang] TEXT, [contributors_enabled] INTEGER, [is_translator] INTEGER, [is_translation_enabled] INTEGER, [profile_background_color] TEXT, [profile_background_image_url] TEXT, [profile_background_image_url_https] TEXT, [profile_background_tile] INTEGER, [profile_image_url] TEXT, [profile_image_url_https] TEXT, [profile_banner_url] TEXT, [profile_link_color] TEXT, [profile_sidebar_border_color] TEXT, [profile_sidebar_fill_color] TEXT, [profile_text_color] TEXT, [profile_use_background_image] INTEGER, [has_extended_profile] INTEGER, [default_profile] INTEGER, [default_profile_image] INTEGER, [following] INTEGER, [follow_request_sent] INTEGER, [notifications] INTEGER, [translator_type] TEXT, [withheld_in_countries] TEXT);
CREATE TABLE 'users_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'users_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'users_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'users_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE [tweets] (
   [id] INTEGER PRIMARY KEY,
   [user] INTEGER REFERENCES [users]([id]),
   [created_at] TEXT,
   [full_text] TEXT,
   [retweeted_status] INTEGER,
   [quoted_status] INTEGER,
   [place] TEXT REFERENCES [places]([id]),
   [source] TEXT REFERENCES [sources]([id]), [truncated] INTEGER, [display_text_range] TEXT, [in_reply_to_status_id] TEXT, [in_reply_to_user_id] TEXT, [in_reply_to_screen_name] TEXT, [geo] TEXT, [coordinates] TEXT, [contributors] TEXT, [is_quote_status] INTEGER, [retweet_count] INTEGER, [favorite_count] INTEGER, [favorited] INTEGER, [retweeted] INTEGER, [lang] TEXT, [possibly_sensitive] INTEGER, [scopes] TEXT, [withheld_in_countries] TEXT, [withheld_scope] TEXT, [withheld_copyright] INTEGER,
   FOREIGN KEY([retweeted_status]) REFERENCES [tweets]([id]),
   FOREIGN KEY([quoted_status]) REFERENCES [tweets]([id])
);
CREATE TABLE 'tweets_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'tweets_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'tweets_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'tweets_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE VIRTUAL TABLE [notes_fts] USING FTS5 (
    [summary],
    content=[notes]
);
CREATE TRIGGER [notes_ai] AFTER INSERT ON [notes] BEGIN
  INSERT INTO [notes_fts] (rowid, [summary]) VALUES (new.rowid, new.[summary]);
END;
CREATE TRIGGER [notes_ad] AFTER DELETE ON [notes] BEGIN
  INSERT INTO [notes_fts] ([notes_fts], rowid, [summary]) VALUES('delete', old.rowid, old.[summary]);
END;
CREATE TRIGGER [notes_au] AFTER UPDATE ON [notes] BEGIN
  INSERT INTO [notes_fts] ([notes_fts], rowid, [summary]) VALUES('delete', old.rowid, old.[summary]);
  INSERT INTO [notes_fts] (rowid, [summary]) VALUES (new.rowid, new.[summary]);
END;
CREATE VIRTUAL TABLE [users_fts] USING FTS5 (
    [name], [screen_name], [description], [location],
    content=[users]
);
CREATE TRIGGER [users_ai] AFTER INSERT ON [users] BEGIN
  INSERT INTO [users_fts] (rowid, [name], [screen_name], [description], [location]) VALUES (new.rowid, new.[name], new.[screen_name], new.[description], new.[location]);
END;
CREATE TRIGGER [users_ad] AFTER DELETE ON [users] BEGIN
  INSERT INTO [users_fts] ([users_fts], rowid, [name], [screen_name], [description], [location]) VALUES('delete', old.rowid, old.[name], old.[screen_name], old.[description], old.[location]);
END;
CREATE TRIGGER [users_au] AFTER UPDATE ON [users] BEGIN
  INSERT INTO [users_fts] ([users_fts], rowid, [name], [screen_name], [description], [location]) VALUES('delete', old.rowid, old.[name], old.[screen_name], old.[description], old.[location]);
  INSERT INTO [users_fts] (rowid, [name], [screen_name], [description], [location]) VALUES (new.rowid, new.[name], new.[screen_name], new.[description], new.[location]);
END;
CREATE VIRTUAL TABLE [tweets_fts] USING FTS5 (
    [full_text],
    content=[tweets]
);
CREATE TRIGGER [tweets_ai] AFTER INSERT ON [tweets] BEGIN
  INSERT INTO [tweets_fts] (rowid, [full_text]) VALUES (new.rowid, new.[full_text]);
END;
CREATE TRIGGER [tweets_ad] AFTER DELETE ON [tweets] BEGIN
  INSERT INTO [tweets_fts] ([tweets_fts], rowid, [full_text]) VALUES('delete', old.rowid, old.[full_text]);
END;
CREATE TRIGGER [tweets_au] AFTER UPDATE ON [tweets] BEGIN
  INSERT INTO [tweets_fts] ([tweets_fts], rowid, [full_text]) VALUES('delete', old.rowid, old.[full_text]);
  INSERT INTO [tweets_fts] (rowid, [full_text]) VALUES (new.rowid, new.[full_text]);
END;
CREATE TABLE [following] (
   [followed_id] INTEGER REFERENCES [users]([id]),
   [follower_id] INTEGER REFERENCES [users]([id]),
   [first_seen] TEXT,
   PRIMARY KEY ([followed_id], [follower_id])
);
CREATE INDEX [idx_following_followed_id]
    ON [following] ([followed_id]);
CREATE INDEX [idx_following_follower_id]
    ON [following] ([follower_id]);
CREATE TABLE [since_id_types] (
   [id] INTEGER PRIMARY KEY,
   [name] TEXT
);
CREATE TABLE [since_ids] (
   [type] INTEGER REFERENCES [since_id_types]([id]),
   [key] TEXT,
   [since_id] INTEGER,
   PRIMARY KEY ([type], [key])
);
CREATE TABLE [count_history_types] (
   [id] INTEGER PRIMARY KEY,
   [name] TEXT
);
CREATE TABLE [count_history] (
   [type] INTEGER REFERENCES [count_history_types]([id]),
   [user] INTEGER REFERENCES [users]([id]),
   [datetime] TEXT,
   [count] INTEGER,
   PRIMARY KEY ([type], [user], [datetime])
);
CREATE TABLE [media] (
   [id] INTEGER PRIMARY KEY,
   [id_str] TEXT,
   [indices] TEXT,
   [media_url] TEXT,
   [media_url_https] TEXT,
   [url] TEXT,
   [display_url] TEXT,
   [expanded_url] TEXT,
   [type] TEXT,
   [sizes] TEXT
, [video_info] TEXT, [additional_media_info] TEXT, [source_status_id] INTEGER, [source_status_id_str] TEXT, [source_user_id] INTEGER, [source_user_id_str] TEXT);
CREATE TABLE [media_tweets] (
   [media_id] INTEGER REFERENCES [media]([id]),
   [tweets_id] INTEGER REFERENCES [tweets]([id]),
   PRIMARY KEY ([media_id], [tweets_id])
);
```

## A warning about IDs

The resulting database from all of this stores twitter IDs as integers.

If you are processing these using JavaScript, you may run into problems with JavaScript's maximum integer size being 9007199254740991 - some twitter IDs may exceed this.

If this is a problem for you, dropping the `--detect-types` options from the initial TSV import should result in IDs being stored as text instead which will work around the issue.

## Now open it in Datasette

You can use the command-line version of [Datasette](https://datasette.io/):

    pip install datasette
    # OR
    brew install datasette
    # OR
    pipx install datasette
    datasette birdwatch.db
    INFO:     Started server process [58650]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)

Or you can install [Datasette Desktop](https://datasette.io/desktop) for macOS and double-click the SQLite file to open it.
