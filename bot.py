import discord
import asyncio
from discord.ext import commands
import base64
import numpy as np
import random
import PIL
from PIL import Image
from natsort import natsorted

bot = commands.Bot(command_prefix="#")


def readtoken():
    with open("Token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


TOKEN = readtoken()

@bot.event
async def on_ready():
    print("Bot is Ready")


@bot.command()
async def test(ctx):
    testmsg = await ctx.send("working")


bot.remove_command('help')


@bot.command()
async def help(ctx):
    await ctx.send(
        "How to use #deckcode: \n type #deckcode 'space' then paste in your decklist with cards in the format S0-XX (similar to the card library bot)\n"
        "How to use #showdeck: \n type #showdeck then the 'deckcode' generate from the '#deckcode' function \n "
        "If you're making a deck and don't want it to be shown on the main server, feel free to message the bot directly with commands \n"
        "How to use #draftpacks: \n type #draftpacks and then use reactions to pick your cards 1 by 1. Once you have picked 30 cards, build a 25 card deck out of them and play!\n"
        "You have 2 Minutes to pick each card, if the command times out you will have to start again. \n"
        "If there are any errors or somethings gone wrong ping @foatman1 as he's probably done something wrong")


@bot.command()
async def showdeck(ctx, arg):
    separation = int(arg.find("@"))
    setinfo = arg[:separation]
    encodednumberinfo = (arg[separation + 1:]).encode("utf-8")

    numberinfo = base64.b64decode(encodednumberinfo)
    numberinfo = str(int.from_bytes(numberinfo, 'big'))

    if len(numberinfo) == 73:
        numberinfo = "00" + numberinfo
    elif len(numberinfo) == 74:
        numberinfo = "0" + numberinfo

    deckdata = setinfo + numberinfo
    setinfo = deckdata[:-75]
    numberinfo = deckdata[-75:]
    numberinfo = [numberinfo[i:i + 3] for i in range(0, len(numberinfo), 3)]
    listofconvertednumbers = []
    for card in numberinfo:
        if card[0] == "0":
            listofconvertednumbers.append(card[1:])
        else:
            listofconvertednumbers.append(card)

    listofsetsused = []
    listofnumberofcardsperset = []
    position = 0
    while position != len(setinfo):
        if setinfo[position].isalpha():
            listofsetsused.append(setinfo[position] + setinfo[position + 1])
            position += 2
        else:
            if position + 2 > len(setinfo):
                listofnumberofcardsperset.append(setinfo[position])
                position += 1
            elif setinfo[position + 1].isnumeric():
                listofnumberofcardsperset.append(setinfo[position] + setinfo[position + 1])
                position += 2
            else:
                listofnumberofcardsperset.append(setinfo[position])
                position += 1

    setposition = 0
    listofcardsindeck = []
    while setposition != len(listofsetsused):
        cardsinset = listofconvertednumbers[0:int(listofnumberofcardsperset[setposition])]
        completedcards = [listofsetsused[setposition] + "-" + card for card in cardsinset]
        listofconvertednumbers = listofconvertednumbers[int(listofnumberofcardsperset[setposition]):]
        listofcardsindeck += completedcards
        setposition += 1
    demideckstring = ""
    for card in listofcardsindeck:
        if card.split("-")[0] == "S0":
            if len(card.split("-")[1]) == 2:
                demideckstring += "0" + card.split("-")[1]
            else:
                demideckstring += card.split("-")[1]
        elif card.split("-")[0] == "S1":
            demideckstring += str(130 + int(card.split("-")[1]))
    cardlibrary = {}
    with open("Card Library.txt") as f:
        for line in f:
            (key, val) = line.split("@")
            cardlibrary[key] = val
    decklist = []
    imagelist = []
    cardsindeck = {}
    dupedict = {}
    for card in listofcardsindeck:
        if listofcardsindeck.count(card) > 1:
            dupedict[card] = listofcardsindeck.count(card)
        NameNumber_Data = (cardlibrary.get(card)).split("Â£")  # [0] = NameNumber, [1] = Data
        cardsindeck[NameNumber_Data[0]] = NameNumber_Data[1].replace("\n", "")
    sortedcardsindeck = {}
    sorted_keys = sorted(cardsindeck, key=cardsindeck.get)
    for w in sorted_keys:  # sorting cards in deck
        sortedcardsindeck[w] = cardsindeck[w]
    for card in sortedcardsindeck:  # iterate through sorted decklist
        Name_Number = card.split("$")
        Number = Name_Number[1].split(".")
        if Number[0] in dupedict:
            i = 0
            while i < dupedict[Number[0]]:
                decklist.append(Name_Number[0])
                imagelist.append(Name_Number[1])
                i += 1
        else:
            decklist.append(Name_Number[0])
            imagelist.append(Name_Number[1])
    deckfile = open("Your Decklist.txt", "w")
    deckfile.write("Deck Code = " + arg + "\n")
    for card in decklist:
        deckfile.write(card + "\n")
    deckfile.write("\n")
    for cardnumber in imagelist:
        cardnumber = cardnumber.split(".")
        deckfile.write(cardnumber[0] + "\n")
    deckfile.write("MC PC String = " + demideckstring)
    deckfile.close()
    await ctx.send(file=discord.File("Your Decklist.txt"))
    await ctx.send("Creating deck image, this may take a few moments")
    imagelist = [PIL.Image.open(i) for i in imagelist]
    imagerow1 = imagelist[0:5]
    min_shape1 = sorted([(np.sum(i.size), i.size) for i in imagerow1])[0][1]
    images_comb1 = np.hstack((np.asarray(i.resize(min_shape1)) for i in imagerow1))
    images_comb1 = PIL.Image.fromarray(images_comb1)
    images_comb1.save("row1.png")
    imagerow2 = imagelist[5:10]
    min_shape2 = sorted([(np.sum(i.size), i.size) for i in imagerow2])[0][1]
    images_comb2 = np.hstack((np.asarray(i.resize(min_shape2)) for i in imagerow2))
    images_comb2 = PIL.Image.fromarray(images_comb2)
    images_comb2.save("row2.png")
    imagerow3 = imagelist[10:15]
    min_shape3 = sorted([(np.sum(i.size), i.size) for i in imagerow3])[0][1]
    images_comb3 = np.hstack((np.asarray(i.resize(min_shape3)) for i in imagerow3))
    images_comb3 = PIL.Image.fromarray(images_comb3)
    images_comb3.save("row3.png")
    imagerow4 = imagelist[15:20]
    min_shape4 = sorted([(np.sum(i.size), i.size) for i in imagerow4])[0][1]
    images_comb4 = np.hstack((np.asarray(i.resize(min_shape4)) for i in imagerow4))
    images_comb4 = PIL.Image.fromarray(images_comb4)
    images_comb4.save("row4.png")
    imagerow5 = imagelist[20:25]
    min_shape5 = sorted([(np.sum(i.size), i.size) for i in imagerow5])[0][1]
    images_comb5 = np.hstack((np.asarray(i.resize(min_shape5)) for i in imagerow5))
    images_comb5 = PIL.Image.fromarray(images_comb5)
    images_comb5.save("row5.png")
    verticalimages = ["row1.png", "row2.png", "row3.png", "row4.png", "row5.png"]
    verticalimages = [PIL.Image.open(i) for i in verticalimages]
    min_shapevertic = (1000, 280)
    imagescombinedfinal = np.vstack((np.asarray(i.resize(min_shapevertic)) for i in verticalimages))
    imgs_comb = PIL.Image.fromarray(imagescombinedfinal)
    imgs_comb.save("DeckImage.png")

    await ctx.send(file=discord.File("DeckImage.png"))


@bot.command()
async def deckcode(ctx, *deck):
    filelist = list(deck)
    filelist = [cardstring.upper() for cardstring in filelist]
    filelist = natsorted(filelist)  # sort cards into alphanumeric order
    listofsets = []  # create a list of what sets each card is in
    for card in filelist:
        cardset = card[0] + card[1]
        listofsets.append(cardset)
    listofcountedsets = natsorted([[x, listofsets.count(x)] for x in set(listofsets)])

    setdata = []
    for sublist in listofcountedsets:
        for item in sublist:
            setdata.append(str(item))

    listofcardnumbers = []  # create a list of the card number for each set
    for card in filelist:
        cardnumber = card[3:]
        if len(cardnumber) < 3:  # pad numbers with 2 or less digits so they remain equal size when encoded
            cardnumber = "0" + cardnumber
        listofcardnumbers.append(cardnumber)

    deckdata = setdata + listofcardnumbers  # add both lists of deck information together
    deckdata = "".join(deckdata)  # turn list into a string
    setinfo = deckdata[:-75]
    numberinfo = deckdata[-75:]

    bytelength = (int(numberinfo).bit_length() + 7) // 8
    numberinfo = int(numberinfo).to_bytes(bytelength, 'big')

    encodenumberinfo = base64.b64encode(numberinfo)
    encodenumberinfo = encodenumberinfo.decode("utf-8")

    encodeddeckdata = setinfo + "@" + encodenumberinfo
    await ctx.send(encodeddeckdata)
    await showdeck(ctx, encodeddeckdata)


@bot.command()
async def sealeddraft(ctx):
    await ctx.send("Creating Sealed Draft, this may take a few moments")
    cubecards = []
    with open("S1 Power Cube Card Numbers.txt") as f:
        for card in f:
            card = card.strip("\n") + ".png"
            cubecards.append(card)
    separator = cubecards.index("------.png")
    cubemonsters = cubecards[:separator]
    cubepowers = cubecards[separator + 1:]

    draftmonsters = random.sample(cubemonsters, 18)
    draftpowers = random.sample(cubepowers, 22)
    draftcards = draftmonsters + draftpowers
    images = [PIL.Image.open(i) for i in draftcards]
    imagerow1 = images[0:8]
    imagerow2 = images[8:16]
    imagerow3 = images[16:24]
    imagerow4 = images[24:32]
    imagerow5 = images[32:40]

    min_shape1 = sorted([(np.sum(i.size), i.size) for i in imagerow1])[0][1]
    min_shape2 = sorted([(np.sum(i.size), i.size) for i in imagerow2])[0][1]
    min_shape3 = sorted([(np.sum(i.size), i.size) for i in imagerow3])[0][1]
    min_shape4 = sorted([(np.sum(i.size), i.size) for i in imagerow4])[0][1]
    min_shape5 = sorted([(np.sum(i.size), i.size) for i in imagerow5])[0][1]
    images_comb1 = np.hstack((np.asarray(i.resize(min_shape1)) for i in imagerow1))
    images_comb1 = PIL.Image.fromarray(images_comb1)
    images_comb1.save("row1.png")
    images_comb2 = np.hstack((np.asarray(i.resize(min_shape2)) for i in imagerow2))
    images_comb2 = PIL.Image.fromarray(images_comb2)
    images_comb2.save("row2.png")
    images_comb3 = np.hstack((np.asarray(i.resize(min_shape3)) for i in imagerow3))
    images_comb3 = PIL.Image.fromarray(images_comb3)
    images_comb3.save("row3.png")
    images_comb4 = np.hstack((np.asarray(i.resize(min_shape4)) for i in imagerow4))
    images_comb4 = PIL.Image.fromarray(images_comb4)
    images_comb4.save("row4.png")
    images_comb5 = np.hstack((np.asarray(i.resize(min_shape5)) for i in imagerow5))
    images_comb5 = PIL.Image.fromarray(images_comb5)
    images_comb5.save("row5.png")
    verticalimages = ["row1.png", "row2.png", "row3.png", "row4.png", "row5.png"]
    verticalimages = [PIL.Image.open(i) for i in verticalimages]
    min_shapevertic = (1600, 280)
    imagescombinedfinal = np.vstack((np.asarray(i.resize(min_shapevertic)) for i in verticalimages))
    imgs_comb = PIL.Image.fromarray(imagescombinedfinal)
    imgs_comb.save("SealedDraftImage.png")
    await ctx.send(file=discord.File("SealedDraftImage.png"))


def generatepacks(numberofplayers):
    cubecards = []
    dictofpacks = {}
    with open("S1 120 Card Cube.txt") as f:
        for card in f:
            card = card.strip("\n") + ".png"
            cubecards.append(card)
    cubecards.remove("------.png")
    players = int(numberofplayers)
    # each pack is chosen randomly
    # for player in range(1, players + 1):
    #    dictofpacks[player] = random.sample(cubecards, 10)

    # each card in a draft round is unique
    cards = random.sample(cubecards, 10 * players)
    for player in range(players):
        dictofpacks[player + 1] = cards[player * 10:(player + 1) * 10]
    
    return dictofpacks

@bot.command()
async def adminunlockdraft(ctx):
    draftpacks.enabled = not draftpacks.enabled


@bot.command()
async def draftpacks(ctx):
    draftpacks.enabled = not draftpacks.enabled
    numberofplayers = 4
    numberofpacks = 4
    packsdrafted = 0
    playerpicks = []
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    #cards in this draft are not unique
    cubecards = []
    dictoftotalpacks = {}
    #open core set
    with open("CORESET70.txt") as f:
        for card in f:
            card = card.strip("\n") + ".png"
            cubecards.append(card)
    cubecards.remove("------.png")

    #addbuckets to draft
    with open("All Bucket Names.txt") as f:
        #select 9 filenames from list f
        numberofbuckets = 9
        info = f.read().split("\n")
        filenames = random.sample(info, numberofbuckets)
        for filename in filenames:
            filename = filename.strip("\n")
            with open(f'Buckets/{filename}') as h:
                for card in h:
                    card = card.strip("\n") + ".png"
                    cubecards.append(card)

    cards = random.sample(cubecards, 10 * numberofplayers * numberofpacks)
    for packnum in range(numberofplayers*numberofpacks):
        dictoftotalpacks[packnum + 1] = cards[packnum * 10:(packnum + 1) * 10]
    packcounter = 1
    for pack in range(numberofpacks):
        #set as active for different pack generation
        # dictofpacks = generatepacks(numberofplayers)
        dictofpacks = {}
        for pack in range(1, numberofplayers + 1):
            dictofpacks[pack] = dictoftotalpacks[packcounter]
            packcounter += 1
        for picknumber in range(len(dictofpacks[1])):  # repeats for each card in the pack
            #  player picks a card from the pack
            playerpackimages = [PIL.Image.open(i) for i in dictofpacks[1]]
            min_shape = sorted([(np.sum(i.size), i.size) for i in playerpackimages])[0][1]
            images_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in playerpackimages))
            images_comb = PIL.Image.fromarray(images_comb)
            images_comb.save("playerpack.png")
            pack = await ctx.send(file=discord.File("playerpack.png"))
            for emoji in range(len(dictofpacks[1])):
                await pack.add_reaction(reactions[emoji])
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Command Timed Out")
                await pack.delete()
            else:
                if str(reaction.emoji) == '1️⃣':
                    cardpicked = 1
                elif str(reaction.emoji) == '2️⃣':
                    cardpicked = 2
                elif str(reaction.emoji) == '3️⃣':
                    cardpicked = 3
                elif str(reaction.emoji) == '4️⃣':
                    cardpicked = 4
                elif str(reaction.emoji) == '5️⃣':
                    cardpicked = 5
                elif str(reaction.emoji) == '6️⃣':
                    cardpicked = 6
                elif str(reaction.emoji) == '7️⃣':
                    cardpicked = 7
                elif str(reaction.emoji) == '8️⃣':
                    cardpicked = 8
                elif str(reaction.emoji) == '9️⃣':
                    cardpicked = 9
                elif str(reaction.emoji) == '🔟':
                    cardpicked = 10
                
            await pack.delete()
            cardpicked = int(cardpicked) - 1
            playerpicks.append(dictofpacks[1][cardpicked])
            del dictofpacks[1][cardpicked]
            #  pick a random card in the other packs for the computers
            for computerpick in range(len(dictofpacks) - 1):
                del dictofpacks[computerpick + 2][random.randint(0, len(dictofpacks[computerpick + 2])) - 1]
            #  rotate the packs around
            keys_list = list(dictofpacks.keys())
            values_list = list(dictofpacks.values())
            values_list.insert(0, values_list.pop())
            dictofpacks = dict(zip(keys_list, values_list))
        packsdrafted += 1
        cardimages = [PIL.Image.open(i) for i in playerpicks]
        verticalimages = []
        for packpicks in range(packsdrafted):
            imagerow = cardimages[packpicks * 10:packpicks * 10 + 10]
            min_shape = sorted([(np.sum(i.size), i.size) for i in imagerow])[0][1]
            images_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imagerow))
            images_comb = PIL.Image.fromarray(images_comb)
            images_comb.save("pack" + str(packpicks + 1) + "picks.png")
            verticalimages.append("pack" + str(packpicks + 1) + "picks.png")
        verticalimages = [PIL.Image.open(i) for i in verticalimages]
        min_shapevertic = (2000, 280)
        imagescombinedfinal = np.vstack((np.asarray(i.resize(min_shapevertic)) for i in verticalimages))
        imgs_comb = PIL.Image.fromarray(imagescombinedfinal)
        imgs_comb.save("DraftPicks.png")
        currentpicksmsg = await ctx.send("Creating an image for current drafted cards")
        demistring = ""
        for card in playerpicks: #iterate through all picked cards and add them to demi's deck string format
            prefix, suffix = card.strip(".png").split("-")
            if len(suffix) <3:
                suffix = "0" + suffix
            if prefix == "S0":
                demistring += f"0{suffix}"
            elif prefix == "S1":
                demistring += f"1{suffix}"
            elif prefix == "KW":
                demistring += f"K{suffix}"
            elif prefix == "IT":
                demistring += f"D{suffix}"
        #maybe use playerpicks image to generate a deck string for demi's bot
        # demi bot string format: cards are XYYY, where X is the set prefix, and YYY is the card number in that set
        # s0 = 0, s1 = 1, k&w = K, ITD = D
        if 'currentpicks' in locals():
            await currentpicks.delete()
        currentpicks = await ctx.send(file=discord.File("DraftPicks.png"))
        await currentpicksmsg.delete()
    await ctx.send(f'Deck Code for Monster Club Deckbuilder:\n{demistring}')    
    draftpacks.enabled = not draftpacks.enabled

@bot.command()
async def generatebooster(ctx):
    numberofpackoptions = 4
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    selectmessage = await ctx.send("Select which booster you want to open. \nSeason 0 : 1️⃣ , Season 1 : 2️⃣ , Knights & Witches : 3️⃣ , Into the Dark : 4️⃣")
    for emoji in range(numberofpackoptions):
        await selectmessage.add_reaction(reactions[emoji])
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Command Timed Out")
        await selectmessage.delete()
    else:
        if str(reaction.emoji) == '1️⃣':
            packpicked = "S0"
        elif str(reaction.emoji) == '2️⃣':
            packpicked = "S1"
        elif str(reaction.emoji) == '3️⃣':
            packpicked = "KW"
        elif str(reaction.emoji) == '4️⃣':
            packpicked = "IT"
    await selectmessage.delete()
    generatingmessage = await ctx.send("Generating Pack Now")
    
    #generate random set of cards for that pack
    if packpicked == "S0":
        wholesetnumbers = range(75,131)
    elif packpicked == "S1":
        wholesetnumbers = range(55,111)
    elif packpicked == "KW" or packpicked == "IT":
        wholesetnumbers = range(1,64)
    cardnumbers = random.sample(wholesetnumbers, 9)
    cardindexs = []
    singledigits = [1,2,3,4,5,6,7,8,9]
    for number in cardnumbers:
        if number in singledigits:
            cardindexs.append(packpicked+"-0"+str(number)+".png")
        else:
            cardindexs.append(packpicked+"-"+str(number)+".png")
    
    
    cardpackimages = [PIL.Image.open(i) for i in cardindexs]
    min_shape = sorted([(np.sum(i.size), i.size) for i in cardpackimages])[0][1]
    images_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in cardpackimages))
    images_comb = PIL.Image.fromarray(images_comb)
    images_comb.save("boosterpack.png")
    pack = await ctx.send(file=discord.File("boosterpack.png"))
    await generatingmessage.delete()


bot.run(TOKEN)
