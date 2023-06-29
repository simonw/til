# Bulk editing status in GitHub Projects

GitHub Projects has a mechanism for bulk updating the status of items, but it's pretty difficult to figure out how to do it.

The trick is to use copy and paste. You can select a cell containing a status and hit `Command+C` to copy it - at which point a dotted border will be displayed around the cell.

Then you can select and then shift-click a range of other cells, and hit `Command+V` to paste the value.

Here's a demo:

![I click a In Progress cell and the border goes dotted when I hit the copy keyboard shortcut. Then I shift-click to select a range of cells and hit paste to update their status.](https://github.com/simonw/til/assets/9599/aedd6b5c-167e-40a1-9866-68410c0299d7)

Here's where this feature was introduced [in the GitHub changelog](https://github.blog/changelog/2023-04-06-github-issues-projects-april-6th-update/#t-rex-bulk-editing-in-tables). See also [this community discussions thread](https://github.com/orgs/community/discussions/5465).
