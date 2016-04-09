#!/usr/bin/env python

# TODO [DONE 4/8]: Load API keys in external file (~/.eapi?)
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

# Try to open the CSV file containing API keys.
# If we fail, provide some details and an error.

try:
    apiCSV = open('.eve_apis', 'rb')
except:
    print ''
    print 'CSV IMPORT FAILURE! Make sure .eve_apis exists here!'
    print ''
    print 'CSV should be: keyid,verification,nickname'
    print ''
    raise
    exit(1)

# Create a list from the CSV and close the file handle

apiList = list(csv.reader(apiCSV, delimiter=',', quotechar='\''))
apiCSV.close()

# Work out what to do based on our input arg and the CSV contents

if len(sys.argv) > 1:
    todo = int(sys.argv[1])
else:
    todo = 'nope'

if type(todo) == int:
    apiId = apiList[int(todo)][0]
    apiVerification = apiList[int(todo)][1]
    apiNickname = apiList[int(todo)][2]
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
        #
        # 'DoB', 'bloodLine', 'bloodLineID', 'certificates', 'characterID', 'cloneJumpDate', 'cloneName', 'cloneSkillPoints', 'cloneTypeID', 'corporationID', 'corporationName', 'corporationRoles', 'corporationRolesAtBase', 'corporationRolesAtHQ', 'corporationRolesAtOther', 'corporationTitles', 'factionID', 'factionName', 'freeRespecs', 'freeSkillPoints', 'gender', 'homeStationID', 'implants', 'jumpActivation', 'jumpCloneImplants', 'jumpClones', 'jumpFatigue', 'jumpLastUpdate', 'lastRespecDate', 'lastTimedRespec', 'name', 'race', 'remoteStationDate', 'skills'
        #
        # Many of these end up as lists. IE, need "range(len(charSheet.skills))" to walk through skills.
        #

        charSheet = pew.char_character_sheet(c.characterID)

        dob = charSheet.DoB
        bal = charSheet.balance
        fsp = charSheet.freeSkillPoints
        respecs = charSheet.freeRespecs

        spTotal = 0
        spNot5s = 0
        spLvl5s = 0
        skillsTotal = 0

        # SKILLS DATA:
        #
        # 'level', 'published', 'skillpoints', 'typeID'
        #
        #
        #

        for n in range(len(charSheet.skills)):
#            skillsTotal += 1
#            if charSheet.skills[n].level == 5:
#                spLvl5s += 1
#            else:
#                spNot5s +=1
            spTotal += charSheet.skills[n].skillpoints
            if charSheet.skills[n].typeID == 2495: # Interplanetary Consolodation
                planetsSkill = charSheet.skills[n].level
            if charSheet.skills[n].typeID == 2505: # Command Center Upgrades
                upgradesSkill = charSheet.skills[n].level
            if charSheet.skills[n].typeID == 3340: # Gallente Industrial
                galIndustrialSkill = charSheet.skills[n].level

        # PLANETS DATA:
        #
        # 'lastUpdate', 'numberOfPins', 'ownerID', 'ownerName', 'planetID', 'planetName', 'planetTypeID', 'planetTypeName', 'solarSystemID', 'solarSystemName', 'upgradeLevel'
        #
        ###
        ### TODO -- More work with expire dates! Current state is dumb - only really grabs last one.
        ### TODO -- Time math!!! Consider double-extract planets maybe.
        ### TODO -- Find FIRST expiring planet to save to a var?
        ### TODO -- Work through pins to find per-planet resources?
        ### TODO -- Grab data from another API (eve-marketdata?) to determine per-planet revenues? (!)
        ### TODO -- Make use of shiny new pew function eve_type_name() to display what planet's working on
        ### TODO -- Add details on what's on each planet, capacity, etc.
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

        if planetCount > 0:

            for n in range(len(p.colonies)):

                # PER PLANET PINS DATA:
                # Each pin is a planet facility.
                #
                # 'contentQuantity', 'contentTypeID', 'contentTypeName', 'cycleTime', 'expiryTime', 'installTime',  'lastLaunchTime', 'latitude', 'longitude', 'pinID', 'quantityPerCycle', 'schematicID', 'typeID',     'typeName'
                #
                # contentTypeIDs: P0 [1032,1033,1035], P1 [1042], P2 [1034], P3 [1040], P4 [1041]
                # -- Gathered from invTypes table in SDE

                pins = pew.char_planetary_pins(c.characterID,p.colonies[n].planetID)

                nonExtractors = 0
                extractors = 0

                for pin in range(len(pins.pins)):

                    #debug
                    # print "--- Planet: %s: PIN typeID: %s, EXPIRY: %s" % (p.colonies[n].planetName, pins.pins[pin].typeID, pins.pins[pin].expiryTime)

                    if pins.pins[pin].expiryTime.startswith('0001'):
                        nonExtractors += 1
                    else:
                        extractors += 1
                        expireDate = datetime.strptime(pins.pins[pin].expiryTime,apiDateFormat)

                planetName = p.colonies[n].planetName
                planetTypeName = p.colonies[n].planetTypeName
                structures = p.colonies[n].numberOfPins
                pID = str(p.colonies[n].planetID)

                #debug
                # print '--- Planet %s: %s,\t%s\t[%s], {%s}' % (pseq, planetName, planetTypeName, structures, pID)

            if expireDate > datetime.now():
                expireDateLocal = datetime.strftime(utc_to_local(expireDate),localDateFormat)
                expireDelta = expireDate - datetime.now()
                timeToExpire = timedelta_to_string(expireDelta)
                expiryWhenString = '%s' % (timeToExpire)
                expiryString = 'Time Until Expiry: '
            else:
                print 'DATE is in the PAST'
                expireDateLocal = '### EXPIRED ON %s ###' % (datetime.strftime(utc_to_local(expireDate),shortDateFormat))
                expireDelta = datetime.now() - expireDate
                timeSinceExpire = timedelta_to_string(expireDelta)
                expiryWhenString = '%s ###==  EXPIRED ALREADY!  ==###' % (timeSinceExpire)
                expiryString = 'Time Since Expiry: '

        else:

                expireDateLocal = '### None to Expire! ###'
                expiryString = '[you really should set up some planets]'

 #       print '---'
        if planetCount < planetsMax:
            print '********************************'
            print '***   PLANETS AVAILABLE: %s   ***' % (planetsMax - planetCount)
            print '********************************'
        balInt = int(float(bal))

        print '--- Gal Ind Skill:      %s' % (galIndustrialSkill)
        print '--- Upgrades Skill:     %s %s' % (upgradesSkill,upgradesSkillString)
        print '--- Planet Count:       %s %s' % (planetCount,planetsSkillString)
        print '--- Planets Expire:     %s' % (expireDateLocal)
        print '--- %s %s' % (expiryString,expiryWhenString)
exit()

