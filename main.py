'''
Copyright 2024 VitamineC
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the “Soft
ware”), to deal in the Software without restriction, including withou
t limitation the rights to use, copy, modify, merge, publish, distrib
ute, sublicense, and/or sell copies of the Software, and to permit pe
rsons to whom the Software is furnished to do so, subject to the foll
owing conditions:
The above copyright notice and this permission notice shall be includ
ed in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRE
SS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHAN
TABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
To do:
    1. [MEDI] de-nbted fish buckets
    2. [SEVE] auto-stop detection
    3. [INFO] get messages from chat
'''

import mcrcon
import time
import random
import sys
# import os

# For Convenience
rcon=mcrcon.MCRcon('127.0.0.1','123',25575)
command = rcon.command
sleep = time.sleep
class trigger:
    reset = 'scoreboard players set @a GameStart 0'
    enable = 'scoreboard players enable @a GameStart'
    test_start = 'xp add @p[scores={GameStart=1}] 0'
    test_stop = 'xp add @p[scores={GameStart=-1}] 0'
    test_shutdown = 'xp add @p[scores={GameStart=-25565}] 0'

# In-Game Cycle:
def onStart():
    command('gamerule sendCommandFeedback false')
    command('gamerule doImmediateRespawn true')
    command('scoreboard objectives remove death')
    command('scoreboard objectives add death deathCount')

    cmdResponse=command('bingo start')
    if cmdResponse!='':
        return
    command('tellraw @a {"text":"[bongo] Game starts in 10 seconds."}')
    cmdResponse=command(trigger.enable)
    command('tellraw @a ["[Bongo] 在游戏结束后，[",{"text":"点击此处","clickEvent":{"action":"run_command","value":"/trigger GameStart set -1"}\
                 ,"hoverEvent":{"action":"show_text","contents":"点击以停止游戏。"},"underlined":true,"bold":true},"] 以返回大厅。"]')

    sleep(7)
    command('execute in bingolobby:lobby positioned 0 64 0 run execute as @a[distance=..64] run scoreboard players set @s GameStart -1')
    for i in range(3,0,-1):
        command('tellraw @a [{"text":"[bongo] Game starts in "},{"text":"'+str(i)+'","bold":"true"}]')
        command('execute as @a at @s run playsound minecraft:block.note_block.bell music @s ~ ~ ~ 10 1')
        sleep(1)
    
    # Emergency Stop:
    cmdResponse=command(trigger.test_stop)
    if not cmdResponse.startswith('No'):
        command(trigger.reset)
        command('bingo stop')
        return
    
    x=random.randint(-1000000,1000000)
    z=random.randint(-1000000,1000000)

    # TP Trial & Test
    count_teleport=0
    temp_teleport ="spreadplayers "+str(x)+" "+str(z)+" 0 1 true @a"
    temp_test_teleport ='xp add @a[x='+str(x-5)+',dx=10,y=-64,dy=256,z='+str(z-5)+',dz=10] 0'
    cmdResponse=command(temp_teleport)
    tpResponse=cmdResponse
    sleep(1)
    cmdResponse=command(temp_test_teleport)
    
    # TP Rescue:
    while True:
        if not cmdResponse.startswith('No'):
            break
        else:
            print("Error caught: "+tpResponse)
            x=random.randint(-1000000,1000000)
            z=random.randint(-1000000,1000000)
            temp_teleport ="spreadplayers "+str(x)+" "+str(z)+" 0 1 true @a"
            temp_test_teleport ='xp add @a[x='+str(x-5)+',dx=10,y=-64,dy=256,z='+str(z-5)+',dz=10] 0'
            count_teleport+=1
            if count_teleport>5:
                command('tellraw @a ["[bongo][FATAL ERROR] Teleport failed after 5 trials!"]')
                break
            cmdResponse=command(temp_teleport)
            sleep(1)
            cmdResponse=command(temp_test_teleport)
        
    # After TP
    command('execute as @a at @s run playsound minecraft:block.note_block.bell music @s ~ ~ ~ 20 2')
    cmd_setspawn ="execute as @a at @s run spawnpoint @s ~ ~ ~"
    cmdResponse=command(cmd_setspawn)

    # In game:
    cmd_give_head="execute as @a[scores={death=1},gamemode=survival] run give @s "
    while True:
        sleep(2)
        command('execute in bingolobby:lobby positioned 0 64 0 run execute as @a[distance=..64] run scoreboard players set @s GameStart -1')
        cmdResponse=command(trigger.enable)
        cmdResponse=command(trigger.test_stop)
        if not cmdResponse.startswith('No'):
            command(trigger.reset)
            command('tp @a @r')
            sleep(1)
            command('bingo stop')
            break
        command(cmd_give_head+'minecraft:stone_axe{Enchantments:[{id:"minecraft:efficiency",lvl:2}]}')
        command(cmd_give_head+'minecraft:stone_pickaxe{Enchantments:[{id:"minecraft:efficiency",lvl:2}]}')
        command(cmd_give_head+'minecraft:stone_shovel{Enchantments:[{id:"minecraft:efficiency",lvl:2}]}')
        command(cmd_give_head+'minecraft:stone_sword')
        command(cmd_give_head+'minecraft:bread 4')
        cmdResponse=command('scoreboard players set @a[scores={death=1},gamemode=survival] death 0')
        return


# Main Cycle:
def main():
    command('scoreboard objectives remove GameStart')
    command('scoreboard objectives add GameStart trigger')
    command(trigger.reset)
    while True:
        sleep(2)
        cmdResponse=command(trigger.enable)
        cmdResponse=command(trigger.test_start)
        if not cmdResponse.startswith('No'):
            command(trigger.reset)
            onStart()
        # note: /trigger GameStart set -25565 to shutdown the server
        cmdResponse=command(trigger.test_shutdown)
        if not cmdResponse.startswith('No'):
            command(trigger.reset)
            command('stop')
            rcon.disconnect()
            break

if __name__ == "__main__":
    if len(sys.argv) == 1 :
        rcon=mcrcon.MCRcon('127.0.0.1','123',25575)
    elif len(sys.argv) == 4 :
        rcon=mcrcon.MCRcon(sys.argv[1],sys.argv[2],int(sys.argv[3]))
    else :
        print('incomplete: [<ip>, <password>, <port>]')
        exit()
    try:
        rcon.connect()
    except:
        try:
            rcon.connect()
        except:
            print('cannot connect!')
            exit()
    try:
        main()
    except KeyboardInterrupt:
        exit()
