# Reformatting text with Copilot

I wanted to write alt text for the following screenshot ([of this page]()), so I could include it in [this post on Mastodon](https://fedi.simonwillison.net/@simon/109484810256112309).

![A screenshot of a list of issues in GitHub - they are in the incorrect order and have a bunch of metadata associated with each one](https://user-images.githubusercontent.com/9599/206784590-fa7b7741-ff60-44fe-a43e-ce4f132b8942.png)

For my alt text I wanted just the concept I was trying to illustrate - which is the number of comments attached to each of those issues.

I hit "select all" in my browser and pasted the following block of text into a new document in VS Code:

```
Day 9: Rope Bridge day
#11 by simonw was closed Dec 9, 2022
7
Day 8: Treetop Tree House day
#10 by simonw was closed Dec 8, 2022
27
Day 7: No Space Left On Device day
#9 by simonw was closed Dec 7, 2022
40
Day 6: Tuning Trouble day
#8 by simonw was closed Dec 5, 2022
16
Day 5: Supply Stacks day
#6 by simonw was closed Dec 5, 2022
17
Day 4: Camp Cleanup day
#5 by simonw was closed Dec 4, 2022
14
Day 3: Rucksack Reorganization day
#4 by simonw was closed Dec 3, 2022
28
Day 2: Rock Paper Scissors day
#3 by simonw was closed Dec 3, 2022
18
Day 1: Calorie Counting day
#1 by simonw was closed Dec 1, 2022
2
```
I wanted to reformat this to be a list of items that looked like this:

    Day 1: Calorie Counting - 2 comments

So I typed the following below:

```
Reformatted sorted by number, with the " day" removed and with just the title and the number of comments:

Day 1: Calorie Counting - 2 comments
```
Giving it an example of the first item I wanted proved essential, since it let it understand that the `2` on its own line was what I meant by "number of comments".

I hit "tab" a few times and Copilot completed the rest of the list for me:

```
Day 1: Calorie Counting - 2 comments
Day 2: Rock Paper Scissors - 18 comments
Day 3: Rucksack Reorganization - 28 comments
Day 4: Camp Cleanup - 14 comments
Day 5: Supply Stacks - 17 comments
Day 6: Tuning Trouble - 16 comments
Day 7: No Space Left On Device - 40 comments
Day 8: Treetop Tree House - 27 comments
Day 9: Rope Bridge - 7 comments
```

Here's what that looked like:

![Animated GIF showing Copilot completing each of those lines for me one at a time](https://user-images.githubusercontent.com/9599/206785272-39cd55c9-68d7-4967-a363-0281a3da70a9.gif)

It also made up a suggestion for Day 10 - "Day 10: The 'C' Language: vb - 1 comment" - no idea where it got that idea from!

