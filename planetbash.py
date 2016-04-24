#!/usr/bin/env python

# TODO: Create capability for in-script "run through all in API CSV" functionality
# TODO: Enable the above most effectively by functionalizing stuff! Break it down!
#
# TODO [mid-term]: Create logic to decide what "type" planet is - P0/P1? Factory?
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

# static date string format vars
apiDateFormat = '%Y-%m-%d %H:%M:%S'
localDateFormat = '%a, %b %d at %I:%M %p %Z'
shortDateFormat = '%a, %m/%d'
# what file are we reading APIs from?
API_CSV_FILENAME = '.eve_apis'

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

def printApiCSVExample():
    print ''
    print 'CSV IMPORT FAILURE! Make sure .eve_apis exists here!'
    print ''
    print 'CSV format looks like this:'
    print ''
    print 'keyid,verification,nickname'
    print '1234567,QVxblnXnr5FLWlWlkx4San0XMeHLygYz5zr6LhFcqyZ6LUakD5npFAhbd0glegPe,main account'
    print '1234568,o3YhqmeQtbITAZLkhadVha76i9d2LgXJsIkzUY1vdzW1Seqy4gg3NGIhWRcNqDCh,industry alts'
    print '1234569,MYhnV6RlzhzMA31L9iqi5rg6Zl3TBhuisdX1vR6pX6hgmbIeOTN7nVsfm7ukeV6Y,goon spy'
    print ''

def getApiListFromCSV(filename):
    try:
        apiCSV = open(filename, 'rb')
        apiList = list(csv.reader(apiCSV, delimiter=',', quotechar='\''))
        apiCSV.close()
    except:
        printApiCSVExample()
        sys.exit(2)

    # Check list sanity
    for i in range(len(apiList)):
        apiId = apiList[int(i)][0]
        apiVerification = apiList[int(i)][1]
        apiNickname = apiList[int(i)][2]
        if (i > 0) and (not (bool(re.match(r'[0-9]{7,}', apiId)) and bool(re.match(r'[0-9A-Za-z]{64}',apiVerification)))):
            printApiCSVExample()
            sys.exit(2)

    # Found good CSV? Found list sane? Lets return that list!
    return apiList

def getTodoArg(args):
    if (len(args) == 2) and (bool(re.match(r'[0-9]+', args[1]))):
        return int(args[1])
    else:
        if len(args) > 2:
            print '\nToo many arguments. Only provide a single integer, please'
        else:
            print '\nNo valid argument provided.'
        return False

def getApiFromList(apiList,todo):
    # Is a safe todo item coming into us from arguments?
    if todo and todo <= len(apiList) and todo is not 0:
        apiPick = apiList[int(todo)]
    else:
        print '\nPlease pick one of the following keys or type "quit" to exit.\n'
        for line in range(len(apiList)):
            if line >= 1:
                print '%s) %-15s [Key ID: %s]' % (line,apiList[line][2],apiList[line][0])
        print ''
        # input loop
        while True:
            todoInput = raw_input("Key to use: ")
            if todoInput == 'quit' or todoInput == 'q': sys.exit(1)
            elif (not todoInput.isdigit()) or todoInput == '0':
                print "ERROR: Please enter a valid item number."
            elif int(todoInput) not in range(len(apiList)):
                print "ERROR: Sorry, %s isn't in our list." % (todoInput)
            else:
                break
        apiPick = apiList[int(todoInput)]
        # end input loop
    return apiPick[0], apiPick[1], apiPick[2]

# Work out what to do based on our input arg and the CSV contents
# todo: add some command-line switches... more/less char detail, more/less planet deets

# for now we just care about TodoArg - in the future we'll add switches. :)
todo = getTodoArg(sys.argv)

# Check input from CLI and assign
apiId, apiVerification, apiNickname = getApiFromList(getApiListFromCSV(API_CSV_FILENAME),todo)

# init Pew XML API wrapper with our fresh pick
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
        galIndustrialSkill = 0
        planetsSkill = 0
        upgradesSkill = 0

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
        # 'lastUpdate', 'numberOfPins', 'ownerID', 'ownerName', 'planetID', 'planetName',
        # 'planetTypeID', 'planetTypeName', 'solarSystemID', 'solarSystemName', 'upgradeLevel'
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

            planetNameList = []
            planetExpireDate = datetime.strptime("2285-09-09 11:11:11", apiDateFormat)

            for n in range(len(p.colonies)):

                planetNameList.append(p.colonies[n].planetName)

                # PER PLANET PINS DATA:
                # Each pin is a planet facility.
                #
                # 'contentQuantity', 'contentTypeID', 'contentTypeName', 'cycleTime', 'expiryTime',
                # 'installTime',  'lastLaunchTime', 'latitude', 'longitude', 'pinID', 'quantityPerCycle',
                # 'schematicID', 'typeID', 'typeName'
                #
                # contentTypeIDs: P0 [1032,1033,1035], P1 [1042], P2 [1034], P3 [1040], P4 [1041]
                # -- Gathered from invTypes table in SDE

                pins = pew.char_planetary_pins(c.characterID,p.colonies[n].planetID)

                for pin in range(len(pins.pins)):

                    commandTypes = [2254,2524,2525,2533,2534,2549,2550,2551]
                    launchpadTypes = [2256,2542,2543,2544,2552,2555,2556,2557]
                    extractorTypes = [2848,3060,3061,3062,3063,3064,3067,3068]
                    storageTypes = [2257,2535,2536,2541,2558,2560,2561,2562]
                    factoryTypes = [2469,2471,2473,2481,2483,2490,2492,2493,2470,2472,2474,2480,2484,2485,2491,2494,2475,2482]

                    p0Types = [2073,2267,2268,2270,2272,2286,2287,2288,2305,2306,2307,2308,2309,2310,2311]
                    p1Types = [2389,2390,2392,2393,2395,2396,2397,2398,2399,2400,2401,3645,3683,3779,9828]
                    p2Types = [44,2312,2317,2319,2321,2327,2328,2329,2463,3689,3691,3693,3695,3697,3725,3775,3828,9830,9832,9836,9838,9840,9842,15317]
                    p3Types = [2344,2345,2346,2348,2349,2351,2352,2354,2358,2360,2361,2366,2367,9834,9846,9848,12836,17136,17392,17898,28974]
                    p4Types = [2867,2868,2869,2870,2871,2872,2875,2876]

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
                            planetExpireDate = pinExpireDate
                            lastPinExpireDate = pinExpireDate

                    elif typeID in storageTypes:
                        pinType = 'storage'
                    elif typeID in factoryTypes:
                        pinType = 'factory'
                    else:
                        pinType = 'unknown'

                    # per pin loop ends

                # per planet last var assignments

                if planetExpireDate <= expireDate:
                    expireDate = planetExpireDate
                    planetExpiring = p.colonies[n].planetName

                # per planet loop ends

            # per char last var assignments

            if expireDate > datetime.now():
                expireDateLocal = datetime.strftime(utc_to_local(expireDate),localDateFormat)
                expireDelta = expireDate - datetime.utcnow()
                timeToExpire = timedelta_to_string(expireDelta)
                expiryWhenString = '%s [Next: %s]' % (timeToExpire,planetExpiring)
                expiryString = 'Time Until Expiry: '
            else:
                expireDateLocal = '### EXPIRED ON %s ###' % (datetime.strftime(utc_to_local(expireDate),shortDateFormat))
                expireDelta = datetime.utcnow() - expireDate
                timeSinceExpire = timedelta_to_string(expireDelta)
                expiryWhenString = '%s --- EXPIRED! [First: %s]' % (timeSinceExpire,planetExpiring)
                expiryString = 'Time Since Expiry: '

            # per char loop ends

        # END PLANET DATA LOOP
        # This runs if the character has zero planets
        else:
            expireDateLocal = '### None to Expire! ###'
            expiryString = '[you really should set up some planets]'
            expiryWhenString = ''
            planetNameList = []

        if upgradesSkill = 5:
            print '*** UPGRADES SKILL MAXED ***'
        if planetCount < planetsMax:
            print '********************************'
            print '***   PLANETS AVAILABLE: %s   ***' % (planetsMax - planetCount)
            print '********************************'
        print '--- LIST: %s' % (", ".join(planetNameList))
        print '--- Next Expiration:    %s' % (expireDateLocal)
        print '--- %s %s' % (expiryString,expiryWhenString)
exit()
