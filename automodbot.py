#March 2020, Egor 'asbestos' Khramenko

import discord
import json

#client has to be initialized before any of the functions. 
#the rest of startup shit is at the very bottom, cause it has to
#be initialized after all the functions. 

print('starting...')
client = discord.Client()

#==========<MEAT>====================================
@client.event
async def on_ready():
    '''
    called when discord.Client() initialization is successful.
    tldr this is mostly for debug purposes and some utility.
    '''
    
    #debug dump
    print(f'im logged in as {client.user}')
    print(f'live on the following servers: {client.guilds}')
    #print(f'or maybe these: {await client.fetch_guilds().flatten()}')
    print(f'i can see these channels: {[f"{_.name} ({_.id}) in {_.guild}" for _ in client.get_all_channels()]}')
    
    #if there is no command listening channel present in the config.json, get one
    if not config['command_channels']:
        comm_ch = None
        while comm_ch is None:
            try:
                comm_ch = await client.fetch_channel(input('please input a valid channel id for commands: '))
            except Exception as e:
                print(e)
            print(comm_ch, comm_ch.id)
        config['command_channels'].append(comm_ch.id)
        config_dump(config)
        
    #more debug dump
    print(f'command channels: {config["command_channels"]}')
    print('--------READY--------\n')
    

@client.event
async def on_message(message):
    '''
    called on every new visible message. 
    determines what to do with the said message.
    '''
    
    #is it my own (bot's) message?
    if message.author == client.user:
        return
    
    #is it a command in a command listening channel? if not, its a normal message
    if message.content.startswith(config['command_char']) and message.channel.id in config['command_channels']:
        await process_command(message)
    else:
        analyse_message(message)


async def process_command(message):
    '''
    determine tokens, ie what command has been issued and with what arguments.
    tokens = command name + all arguments
    do correct shit acordingly
    '''
    
    print(f'processing the following command: {message.clean_content}')
    
    #extract tokens. first token in the list is the command name, the rest are arguments. 
    tokens = message.clean_content[1:].split()
    
    #case for unrecognized command 
    if tokens[0] not in config['valid_commands']:#locals():
        await message.channel.send(f'Sorry, I don\'t recognize that command: ` {tokens[0]} `')
    else:
        return_message = 'this shouldnt happen, have a look at the terminal' #debug purposes
        try:
            print(f'trying to call {tokens[0]} with {tokens[1:]} and message object') #more debug
            
            #try calling the function with said arguments. 
            #ngl imho this is a really shitty way of doing this.
            #important note: every callable function should return a status string, indicationg whether
            #an operation was a success or not. This status string is then posted to the channel. 
            return_message = globals()[tokens[0]](*tokens[1:], message=message) #probably a bad idea now that i think about it
        except TypeError as e:
            #you passed wrong argument set to the function
            return_message = f'Wrong command arguments provided: {tokens[1:]}\n```{e}```'
        except Exception as e:
            #something else happened 
            return_message = f'Something went wrong here\n```{e}```'
        finally:
            #post results
            await message.channel.send(return_message)


def command_char(char, message=None):
    '''
    change the command character. ! is default. 
    todo: make it dump new character to config.json with config_dump()
    '''
    
    print('attempting to change command character') #debug 
    if len(char) == 1: #make sure its a singular character
        config['command_char'] = char
        return f'Success! The new command character is: ` {char} `'
    else:
        return f'Cannot set ` {char} ` as a command character'
    
def here(message=None):
    '''placeholder'''
    pass
    
def echo(message=None):
    '''placeholder'''
    pass

def greet(*args, message=None):
    '''
    mostly for debugging purposes to test the process_command() functionality. 
    funky discord markdown:
    `code line`
    ```code block```
    >>>quote
    '''
    print(f'test command, args: {args}, message: {message.clean_content}')
    return f'''Hello!\nIf you\'re seeing this, looks like everything is working! 
You have passed these on to me:```{args}```in this message:\n>>> {message.clean_content}'''


def analyse_message(message):
    '''
    scan the message for undesirable content. 
    atm just dumps some debug info. 
    todo: actually make it work lol
    '''
    
    auth = message.author
    content = message.clean_content
    print(f'\nanalysing the following message:\n\'\'\'\n{content}\n\'\'\'')
    print(f'author: {f"{auth.nick}/{str(auth)}" if isinstance(auth, discord.Member) else f"{auth.name}/{str(auth)}"}')
    print(f'type: {message.type}')
    print(f'attachments: {[a.filename for a in message.attachments]}')

def config_dump(config):
    '''redump config.json'''
    print('dumping json config')
    with open('config.json', mode='w') as file:
        file.write(json.dumps(config, indent = 4))

def config_load():
    '''load or reload config.json, sometimes good to use after dump'''
    with open('config.json', mode='r') as file:
        config = json.loads(file.read())
        print('----loading json config--------')
        print(config)
        print('-------------------------------') 
        return config

#======</MEAT>=====================================


#this is the rest of the bot initialization 
config = config_load()

#in config.json you gotta list all usable by the bot functions
if not set(config['valid_commands']).issubset(globals().keys()):
    #you listed a command that doesnt actually exist          ...yet
    raise NameError('Command(s) specified in the config file are not defined.')


print('token:', config['token'], flush=True)

#run the blasted thing already
client.run(config['token'])