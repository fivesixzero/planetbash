#!/usr/bin/env python

# TODO: Create capability for in-script "run through all in API" functionality
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
    print 'CSV format be: keyid,verification,nickname with a key on the first line'
    print ''
    raise
    exit(1)

# Create a list from the CSV and close the file handle

apiList = list(csv.reader(apiCSV, delimiter=',', quotechar='\''))
apiCSV.close()

if type(todo) == int:
    apiId = apiList[int(todo)][0]
    apiVerification = apiList[int(todo)][1]
    apiNickname = apiList[int(todo)][2]
    if not (re.match('[0-9]{7}', apiId) and re.match('[0-9A-Za-z]{64}',apiVerification)):
        apiOK = 'false'
        print 'ERROR: API key nicknamed "%s" is bad! Please fix .eve_apis file and try again.' % (apiNickname)
        print ''
        print 'ID:           {%s}' % (apiId)
        print 'Verification: {%s}' % (apiVerification)
        print 'Nickname:     {%s}' % (apiNickname)
        exit(1)
    print '==='
    print 'Using API Key for nickname [%s]' % (apiNickname)
    print '==='
    pew = Pew(apiId,apiVerification)
else:
    print ''
    print 'Please pick one of the following keys and use the number at the left as an argument.'
    print ''
    for line in range(len(apiList)):
        if line >= 1:
            print '%s) %s [ID: %s]' % (line,apiList[line][2],apiList[line][0])
    print ''
    exit(1)

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

        for n in range(len(charSheet.skills)):
#            spTotal += charSheet.skills[n].skillpoints
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

        if upgradesSkill == 5:
            upgradesSkillString = '- MAXED UPGRADES'
        elif upgradesSkill == 4:
            upgradesSkillString = ''
        elif upgradesSkill <= 3:
            upgradesSkillString = '- NEEDS TRAINING'

        p = pew.char_planetary_colonies(c.characterID)

        planetCount = len(p.colonies)

        # initial vars for expireDate and lastPinExpireDate
        #
        expireDate = datetime.strptime("2300-01-01 00:00:00", apiDateFormat)
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

                nonExtractors = 0
                extractors = 0

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
        print '--- Gal Ind Skill:      %s' % (galIndustrialSkill)
        print '--- Upgrades Skill:     %s %s' % (upgradesSkill,upgradesSkillString)
        print '--- Planet Count:       %s %s' % (planetCount,planetsSkillString)
        print '--- Planets Expire:     %s' % (expireDateLocal)
        print '--- %s %s' % (expiryString,expiryWhenString)
exit()

