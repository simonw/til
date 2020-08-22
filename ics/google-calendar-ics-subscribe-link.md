# Providing a "subscribe in Google Calendar" link for an ics feed

If you provide your own custom generated ICS file hosted at a URL it's nice to be able to give Google Calendar users an easy way to subscribe to that feed.

As far as I can tell this isn't documented anywhere, but it is possible.

The format is:

    https://www.google.com/calendar/render?cid=webcal://pretalx.com/pycon-au-2020/schedule/export/schedule.ics

So it's `https://www.google.com/calendar/render?cid=webcal://` followed by your URL.

I believe this only works if you are serving your ICS feed over HTTPS.
