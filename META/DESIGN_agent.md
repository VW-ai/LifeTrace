# Techinical Design for Our Agent
This is file is an extension of our DESIGN.md. This is file is a technical focusing on the behavior of our current Agent.

# Current Problem
Currently, a serious problem is that our agent is not producing meaningful tags, and it is not matching any acitivty from our Notino to Calendar.
I have investigated, and it seems like we are not utilizing the power of AI enough at the processing.
I have noitced couple functions where we should pay attention to:
1. find_matching_existing_tags @/Users/bytedance/smartHistory/src/backend/agent/tools/tag_generator.py is using exact word match with exisiting tags. 
2. def _calculate_content_similarity @src/backend/agent/core/activity_matcher.py. This is using example word match.
Above are just some examples. A systematic problem those design expose is that we are not letting do their job: AI should be handling jobs like understand, summarizing, and matching at a certain stage. Worst case, we should use language to produce embedding (One proposal might be we can use AI's understanding of two events and then use embedding of AI's output, to calculate a precise simlarity score with cosine similarity.) In general, our current implementation is not AI native enough, not to mention agentic. If Agentic, we should delegate the job of when, and how do we regenerate tags to ai agent ( NOT there yet)

# Direction
We will focus on the following two directions
1. I will give you access to multiple Google Calendar, and more Notion Page to process
    This means, you will have more content to process and match, but it also means that we need to make a turn to a more AI agent/Agentic turn

2. We will update our agent structure (Currently our usage is hardly anything agentic). Much more job requirement will be delegated to AI to do, and we will less strictly rulinng but more prompt engineering to work on ( all prompt will be centered in /Users/bytedance/smartHistory/src/backend/agent/prompts/tag_prompts.py)
    One proposal would be that we spend a lot of time for the ai to process our Diary, Developer manual, and study events first, and we initiazed a knowledge center on an user image about user's past projects, project types, scopes, etc.




