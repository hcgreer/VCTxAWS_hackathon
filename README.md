# VCTxAWS_hackathon
# Project Overview
This project aims to build an AI-powered assistant for creating the best competitive VALORANT roster. The assistant focuses on player statistics, experience on a regional and international level, roles, and team chemistry to construct the optimal roster. A tool like this could be useful for scouting or recruiting.

# Function and Features
- **League Filter:** The assistant filters players based on the different VALORANT leagues to ensure rosters are composed of players from the desired league.
- **Role Prioritization:** The assistant accounts for the need to have one player in each role (duelist, initiator, controller, sentinel, and flex). It also considers the purpose of each role and the stats that indicate a good player for each position.
- **Roster Selection:** The assistant suggests rosters by analyzing total and international performance stats. The stats include games played, rating, kills, deaths, assists, damage per round, headshot percentage, first kills, and first deaths. It also considers a player's overall experience (number of games played) and potential past chemistry (if the players have been on the same team before).
- **In-Game Leader:** The assistant selects the In-Game Leader by choosing the most experienced player on the roster, with a heavy emphasis on international experience.
- **Team Performance:** The assistant provides reasoning for why it believes the selected roster will perform at the top of the competition in VALORANT.

# Methodology
## Data
- The only data used was provided by Riot Games.
- Data processing involved multiple steps:
  - The game data was split into smaller chunks to calculate total stats per game for overall player totals.
  - Once stats were totaled by match, a rating system was designed to rate each player, using a weighted average favoring recent performances.
  - The tournament, player, and team datasets were used to find current teams and regions of players. Players who had not played a game in 2024 were not considered.
  - Analysis determined each player's role. Players with a play rate above 55% for a certain role were labeled as that role. Those with a 25%-55% play rate in two or more roles were labeled as flex players.
  - The data was then merged to include a player's current team, region, role, total, and international stats.

## Model
- The roster generation relies on a weight- and rules-based approach powered by Claude 3 Haiku on Amazon Bedrock. The model is prompted with a description of team needs and uses a set of criteria to suggest the best roster.
- The agent has access to a single tool, allowing it to retrieve a list of players from one or multiple leagues.
- Instead of using a knowledge base, the model was prompted with a brief description of each role and the key stats to prioritize when selecting a player for that role. Additionally, a short description was provided for each league in VALORANT esports.

## Output
- The model outputs a roster with one player per role, a selection for the In-Game Leader, and its reasoning behind the roster selection.

# Findings and Learnings
Going into this project, I had never worked with LLMs, agents, knowledge bases, or AWS. I had a good understanding of VALORANT as a fan of the esport, which was my main advantage. However, I gained a lot of knowledge through this project and believe there is real potential to create a solid scouting agent if provided with the right information. Seeing what the assistant is capable of with just prompt engineering, I am eager to revisit this project with more time to improve the prompt and add new features to the agent.
