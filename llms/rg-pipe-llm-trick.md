# Piping from rg to llm to answer questions about code

Here's a trick I've used a couple of times in the past few days.

If I have a question about a codebase and I want to answer it using an LLM, I'll use `ripgrep` (aka `rg`) to search that codebase for a specific symbol and output the 5-10 lines of code that follow that symbol. 

Then I'll pipe the result to my [llm CLI tool](https://llm.datasette.io/), running through a large context model such as Claude or `gpt-4-turbo`, and ask it a question about the code.

## The question

I wanted to figure out what "read ribbons" are in the source code for https://lobste.rs/ - which I checked out from GitHub like this:

```bash
cd /tmp
git clone https://github.com/lobsters/lobsters
cd lobsters
```
## The recipe

Here's the recipe I use, explained in full below:
```bash
rg -N -A 5 read_ribbons | \
  llm --system 'explain what read ribbons are' -m gpt-4-turbo
```
Which gave me:

> Based on the provided code snippets, "read ribbons" appear to be a feature used within a web application, presumably part of a content platform that shares stories or articles. Read ribbons are likely used to track user interaction with stories, specifically marking which stories a user has read or interacted with and possibly which they are following for updates. Here's a breakdown of their functionality as inferred from the snippets:
>
> 1. **User and Story Association**: Each read ribbon record seems to connect a user (`user_id`) with a story (`story_id`), indicating that a specific user has some level of interaction or interest in a particular story.
>
> 2. **Following Status**: The field `is_following` suggests that users can follow certain stories, likely to receive notifications or updates about new comments or changes to the story. Whether a user is following a story or not is stored as a boolean value.
>
> 3. **Read Status**: The read ribbons seem to be used to determine whether a story or its comments are unread by the user. This is indicated by checks on `read_ribbons.updated_at < comments.created_at`, comparing the last update time of the read ribbon to the creation time of comments. If the comment was created after the last update of the read ribbon, it is considered "unread".
>
> 4. **Database Schema and Indexes**: The read ribbons are stored in a database table that includes columns for whether a user is following a story, creation and update timestamps for tracking interactions over time, and foreign keys to associate the ribbon with specific users and stories.
>
> 5. **Application Logic**: The read ribbons are used in various SQL queries and views, indicating their integration into the application's notification and content delivery systems. They help filter and deliver content based on what the user has not yet read or interacted with, enhancing user engagement with the platform.
>
> 6. **Updating Read Ribbons**: There is a specific action within a controller (`update_read_ribbons`) that updates the `updated_at` timestamp of read ribbons for stories that a user interacts with. This action helps manage the read status of stories and comments in real-time as the user browses the application.
>
> In summary, read ribbons are a tracking feature within an application that marks users' reading progress and interest in specific stories, allowing for personalized content updates and keeping track of what content has or hasn't been read.


## rg -N -A 5 searchterm

[ripgrep](https://github.com/BurntSushi/ripgrep) is a lightning fast grep-style tool. If you give it a search term it will find that term in every file (including in subdirectories) of your current directory:

```bash
rg read_ribbons
```
```
db/views/replying_comments_v01.sql
2:    read_ribbons.user_id,
4:    read_ribbons.story_id as story_id,
10:    (read_ribbons.updated_at < comments.created_at) as is_unread
12:    read_ribbons
14:    comments ON comments.story_id = read_ribbons.story_id
20:    read_ribbons.is_following = 1
21:    AND comments.user_id != read_ribbons.user_id
23:        (parent_comments.user_id = read_ribbons.user_id
25:         AND stories.user_id = read_ribbons.user_id))

db/schema.rb
177:  create_table "read_ribbons", id: { type: :bigint, unsigned: true }, charset: "utf8mb4", collation: "utf8mb4_general_ci", force: :cascade do |t|
183:    t.index ["story_id"], name: "index_read_ribbons_on_story_id"
184:    t.index ["user_id"], name: "index_read_ribbons_on_user_id"
...
```
For the purposes of feeding code into a large language model those line numbers are just wasted tokens. Using `-H` removes them:
```bash
rg -N read_ribbons
```
```
db/views/replying_comments_v01.sql
    read_ribbons.user_id,
    read_ribbons.story_id as story_id,
...
```
I want a bit more context. I've found that for this purpose returning the 5 or 10 lines following a match works great, which can be achieved using `-A 5` (for `--after-context`). `rg` will merge together overlapping sections:
```bash
rg -N -A 5 read_ribbons
```
```
db/schema.rb
  create_table "read_ribbons", id: { type: :bigint, unsigned: true }, charset: "utf8mb4", collation: "utf8mb4_general_ci", force: :cascade do |t|
    t.boolean "is_following", default: true
    t.datetime "created_at", precision: nil, null: false
    t.datetime "updated_at", precision: nil, null: false
    t.bigint "user_id", null: false, unsigned: true
    t.bigint "story_id", null: false, unsigned: true
    t.index ["story_id"], name: "index_read_ribbons_on_story_id"
    t.index ["user_id"], name: "index_read_ribbons_on_user_id"
  end
...
```
Tokens cost money, so I ran a check to see the token count by piping through my [ttok](https://github.com/simonw/ttok) tool:
```bash
rg -N -A 5 read_ribbons | ttok
```
It replied `7790` which is fine - GPT-4 Turbo [is currently priced](https://openai.com/pricing) at 1c per 1,000 input tokens.

The `-C 5` gives 5 lines before the match and 5 lines after. `-B 5` is just 5 lines before.

## Piping to llm

My `llm` tool accepts piped content, and can also take a `--system` prompt (for models that support it) providing instructions about what to do with that content. Hence this final recipe:

```bash
rg -N -A 5 read_ribbons | \
  llm --system 'explain what read ribbons are' -m gpt-4-turbo
```
The `-m gpt-4-turbo` option can be shortened to `-m 4t`.
