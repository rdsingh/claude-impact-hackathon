We are leaning towards "Neighborhood Issue Tracker — Combine 311 data, code enforcement records, and police call data from the Open Data Portal to visualize and track quality-of-life issues by neighborhood over time."



I need you to follow these rules given to us:





Use city data responsibly. Use public APIs and open data. Do not scrape or abuse city systems.



Code must be in a public GitHub repo. Judges need to be able to review your code. You're free to make the repo private after the hackathon closes.



Create a checkpoint at the end of each phase. I must confirm when a phase is complete.



Judging Criteria

Each project will be scored across four categories on a 1-5 scale (1 = minimal, 5 = exceptional), for a maximum of 20 points. But I am only providing the descriptions for Score 4 and 5, as our focus is to keep our phase execution in that range only.



1. Civic Impact (4-5)

Does this solve a real problem for San Diego residents, city staff, or the community?

Judges should ask: Would someone actually use this?

Score | Description

5 | Addresses a clear, pressing civic need with a compelling use case

4 | Solves a real problem with a well-defined audience



Bonus consideration: Solutions that enable broader access -- such as MCP servers, CLIs, or agentic tools that others can build on -- should be rewarded.



2. Use of City Data (4-5)

How effectively does the project leverage San Diego's open data, municipal code, council records, or other city resources?

Score | Description

5 | Deeply integrates multiple city data sources in a meaningful way

4 | Strong use of at least one city data source with clear value



Bonus consideration: Projects that creatively combine datasets (e.g., joining permit data with zoning codes, enriching 311 data with budget info) should be rewarded.



3. Technical Execution (4-5)

Does it work? Is the demo functional and reasonably polished for a hackathon timeframe?

Score | Description

5 | Fully functional, polished, and well-scoped for the time available

4 | Working demo with minor rough edges



A focused, working MVP beats an ambitious idea that crashes during the demo. Judges should reward smart scoping.



4. Presentation & Story (4-5)

Did the team clearly communicate what they built, why it matters, and who it's for?

Score | Description

5 | Compelling narrative, clear demo, and strong delivery

4 | Well-structured presentation with a clear problem/solution arc



A strong demo tells a story: here's the problem, here's how we solve it, here's what it looks like in action.



Total Score possible: 20



We want to divide the hackathon into 4 phases. Use the most optimal model for each phase in an effort to use tokens wisely and optimally.



Phase 1: Research and planning .

Success criteria for this phase:





Requirements are documented.



Data sources identified - 311 data, code enforcement records, and police call data



ESRI API integration details documented - including API Key, data schema, ability to push data to ESRI APIs in the correct format for rendering in the Maps GUI



Expected tokens required for each phase. This will become important in Phase-4 during the demo and presentation phase where we would like to present a sustainability argument around the use of AI-powered infrastructure for building complex applications such as this.



Identify Testing strategy.



Data has been downloaded and placed in the project workspace



Context file is updated.



Phase 2: Engineering phase including programming front-end, back-end, API integration, MCP Server Setup, Data analysis.

Success criteria for this phase:





Workspace and project structure for front-end, back-end, MCP servers, environment detail is appropriately setup.



For major functionality code, the comment should be sufficient but not verbose.



Test plan is drafted based on Phase-1 outcome.



Functional objectives of the hackathon are complete. I will provide more details on this separately.



End to end connectivity with ESRI is complete via MCP server - this will include sending data to ESRI API in the acceptable format that can be rendered in Maps by ESRI.



Context file is refined.



Phase-3: Testing end to end.

Success criteria:





End to end testing with test results documented - including test coverage, pass and fail metrics.



Context file is refined.



Phase-4: Demo, Presentation, and wrap-up

Creating a slide-deck less than 10 slides -





Team name





Problem statement -- what civic problem are you solving?



What it does -- a short paragraph describing the application



Data sources used -- which city datasets or resources your project uses



Architecture / approach -- brief description (or diagram) of how the pieces fit together



Links -- URL to the live application, if deployed



Demo video -- a 60-second walkthrough of the application. Optional if your app is deployed and accessible via a public link; required if it is not.



Context file is refined.



Product Metrics for the following categories: code coverage, comments, unit test, integration test, security vulnerabilities. Provide top 2 To-Dos in each of these categories as next steps (if applicable)



Also produce metrics around the use of tokens in each of these 4 phases, and mention the model that was used.
