# Tech Design
This is the high level tech design of the product. This is the serves as a structure overview and guideline in development. Any technical update should also be reflected in this file (e.g. change from using javascript to typescript; change from single agent to multi agent structure)
This file consists of 4 parts:
1. Backend
2. Frontend
3. Data Storage
4. API Design


# Backend
## Tech Stack
Python, Notion API (potentially use Notion MCP), Google Calendar API, and OpenAI API
## Layers
Our backend consists of the following layers:
1. data: This is responsible for accessing data:
    a. Notion (READ)
    b. Notion Calendar (READ)
    c. Database (CRUD)
2. processer: Queried Data are processed at this stage, and it has 2 main responsibility:
    a. based on frontend request, invoke the queryData layer appropriately, and return the data to API layer
    b. Agent lies in this layer
        b.1 Agent consumes data from Notion and Notion Calendar; categorize the data with tags with LLM ability
        b.2 Agent write data into our database
3. API: define how our backend and frontend interact with each other
    a. receive and decouple different requests
### AGENT DESIGN
Our use a single agent structure. The agent should be able to accomplish the following using tool.
#### 1. Generate appropriate tags for events it observed. Mainly, it should generate be able generate same tags for events that share the same nature at a certain level. 
    a. The information retrieval logic is simple:
        1. We start from Notion Calendar, where most events during the day is logged. 
        2. Using the name of the activity on Notion Calendar, we deduce the activities nature. This is the `Init Event Fetch`, we have a simple deduced nature of the event, and the precise time duration.
        3. We went into notion, attempting find related content for the event. We look for probable source in the following ways:
                i. Blocks with Last edited time within the time range is probable source. 
                ii. That Day's Diary probably contains some details about the activity
            We then check the probable source's with the deduced nature of the event, then we produce data entries to the `raw activity table`
            In the case we did not fetch anything relevant, we log the data entries to the `raw activity table`, and the details part we will use our deduced nature of the event.
        4. If there is any updates Notion that has not being matched in any of our calendar event, we check up the edits, and make a decision out the three choices:
                i. It should be listed as a new event; we give this type of event a time estimation based on the length of the text 【will be specified in later development】
                ii. It should be merged with some existed event.
                iii. It should be abandoned because its content is too minimal [we will add some Random Thoughts of the Day section in future stage of development, potentially, for this type of thing]
    a. Everyday, after fetch the primiarily organize information from notion and notion calendar into events `raw activity table`
        before agent starts to generate tags for events collected, it queries our database to see what existed tags to are there. Agent attempts to use existing tag to tag our current events.
    b. There are two cases where an agent can generate new tags
        b.1 the average `tag : event ratio` is too high (I will set a value for this). In this case, agent will initiate a system-wide tag generation, where it is allowed to, based on all events in the database, generate tags.
        b.2 No existing tags is appropriate: e.g. `swimming` is our only existing tag, but our event is cooking.


# Frontend
## Tech Stack
react.js
## Style
Creative, Dadaism
## Charts
1. A line chart showing the trend of time we spent across different activity.
2. A PIE chart showing the composition of our activites
3. A breakdown list, showing our top 5 time-consuming activity, and the key words/hot words for that activity.
For charts, we should be able to select time range, and the charts will focus on the trend/composition/and break down list in the time selected.


# Abstract Data Storage
The point of having processed activity table is to join different description of the same activity together. (on calendar, event's time; notion's notes, event's detail)
## Tech Stack
SQL-like database. Relational Database
## Data Schema
### raw activity table
1. Date: the date that the activity happened
2. Time (optional)
3. Duration: how long did this activity took
4. Details: In this field have a thorough summary of raw information, like text from development notes(开发笔记), or whatever from calendar. 
5. Source: e.g., notion, notion calendar.
6. Orig: a link pointing the original information
### processed activity table
1. Date: the date that the activity happened
2. Time (optional)
3. Raw acitvities: the IDs of raw activity we point to.
6. tag, generated based on details.


# API
Our API includes external type and internal type
## External
1. Notion API: we use it to read Notion
2. Notion Calendar: we use it to read Notion Calendar
3. OpenAI API: We build our agent using OpenAI's model
## Internal
### Backend
1. Process the line chart query from frontend
2. Process the PIE chart query from frontend
3. Process the Breakdown List query from frontend