import json
import pandas as pd
import boto3

# Initialize an S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Retrieve the CSV file from the S3 bucket
    bucket_name = 'vct-hackathon-hcg'
    obj = s3.get_object(Bucket=bucket_name, Key='weighted_players.csv')
    df = pd.read_csv(obj['Body'])

    # Get the list of leagues from the event input
    league_list = event.get('league')
    
    roles = ['Duelist', 'Initiator', 'Controller', 'Sentinel', 'Flex']
    role_groups = {}
    for role in roles:
        players_list = []
        for league in league_list:
            # Filter players to control number of input tokens.
            filtered_df = df[
                (df['agent_role'] == role) & 
                (df['league'] == league) & 
                (df['total_games'] > 10) & 
                (df['total_rating'] > .45)
            ]
            ordered_df = filtered_df.sort_values(['total_games'], ascending=False)
            top_players = ordered_df.head(5)
            players_list.extend(top_players.to_dict('records'))
        role_groups[role] = players_list
    
    # Prepare the result text summarizing the top players for each role
    result_text = (
        f"The top Controller players: {role_groups['Controller']}, "
        f"The top Duelist players: {role_groups['Duelist']}, "
        f"The top Initiator players: {role_groups['Initiator']}, "
        f"The top Flex players: {role_groups['Flex']}, "
        f"The top Sentinel players: {role_groups['Sentinel']}"
    )
    
    # Return the result as a JSON response
    return {
       "response_text":  json.dumps(result_text)
    }