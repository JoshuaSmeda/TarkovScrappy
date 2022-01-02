import discord
import os
import re
from keep_alive import keep_alive

client = discord.Client()

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

def run_query(query):
  import requests
  response = requests.post('https://tarkov-tools.com/graphql', json={'query': query})
  if response.status_code == 200:
    return response.json()
  else:
    raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

graphql_query = """
{
	quests {
        title
        objectives {
        type
			number
        targetItem {
            name
        }
        }
    }
}
"""

result = run_query(graphql_query)
hash_dict = dict()

def get_quest_item(search_item):
  for obj in result['data']['quests']:
    try:
      if (obj['objectives'][0]['type'] == 'find') or (obj['objectives'][0]['type'] == 'place'): # Handle find / place objective types
        for element in obj['objectives']:
          try:
            if re.search(search_item, element['targetItem']['name'], flags=re.IGNORECASE):
              hash_dict[obj['title']] = element['targetItem']['name'], element['number']
          except TypeError: pass
    except IndexError: pass

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg == '!quest':
    await message.channel.send('Give me the name of the item you want me to check if you should toss it, or keep it.')

  if msg.startswith('!quest'):
    item = msg.split("!quest ", 1)[1]
    item = item.strip()
    get_quest_item(item)
    if hash_dict:
      for i in hash_dict:
        await message.channel.send("```\nQuest name: %s\n\nItem required: %s\n\nNumber of required items: %s```" % (i, hash_dict[i][0], hash_dict[i][1]))
      hash_dict.clear()
    else:
      await message.channel.send("```\nI couldn't find any quest which requires %s.\n\nIf you think this is wrong, please ensure the provided item name is accurate...```" % item)

keep_alive()
client.run(os.getenv('TOKEN'))