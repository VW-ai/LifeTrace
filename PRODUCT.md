# Product Requirement Document
This file is serve as the ultimate instruction and guideline for my development; this file outlines the initiative and key features needed to be satisfied by developer.
## 1. Summary
At the MVP stage. This is going to be a project that serve a very oriented-focus: use AI(langauge model), to document and organize one's time.
This product provide the ability for people to understand what has their time has spent on over a 4-week, 1-year, and even 5-year span.
This product organize information from diary, calendar, and potentially other sources, detect what activity has occured, how long its duration, what is the nature of the activity.

## 2. Example
At simplicity, it output a information like the followoing
```csv
5 year time report
study economy, 100hr25mins
play basketball, 200hr20mins
...
```

## 3. Use Case and Workflow
Our product has two feature:
1. Consume: Consume and organize informatino from Notion/Notion Calendar
2. Display: Display the organized information from our database.
### Consume
On a daily basis, our system is triggered automoaticaly to work, in the following flow
1. Agnet is invoked everyday at 2.a.m.
2. Agent reads notion/notion calendar (it should be able to focus on what is updated, and what is not.)
3. Agent organize and events and save events to database
### Display
Our primary display on frontend will be one-single page at the point, with the following charts:
1. A line chart showing the trend of time we spent across different activity.
2. A PIE chart showing the composition of our activites
3. A breakdown list, showing our top 5 time-consuming activity, and the key words/hot words for that activity.
For charts, we should be able to select time range, and the charts will focus on the trend/composition/and break down list in the time selected.