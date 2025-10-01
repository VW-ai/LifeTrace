# Future Development To Be considered
This file contains tasks about features we could be focuing on after we finished our MVP as described in our PRD `PRODUCT.md`
All task are to be organized in the following way:
1. Priority: Ranked from P0(Highest), P1(Medium) to P2(Lowest)
2. Feature: A very brief name/ description of the feature that we intent to work on.
3. Type: Wether this is a product-oriented or a technical-oriented task.
4. Description: detail explanation of what I want to achieved.
5. Projection: Random thoughts on how this functionality is going to be

# Task Lists
This is the tasks lists for future development
## 1. More Accurate/Detailed/Flexible Tagging System
1. Priority: P0
2. Feature: Enable the system to handle activities of granularities.
3. Type: Technical
4. Description: Two things:
    4.1 Our tagging agent is not grasping the nature of our events very well. We need to improve that.
        We can work with this in 2 ways:
        4.1.1 better prompt engineering
        4.1.2 Use some existing system/models/methodology that good at tagging (it should be publicly available because companies use this a lot at resume tagging)
    4.2 An improved tag generation system
        Currently, we only generate tags that is very abstract, and we even have a mechanism that excludes us from getting to0 specific (system-wide tag regeneration). We will need some additional check, to allow us to remember, and store, and resuse (tags of) a project that maybe lasts 3 months. We can have more general tags on top of it, and we should, so that if we go about Coding section, we can expand it to different dimension:
            a. Acitivty: then we have things like debugging, PRD writing, testing, new feature development (Just an example)
            b. Project: Life2Notion, SmartHistory, CompanyProject1, etc.
            ...
        Some ideas on what might help us accomplishing this:
        1. Simple RAG
        2. Context engineering
        3. An multiple agent framework( not too hype for this)
5. Projection: Essentially, expand from this, I think we will make this a big data platform, essentially, process data in stream and in batch. 

## 2. Manual Processing
1. Priority: P2
2. Feature: Enable User to Customize the Way how Tagging workds
3. Type: Product
4. Description: Add a portal in our application, where user can input an prompt in terms of how does the user want their activites are organized (e,g. focusing on sports acitvity). 
An related functionality would be this one. 
making the useer manually selected a time range, and generate tags for this period
5. Projection: We can build a chat bot I think, to chat with data/raw texts.


## 3. Manual Selected Time/Detail Granularity Tag Generation
1. Priority: P2
2. Feature: allows user to regnerate tags with more customization
3. Type: Product
4. Description: This milestone complements for LLM's uncontrollable nature. Will have three main functionality:
    a. Re-Generate Tags for Activity in an selected time range:
        Making the generation more focus, this time range will be the GLOABL-SCALE at generation
    b. Select/Delete Generated Tags, Add Manual Tags, and request regeneration.

