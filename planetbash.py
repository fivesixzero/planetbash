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
apiDateFormat   = '%Y-%m-%d %H:%M:%S'
localDateFormat = '%a, %b %d at %I:%M %p %Z'
shortDateFormat = '%a, %m/%d'
# what file are we reading APIs from?
API_CSV_FILENAME = '.eve_apis'
# pin typeIDs
commandTypes   = [2254,2524,2525,2533,2534,2549,2550,2551]
launchpadTypes = [2256,2542,2543,2544,2552,2555,2556,2557]
extractorTypes = [2848,3060,3061,3062,3063,3064,3067,3068]
storageTypes   = [2257,2535,2536,2541,2558,2560,2561,2562]
factoryTypes   = [2469,2471,2473,2481,2483,2490,2492,2493,2470,2472,2474,2480,2484,2485,2491,2494,2475,2482]
# content typeIDs
p0Types = [2073,2267,2268,2270,2272,2286,2287,2288,2305,2306,2307,2308,2309,2310,2311]
p1Types = [2389,2390,2392,2393,2395,2396,2397,2398,2399,2400,2401,3645,3683,3779,9828]
p2Types = [44,2312,2317,2319,2321,2327,2328,2329,2463,3689,3691,3693,3695,3697,3725,3775,3828,9830,9832,9836,9838,9840,9842,15317]
p3Types = [2344,2345,2346,2348,2349,2351,2352,2354,2358,2360,2361,2366,2367,9834,9846,9848,12836,17136,17392,17898,28974]
p4Types = [2867,2868,2869,2870,2871,2872,2875,2876]

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
    print 'keyid,verification,nickname,type'
    print '1234567,QVxblnXnr5FLWlWlkx4San0XMeHLygYz5zr6LhFcqyZ6LUakD5npFAhbd0glegPe,main account,char'
    print '1234568,o3YhqmeQtbITAZLkhadVha76i9d2LgXJsIkzUY1vdzW1Seqy4gg3NGIhWRcNqDCh,industry alts,char'
    print '1234569,MYhnV6RlzhzMA31L9iqi5rg6Zl3TBhuisdX1vR6pX6hgmbIeOTN7nVsfm7ukeV6Y,goon spy,char'
    print ''
    print 'Valid "type" entries are corp and char - items with other types will be ignored'
    print ''

def getApiListFromCSV(filename, type = 'char'):
    try: # is our CSV gonna open right?
        apiCSV = open(filename, 'rb')
        apiList = list(csv.reader(apiCSV, delimiter=',', quotechar='\''))
        apiCSV.close()
    except: # If not, lets print an example of what it should look like then quit
        printApiCSVExample()
        sys.exit(2)
    # Check list sanity
    for i in range(len(apiList)):
        apiId = apiList[int(i)][0]
        apiVerification = apiList[int(i)][1]
        apiNickname = apiList[int(i)][2]
        apiType = apiList[int(i)][3]
        if (i > 0) and (not (bool(re.match(r'[0-9]{7,}', apiId)) and bool(re.match(r'[0-9A-Za-z]{64}',apiVerification)))):
            printApiCSVExample()
            sys.exit(2)
    # if we're looking for character keys, do this
    if type == 'char':
        apiListOutput = []
        for i in range(len(apiList)):
            if apiList[i][3] == 'char':
                apiListOutput.append(apiList[i])
    elif type == 'corp':
        apiListOutput = []
        for i in range(len(apiList)):
            if apiList[i][3] == 'corp':
                apiListOutput.append(apiList[i])

    # Found good CSV? Found list sane? Lets return that list!
    return apiListOutput

def getPlanetDetails(p, charID):
    """INPUT: planet object
       OUTPUT: pins (pp), routes (pr), links (pl)"""
    # get pins
    pp = pew.char_planetary_pins(charID,p.planetID).pins
    # get routes
    pr = [] # not using routes or links yet, so why pull them?
    # pr = pew.char_planetary_routes(charID,p.planetID).routes
    # get  links
    pl = []
    #pl = pew.char_planetary_links(charID,p.planetID).links
    # pre-assign null value for last expire
    planetExpireDate = datetime.strptime("2285-09-09 11:11:11", apiDateFormat)
    lastPinExpireDate = datetime.strptime("2285-09-09 11:11:11", apiDateFormat)
    # round up important aggregate pin stats
    for pin in range(len(pp)):
        #
        typeID          = pp[pin].typeID
        typeName        = pp[pin].typeName
        contentQuantity = pp[pin].contentQuantity
        contentTypeID   = pp[pin].contentTypeID
        contentTypeName = pp[pin].contentTypeName
        cycleTime       = pp[pin].cycleTime
        expiryTime      = pp[pin].expiryTime
        #
        pinExpireDate = datetime.strptime(pp[pin].expiryTime,apiDateFormat)
        #
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
        #
    return pp, pr, pl, planetExpireDate, expireDate

def getPlanetSkillDetails(c):
    # CharacterSheet data:
    #
    charSheet = pew.char_character_sheet(c.characterID)
    #
    galIndustrialSkill = 0
    planetsSkill = 0
    upgradesSkill = 0
    #
    for n in range(len(charSheet.skills)):
        if charSheet.skills[n].typeID == 2495: # Interplanetary Consolodation
            planetsSkill = charSheet.skills[n].level
        elif charSheet.skills[n].typeID == 2505: # Command Center Upgrades
            upgradesSkill = charSheet.skills[n].level
        elif charSheet.skills[n].typeID == 3340: # Gallente Industrial
            galIndustrialSkill = charSheet.skills[n].level
    #
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
    #
    planetsMax = int(planetsSkill) + 1

    return charSheet, planetsMax, planetsSkill, planetsSkillString, upgradesSkill, upgradesSkillString, galIndustrialSkill

# start actual script here :)

# get our char api list
apiList = getApiListFromCSV(API_CSV_FILENAME,'char')

# iterate through list, starting with #1
for i in range(len(apiList)):
    #
    # Check input from CLI and assign
    apiId, apiVerification, apiNickname = apiList[i][0], apiList[i][1], apiList[i][2]
    #
    # init Pew XML API wrapper with our fresh pick
    pew = Pew(apiId,apiVerification)
    #
    charsPew = pew.acct_characters()
    #
    for c in charsPew.characters:
        #
        print '{%s} %s (%s) [%s]' % (c.characterID, c.name, c.corporationName, c.allianceName)
        #
        charSheet, planetsMax, planetsSkill, planesSkillString, upgradesSkill, upgradesSkillString, galIndustrialSkill = getPlanetSkillDetails(c)
        p = pew.char_planetary_colonies(c.characterID)
        planetCount = len(p.colonies)
        # initial vars for expireDate and lastPinExpireDate to start fresh on each character
        expireDate = datetime.strptime("2285-09-09 11:11:11", apiDateFormat)
        if planetCount > 0:
            planetNameList = []
            for n in range(len(p.colonies)):
                planetNameList.append(p.colonies[n].planetName)
                pp, pr, pl, planetExpireDate, expireDate = getPlanetDetails(p.colonies[n], c.characterID)
                # per planet last var assignments
                if planetExpireDate <= expireDate:
                    expireDate = planetExpireDate
                    planetExpiring = p.colonies[n].planetName
                # per planet loop ends
            # per char final var assignments
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

        if upgradesSkill == 5:
            print '*** UPGRADES SKILL MAXED ***'
        if planetCount < planetsMax:
            print '********************************'
            print '***   PLANETS AVAILABLE: %s   ***' % (planetsMax - planetCount)
            print '********************************'
        print '--- LIST: %s' % (", ".join(planetNameList))
        print '--- Next Expiration:    %s' % (expireDateLocal)
        print '--- %s %s' % (expiryString,expiryWhenString)

    print '=========='


exit()
