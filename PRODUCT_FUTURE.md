# Future Development To Be considered
This file contains tasks about features we could be focuing on after we finished our MVP as described in our PRD `PRODUCT.md`
All task are to be organized in the following way:
1. Priority: Ranked from P0(Highest), P1(Medium) to P2(Lowest)
2. Feature: A very brief name/ description of the feature that we intent to work on.
3. Type: Wether this is a product-oriented or a technical-oriented task.
3. Description: detail explanation of what I want to achieved.

# Task Lists
This is the tasks lists for future development
## 1. More Detailed/Flexible Tagging System
1. Priority: P1
2. Feature: Enable the system to handle activities of granularities.
3. Type: Product
4. Description: Currently, we only generate tags that is very abstract, and we even have a mechanism that excludes us from getting to specific (system-wide tag regeneration). We will need some additional check, to allow us to remember, and store, and resuse (tags of) a project that maybe lasts 3 months. We can have more general tags on top of it, and we should, so that if we go about Coding section, we can expand it to different dimension:
    a. Acitivty: then we have things like debugging, PRD writing, testing, new feature development (Just an example)
    b. Project: Life2Notion, SmartHistory, CompanyProject1, etc.
    ...
Essentially, expand from this, I think we will make this a big data platform, essentially, process data in stream and in batch. 