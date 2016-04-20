#!/usr/bin/env python

# TODO: Create capability for in-script "run through all in API" functionality
# TODO: Enable the above most effectively by functionalizing stuff! Break it down!
#
# TODO [long-term]: Add quick check for broken routes!
# TODO [long-term]: Add "time to done" for factory planets

import sys
import csv
from Pew.pew import Pew
import datetime as dt
from datetime import datetime
from datetime import timedelta
from tzlocal import get_localzone
import calendar
import pytz
import re

# assign our local TZ based on this system's local TZ at runtime.

local_tz = get_localzone()

# shifts a datetime into local timezone
def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

# Takes timedelta input, converts timedelta.total_seconds() to a string we can display
def timedelta_to_string(timedelta):
    seconds = int(expireDelta.total_seconds())
    days, remainder1 = divmod(seconds, 86400)
    hours, remainder2 = divmod(remainder1, 3600)
    minutes, seconds = divmod(remainder2, 60)
    return '{} days, {} hours, {} minutes'.format(days, hours, minutes)

apiDateFormat = '%Y-%m-%d %H:%M:%S'
localDateFormat = '%a, %b %d at %I:%M %p %Z'
shortDateFormat = '%a, %m/%d'

# Work out what to do based on our input arg and the CSV contents
# todo: add some command-line switches... more/less char detail, more/less planet deets

if len(sys.argv) > 1:
    todo = int(sys.argv[1])
else:
    todo = 'nope'

# Try to open the CSV file containing API keys.
# If we fail, provide some details and an error.

try:
    apiCSV = open('.eve_apis', 'rb')
except:
    print ''
    print 'CSV IMPORT FAILURE! Make sure .eve_apis exists here!'
    print ''
    print 'CSV format is: keyid,verification,nickname with a key on the first line'
    print ''
    raise
    exit(1)

# Create a list from the CSV and close the file handle

apiList = list(csv.reader(apiCSV, delimiter=',', quotechar='\''))
apiCSV.close()

# Check entire csv for sanity - we don't want to do anything unless we know the CSV is legit.
for i in range(len(apiList)):
    apiId = apiList[int(i)][0]
    apiVerification = apiList[int(i)][1]
    apiNickname = apiList[int(i)][2]
    if (i > 0) and (not (re.match('[0-9]{7}', apiId) and re.match('[0-9A-Za-z]{64}',apiVerification))):
        apiOK = 'false'
        print 'ERROR: API key nicknamed "%s" is bad! Please fix .eve_apis file and try again.' % (apiNickname)
        print ''
        print 'ID:           {%s}' % (apiId)
        print 'Verification: {%s}' % (apiVerification)
        print 'Nickname:     {%s}' % (apiNickname)
        print ''
        print 'CSV format is: keyid,verification,nickname with a key on the first line'
        print ''
        raise
        exit(1)

# Check input from CLI and assign
if type(todo) == int:
    apiPick = apiList[int(todo)]
else:
    print ''
    print 'Please pick one of the following keys or type "quit" to exit.'
    print ''
    for line in range(len(apiList)):
        if line >= 1:
            print '%s) %s [ID: %s]' % (line,apiList[line][2],apiList[line][0])
    print ''

    def pickApi(apiListInput):
        todoInput = raw_input("Key to use: ")
        # handle quit request
        if todoInput == 'quit' or todoInput == 'q':
            print "ERROR: Quitting!"
            exit()
        # handle non-digit
        if not todoInput.isdigit():
            print "ERROR: Please enter only an item number."
            pickApi(apiListInput)
        # if our input definitely is a digit, lets make sure its an int
        else:
            todoInput = int(todoInput)
        # is this int within our list of keys? if so, return our pick!
        if todoInput in range(len(apiListInput)):
            apiSelection = apiList[todoInput]
            return(apiSelection)
        else:
            print "ERROR: Sorry, this isn't in our list: %s" % (todoInput)
            pickApi(apiListInput)

    apiPick = pickApi(apiList)

apiId = apiPick[0]
apiVerification = apiPick[1]
apiNickname = apiPick[2]

# announce key we're using:
#print '==='
#print 'Using API Key for nickname [%s]' % (apiNickname)
#print '==='

# init Pew XML API wrapper
pew = Pew(apiId,apiVerification)

# Using "try" here because if this doesn't work, the rest of the script is gonna fail miserably.

try:

    #
    # PER-ACCOUNT CHARACTER LIST DATA:
    #
    # 'allianceID', 'allianceName', 'characterID', 'corporationID', 'corporationName', 'factionID', 'factionName', 'name'

    charsPew = pew.acct_characters()

except:

    print 'API or Pew error %s' + e
    print ''
    raise
    exit(1)

else:

    for c in charsPew.characters:

        print '{%s} %s (%s) [%s]' % (c.characterID, c.name, c.corporationName, c.allianceName)

        # CharacterSheet data:

        charSheet = pew.char_character_sheet(c.characterID)

        # SKILLS DATA:
        #
        # For this script there are only three skills we really care about since
        # they're arguably the only ones that affect Planetary Interaction

        spTotal = 0

        for n in range(len(charSheet.skills)):
            spTotal += charSheet.skills[n].skillpoints
            if charSheet.skills[n].typeID == 3340: # Gallente Industrial
                galIndustrialSkill = charSheet.skills[n].level
            if charSheet.skills[n].typeID == 2495: # Interplanetary Consolodation
                planetsSkill = charSheet.skills[n].level
            if charSheet.skills[n].typeID == 2505: # Command Center Upgrades
                upgradesSkill = charSheet.skills[n].level

        # PLANETS DATA:
        #
        # 'lastUpdate', 'numberOfPins', 'ownerID', 'ownerName', 'planetID', 'planetName', 'planetTypeID', 'planetTypeName', 'solarSystemID', 'solarSystemName', 'upgradeLevel'
        #
        ###
        ### TODO -- More work with expire dates! Grab then more intelligently.
        ###         Current state is dumb - only really grabs last one.
        ### TODO -- Make use of shiny new pew function eve_type_name() to display what planet's working on
        ### TODO -- Add details on what's on each planet, capacity, link status, etc.
        ### TODO -- Grab data from another API (eve-marketdata?) to determine per-planet revenues? (!)
        ###

        planetsMax = int(planetsSkill) + 1

        if planetsSkill == 5:
            planetsSkillString = '- MAXED PLANETS'
        elif planetsSkill == 4:
            planetsSkillString = ''
        elif planetsSkill <= 3:
            planetsSkillString = '- NEEDS TRAINING'
        #
        if upgradesSkill == 5:
            upgradesSkillString = '- MAXED UPGRADES'
        elif upgradesSkill == 4:
            upgradesSkillString = ''
        elif upgradesSkill <= 3:
            upgradesSkillString = '- NEEDS TRAINING'

        p = pew.char_planetary_colonies(c.characterID)

        planetCount = len(p.colonies)

        # initial vars for expireDate and lastPinExpireDate to start fresh on each character
        expireDate = datetime.strptime("2285-09-09 11:11:11", apiDateFormat)
        lastPinExpireDate = expireDate

        if planetCount > 0:

            for n in range(len(p.colonies)):

                # PER PLANET PINS DATA:
                # Each pin is a planet facility.
                #
                # 'contentQuantity', 'contentTypeID', 'contentTypeName', 'cycleTime', 'expiryTime', 'installTime',  'lastLaunchTime', 'latitude', 'longitude', 'pinID', 'quantityPerCycle', 'schematicID', 'typeID', 'typeName'
                #
                # contentTypeIDs: P0 [1032,1033,1035], P1 [1042], P2 [1034], P3 [1040], P4 [1041]
                # -- Gathered from invTypes table in SDE

                pins = pew.char_planetary_pins(c.characterID,p.colonies[n].planetID)

                for pin in range(len(pins.pins)):

                    commandTypes = [2254, 2524, 2525, 2533, 2534, 2549, 2550, 2551]
                    launchpadTypes = [2256, 2542, 2543, 2544, 2552, 2555, 2556, 2557]
                    extractorTypes = [2848, 3060, 3061, 3062, 3063, 3064, 3067, 3068]
                    storageTypes = [2257, 2535, 2536, 2541, 2558, 2560, 2561, 2562]
                    factoryTypes = [2469, 2471, 2473, 2481, 2483, 2490, 2492, 2493, 2470, 2472, 2474, 2480, 2484, 2485, 2491, 2494, 2475, 2482]

                    typeID = pins.pins[pin].typeID
                    typeName = pins.pins[pin].typeName
                    contentQuantity = pins.pins[pin].contentQuantity
                    contentTypeID = pins.pins[pin].contentTypeID
                    contentTypeName = pins.pins[pin].contentTypeName
                    cycleTime = pins.pins[pin].cycleTime
                    expiryTime = pins.pins[pin].expiryTime

                    pinExpireDate = datetime.strptime(pins.pins[pin].expiryTime,apiDateFormat)

                    if typeID in commandTypes:
                        pinType = 'command'
                    elif typeID in launchpadTypes:
                        pinType = 'launchpad'
                    elif typeID in extractorTypes:
                        pinType = 'extractor'
                        if (pinExpireDate <= lastPinExpireDate) and (expireDate <= lastPinExpireDate):
                            expireDate = pinExpireDate
                            lastPinExpireDate = pinExpireDate
                    elif typeID in storageTypes:
                        pinType = 'storage'
                    elif typeID in factoryTypes:
                        pinType = 'factory'
                    else:
                        pinType = 'unknown'

                planetName = p.colonies[n].planetName
                planetTypeName = p.colonies[n].planetTypeName
                structures = p.colonies[n].numberOfPins
                pID = str(p.colonies[n].planetID)

            if expireDate > datetime.now():
                expireDateLocal = datetime.strftime(utc_to_local(expireDate),localDateFormat)
                expireDelta = expireDate - datetime.now()
                timeToExpire = timedelta_to_string(expireDelta)
                expiryWhenString = '%s' % (timeToExpire)
                expiryString = 'Time Until Expiry: '
            else:
                expireDateLocal = '### EXPIRED ON %s ###' % (datetime.strftime(utc_to_local(expireDate),shortDateFormat))
                expireDelta = datetime.now() - expireDate
                timeSinceExpire = timedelta_to_string(expireDelta)
                expiryWhenString = '%s --- EXPIRED!' % (timeSinceExpire)
                expiryString = 'Time Since Expiry: '
        # END PLANET DATA LOOP
        # This runs if the character has zero planets
        else:
            expireDateLocal = '### None to Expire! ###'
            expiryString = '[you really should set up some planets]'

 #       print '---'
        if planetCount < planetsMax:
            print '********************************'
            print '***   PLANETS AVAILABLE: %s   ***' % (planetsMax - planetCount)
            print '********************************'
        #print '--- Gal Ind Skill:      %s' % (galIndustrialSkill)
        #print '--- Upgrades Skill:     %s %s' % (upgradesSkill,upgradesSkillString)
        #print '--- Planet Count:       %s %s' % (planetCount,planetsSkillString)
        print '--- Next Expiration:    %s' % (expireDateLocal)
        print '--- %s %s' % (expiryString,expiryWhenString)
exit()

