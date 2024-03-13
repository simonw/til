# Generating URLs to a Gmail compose window

I wanted to send out a small batch of follow-up emails for workshop attendees today, and I realized that since I have their emails in a database table I might be able to semi-automate the process.

I guessed that Gmail might have a way to generate a querystring URL to the compose interface such that the to/subject/body fields were filled out for me.

I ran prompts through ChatGPT, Claude and Google Gemini - in my experience LLMs often know about undocumented URL patterns like this.

The answer I got back turned out to work, but was out-of-date (it redirected to something different). Here's what I figured out as the current correct format:

`https://mail.google.com/mail/u/0/?to=recipient@example.com&cc=one@example.com,two@example.com&bcc=bcc@example.com&su=Email+Subject&body=Hello+There&tf=cm`

Or more clearly formatted:

```
https://mail.google.com/mail/u/0/
  ?to=recipient@example.com
  &cc=one@example.com,two@example.com
  &bcc=bcc@example.com
  &su=Email+Subject
  &body=Hello+There
  &tf=cm
```

The `tf=cm` parameter at the end is the one that navigates to a compose window.

The query string parameters are:

- `to` - the recipients - can be comma separated
- `cc` - CCs - can also be comma separated
- `bcc` - BCCs - can also be comma separated
- `su` - the email subject
- `body` - the initial email body

## What this gets you

![Screenshot of a Gmail compose window. The To, CC, BCC, Subject and Body are filled out as requested in the URL.](https://github.com/simonw/til/assets/9599/87c9ef81-c067-45b1-b9d1-b5a3334e07dc)

## Tip about the /u/0/ bit

Tip [from Corentin Smith](https://twitter.com/CorentinSmith/status/1768000490481004641):

> You can replace the `/u/0/` with `/u/youremail@gmail.com/`, it will redirect you to the correct account

## It doesn't work on Mobile Web

Frustratingly, attempting to click one of these links in Mobile Safari takes you to the Gmail inbox but does not open a compose window. I don't know if there's a workaround for that.

## The answer from Gemini

My prompt was:

> I would like to build an application that helps me send out emails by constructing URLs to the Gmail interface in the way that will pre-fill the to and cc and subject and body fields for me
>
> Show me an example URL like that and then give me a table, documenting all of the query string parameters that I need to know

Google Gemini gave me this example:

`https://mail.google.com/mail/?view=cm&fs=1&to=recipient@example.com&cc=someoneelse@example.com&su=Email%20Subject&body=Hello%20There`

Following that link redirected to almost the example I provided above.

Gemini also gave me this table:

| Parameter | Description                                            | Example                                              |
|-----------|--------------------------------------------------------|------------------------------------------------------|
| `view`      | **Required.** Sets the view mode to compose (`cm`)     | `view=cm`                                              |
| `fs`        | **Required.** Fullscreen mode (`1` for on, `0` off)    | `fs=1`                                                 |
| `to`        | The recipient's email address                          | `to=recipient@example.com`                             |
| `cc`        | Email address(es) to CC (separate by commas)           | `cc=someoneelse@example.com`                           |
| `bcc`       | Email address(es) to BCC (separate by commas)          | `bcc=anotherperson@example.com`                        |
| `su`        | The email subject (URL Encoded)                        | `su=Email%20Subject`                                   |
| `body`      | The email body (URL Encoded)                           | `body=Hello%20There`                                   | 

That's not entirely correct -the `fs=0/1` option no longer does anything, and I found that `view=cm` should be replaced by `tf=cm`.
