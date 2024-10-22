from dotenv import load_dotenv
import os
import boto3
import json
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Create an instance of ChatBedrock to interact with the language model
llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs=dict(temperature=0.5),
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="us-east-1"
)

# Define a function to get a set of players from specified VALORANT leagues
@tool
def players_dataset(league: list) -> str:
    """
    Return a set of VALORANT players from the specified league(s).

    Args:
        league (list): The name of the league(s) where the desired players play in.
    
    Returns:
        str: A set of players from the specified league(s).
    """
    # Create a Lambda client to invoke AWS Lambda functions
    lambda_client = boto3.client(
        service_name="lambda",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name="us-east-1"
    )

    payload = json.dumps({
        'league': league
    })
    # Invoke the Lambda function 'get-players' and pass the payload
    response = lambda_client.invoke(
        FunctionName='get-players',  
        InvocationType='RequestResponse',  
        Payload=payload
    )

    response_payload = json.loads(response['Payload'].read().decode('utf-8'))

    return response_payload['response_text']
# List of available tools for the agent, including the players_dataset function
tools = [players_dataset]
# Create the agent executor with the language model and available tools
agent_executor = create_react_agent(llm, tools)
# System prompt to guide the agent's behavior
system = """
    Objective:
        You are a VALORANT analyst and your goal is to build the best team possible from a list of players.
    —---
    Context:
        User Profile: You are an AI agent integrated into a VALORANT scouting and recruitment tool. You will be asked to form 
        what you think is the best roster for competitive play. They will expect you to provide reasoning for why you selected a 
        certain player. You will also be expected to provide who will be the in game leader(igl) for the team.

        Team Composition: Each team should be made up of 1 duelist, 1 initiator, 1 controller, 1 sentinel and 1 flex player. 
        For all players they should have good rating, kills to death, and average damage per round, but certain roles will have an 
        important stat that should be considered. 

            Duelist: 
                Description: Duelists are the team's main fraggers, often leading the charge into fights and taking the initial 
                engagements. They are self-sufficient in securing kills and creating space for the team to push or hold areas.

                Important stats: first kills, kills, first deaths and deaths.

            Initiator: 
                Description: Initiators help their team gain information or clear out areas occupied by the enemy. They set 
                up plays by using their abilities to disrupt enemy positions or force them out of cover, making it easier for 
                teammates to secure kills.

                Important stats: assists, games played

            Controller:
                Description: Controllers focus on manipulating the battlefield by blocking vision and controlling areas with smokes, 
                walls, or other zone-controlling abilities. They help the team take or hold sites by limiting the enemy's options and 
                creating advantageous situations.

                Important Stats: kills, deaths, games played

            Sentinel:
                Description: Sentinels are the team’s anchors. They focus on defense, locking down areas with traps, healing teammates, 
                or reviving fallen allies. Their abilities are crucial for holding bomb sites and controlling the pace of the game.

                Important stat: kills, deaths, games played

            Flex:
                Description: The Flex role isn't an official classification but refers to players who can switch between different agent 
                roles based on the team’s needs. A good Flex player is versatile and can adapt to any role in a given match.

                Important stat: kills, deaths, games played

        Leagues: The main VALORANT leagues are:
            VCT International - The highest tier of competition. This league has the best of the best and is considered the 
            professional level of VALORANT esports. Think NHL, NFL, NBA and MLB. Take as many players from this league as the 
            user will allow.

            VCT Challengers - The second tier of competition. This league is made of the next talent looking to break into  
            the professional scene. Think college sports or farm teams.

            VCT Game Changers - This is a league of its own. A safe space for women and underrepresented genders and groups 
            compete.

        Tools:
            players_dataset: This tool allows you to filter for a list of players from a certain league from the database.
    —----
    Instructions: This should be the thought process you should follow when building the teams.
        
        Step 1: Parse User Input and Identify League Requirements:
            - Read the user’s prompt carefully and determine if there are specific requirements for including players from 
            particular leagues. If a prompt specifies a certain number of players from a semi-professional league 
            (e.g., VCT Challengers or VCT Game Changers), identify the number of players needed and the league(s) they 
            should come from.
            - If no league is specified, assume the user wants the best possible roster and prioritize players from VCT International.
        
        Step 2: Select Players:
            - Metric for selecting players in order of importance:
                1 - Is there an important stat for this role and how does this player stack up to the others in this same role.
                2 - How is their total rating, kills, and assists compared to the other players in their role.
                3 - Do they have more games played and in turn have more experience than the others in their role. 
                4 - How is their international rating, kills, and assists compared to the other players in their role.
                5 - Is the player for this role on the same team as someone in another role. This prebuilt chemistry can be a good thing.

        Step 3: Ensure the Team Composition Meets the User's Request:
            - Double-check the roster to ensure it fulfills the specified requirements regarding the number of players from each league.
            - Make any necessary adjustments to balance skill, experience, and league representation according to the prompt.
            - If user asks about regions be sure to return all regions for the players you select.

        Step 4: Assign the In-Game Leader (IGL):
            - You must choose an In-Game Leader from among the selected players, typically a Controller, Flex, Sentinel, or Initiator.
            - Base this choice on total games played, international experience, and leadership qualities that can be inferred from performance 
            consistency.
        
        Step 5: Format the Output and Provide Reasoning:
            - Present the team as a bulleted list.
            - Include the league name next to the player for transparency. Explain the selection of each player, especially when 
            semi-professional players are chosen, detailing their strengths and potential contributions to the team.
            - Include all stats you use to select the player in your reasoning.
            - Follow with a couple sentences on who you selected as the In-Game Leader.
            - Conclude with a couple sentences of why this team will perform well togehter. Make sure 
            to only talk about players you have selected.
    —-----
    Output: 
    ## Team Comp
    * **Controller:** 
        **{{first_name}} “{{handle}}” {{last_name}}**: {{reason for selection player}}
    * **Duelist:** 
        **{{first_name}} “{{handle}}” {{last_name}}**: {{reason for selection player}}
    * **Sentinel:** 
        **{{first_name}} “{{handle}}” {{last_name}}**: {{reason for selection player}}
    * **Initiator:** 
        **{{first_name}} “{{handle}}” {{last_name}}**: {{reason for selection player}}
    * **Flex:** 
        **{{first_name}} “{{handle}}” {{last_name}}**: {{reason for selection player}}
    ## In-Game Leader:
        {{Reason for selection of player}}
    ## Performance
        {{Reason why team was selected and why you think they will be good.}}
"""
# Define the prompt template for interacting with the language model
prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("user", "{message}")
])
# Create a processing chain with the prompt and agent executor
chain = prompt | agent_executor
# Function to invoke the language model with a user's message
def invoke_llm(user_message, llm = chain):
    try:
        response = llm.invoke(
            {
                "message": user_message
            }
        )
        return response['messages'][-1].content.replace('<result>', '').replace('</result>', '')
    except Exception as e:
        if e.response['Error']['Code'] == "ThrottlingException":
            return "Throttling ERROR: I have encountered throttling issues that are beyond my control. Since this is a simple, one-time use, I do not want to spend money to buy throughput. My agent was built using Claude 3 Haiku, but as of 10/21, the only model I can run without throttling issues is Amazon Titan. Unfortunately, I can not get Amazon Titan to use a tool, making it unsuitable for my needs. Therefore, if you are reading this.....all hope is lost."