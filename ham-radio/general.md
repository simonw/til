# How I studied for my Ham radio general exam

I scraped a pass on my Ham radio general exam today, on the second attempt (you can retake on the same day for an extra $15, thankfully).

In the USA [Ham amateur radio licenses](https://en.wikipedia.org/wiki/Amateur_radio_licensing_in_the_United_States) are issued based on multiple choice exams. There are three classes of license: technician, general and amateur extra - which govern what frequency bands you are allowed to use, among other things.

I passed my technician a while ago. The general is significantly harder.

## The question pools

Each of the three exams has a fixed pool of questions. These are published as Word documents in various places, and updated every few years. I used a document from [the ARRL](https://www.arrl.org/general-question-pool).

There are many different websites, video course and apps that can help you learn the full set of questions.

I partly built my own. I extracted the text from the General question pool word document into a text file, then wrote some JavaScript in [an Observable notebook](https://observablehq.com/@simonw/ham-general-2024) to convert that into JSON. I shared my JSON of the 429 questions here:

https://github.com/simonw/ham-general-question-pool/blob/main/ham-general-july-2023-to-june-2027.json

You can open that in Datasette Lite like this:

https://lite.datasette.io/?json=https://github.com/simonw/ham-general-question-pool/blob/main/ham-general-july-2023-to-june-2027.json#/data/ham-general-july-2023-to-june-2027

I mainly used [the iPhone app](https://apps.apple.com/us/app/hamstudy-org/id1371288324) from [HamStudy.org](https://hamstudy.org/) - my own data was primarily useful for search, for things like running searches to see how many questions mentioned "Aurora".

## Studying with the HamStudy iPhone app

This app is really good, once you figure out how to use it. The three modes I found most useful were cram mode, quiz mode and the practice exam.

![Screenshot showing the Study / Quiz mode / Cram mode / Practical exam menu, an example question with the answer highlighted an the right hand panel with the chart showing how much of the material you have studied and the interface for filtering the questions.](https://static.simonwillison.net/static/2024/ham-iphone-app-1.png)

### Cram mode

In this mode you see each question along with its answer. You can tap a bar at the bottom to note how easy or hard you find the question - this seems to influence how often you will see the question in the future.

The "explain" link opens up some explanatory text. Sometimes this includes a "silly" mnemonic to help remember the answer, these are mostly really useful.

Opening up the right hand menu panel provides an extremely useful chart showing how many questions you have seen so far, across which sections. You can also use this panel to filter down to see just questions in one section, or in a custom combination of sections.

### Quiz mode

In quiz mode you get to try and answer the filtered questions - using the same filters as you applied in cram mode.

Your activity in quiz mode adds up to your "aptitude" score - my goal was to get to 100% "seen" (meaning I had at least seen each question at least once), then push my aptitude score up to above 75% for each of the sections.

### Practice exams

The practice exam puts you through a full simulated 35 question exam. It tracks your score over time, so you can see a chart showing if you are getting better.

![Screenshot of the General Exam Portal page. A chart at the top shows my score over time, with an orange line showing the passing grade. Below is an exam history section showing my score and weakest areas for different attempts.](https://static.simonwillison.net/static/2024/general-exam-portal.jpg)

At the end of each exam you get the option to review the questions. After each attempt I reviewed the questions I got wrong, tried to commit the correct answers to memory and then retook the exam (hence the pattern on my chart where failures were often followed by higher scores) to reinforce my learning.

## Some tricks I used

I few things that helped me along the way:

- I looked out for unique words that only occurred in correct answers. "Dip" is a great example - there's only one instance of dip in the entire pool and it's in a correct answer, so I remembered Jason Mendoza from the Good Place.
- I tried to spot groups of questions that were related and had potentially confusing answers. For example these two, where I noted the pattern that U was below and L was above (opposite of Upper / Lower):
  - How close to the upper edge of a band’s phone segment should your displayed carrier frequency be when using 3 kHz wide USB? Answer is "At least 3 kHz below the edge of the band"
  - How close to the lower edge of a band’s phone segment should your displayed carrier frequency be when using 3 kHz wide LSB?: Answer is "At least 3 kHz above the edge of the segment"
- I made notes of questions I consistently got wrong and tried creating mnemonics or just really focusing on memorizing the answers.

## What I wish I'd done

Cramming for the exam like this seems to be the way everyone does it, but I found it pretty unsatisfying - I don't feel like I learned nearly enough along the way.

I tend to be a very practical learner, and a challenge with Ham radio is that you need the license in advance in order to start doing the practical stuff!

My main regret is not leaving enough time to study. I crammed for the whole thing in just a few days running up to the exam - if I'd paced out my study I would have had time to dig into the underlying material more, which would have been much more satisfying.

Figuring out the pattern for using the app, described above, was the point at which my studying really started to work. I wish I'd figured this all out much sooner!
