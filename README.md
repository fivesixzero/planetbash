# planetbash.py

Tired of losing track of your extractor timings? Don't want to click 10 times in existing character info apps to drill down to each character's PI info? This might be the tool for you! :D

As the project name suggests, this script was intended to be launched within a bash CLI environment. It may work in a pure Windows environment but I haven't tested that.

### Output:

```
$ ./planetbash.py 4
===
Using API Key for nickname [account two]
===
{11111111} Chracter Name1 (Corporation Name One) [Alliance One]
--- Gal Ind Skill:      3
--- Upgrades Skill:     5 - MAXED PLANETS
--- Planet Count:       6 - MAXED PLANETS
--- Planets Expire:     ### EXPIRED ON Wed, 04/06 ###
--- Time Since Expiry:  2 days, 7 hours, 43 minutes --- EXPIRED!
{11111111} Chracter Name2 (Corporation Name Two) [Alliance Two]
--- Gal Ind Skill:      3
--- Upgrades Skill:     4
--- Planet Count:       5
--- Planets Expire:     Fri, Apr 08 at 10:17 PM EDT
--- Time Until Expiry:  0 days, 1 hours, 17 minutes
{11111111} Chracter Name3 (Corporation Name Three) [Alliance Three]
--- Gal Ind Skill:      2
--- Upgrades Skill:     4
--- Planet Count:       5
--- Planets Expire:     Fri, Apr 08 at 10:52 PM EDT
--- Time Until Expiry:  0 days, 1 hours, 52 minutes
```

### Dependencies:

This was written for Python 2.7 so you'll need that installed.

Make sure these guys are available via 'pip install'!

* DateTime (4.0.1)
* tzlocal (1.2.2)

### Usage:

#### `.eve_apis` CSV file

To use this script all you've got to do is drop a few API keys (or a bunch of API kes) into a file named `.eve_apis` in the project root. The first line is ignored to allow for a proper `CSV` header.

'''
id,verification,nickname
1234567,QVxblnXnr5FLWlWlkx4San0XMeHLygYz5zr6LhFcqyZ6LUakD5npFAhbd0glegPe,main account
1234568,o3YhqmeQtbITAZLkhadVha76i9d2LgXJsIkzUY1vdzW1Seqy4gg3NGIhWRcNqDCh,industry alts
1234569,MYhnV6RlzhzMA31L9iqi5rg6Zl3TBhuisdX1vR6pX6hgmbIeOTN7nVsfm7ukeV6Y,goon spy
1234570,Up1c1rwGqqiKefeYBb5gliZmk7yfzVgAVdynqyJ6SGtVsOVgW9erOqFnQZorZoCV,boring highsec guy
'''

*NOTE: The `.gitignore` file includes `.eve_apis` so this file will never be seen by git for commits!*

#### Command Line Arguments

If planetbash.py is run without any arguments and proper a `.eve_apis` CSV file is present, it'll display the following output.

```
$ ./planetbash.py

Please pick one of the following keys and use the number at the left as an argument.

1) main account [ID: 1234567]
2) industry alts [ID: 1234568]
3) goon spy [ID: 1234569]
4) boring highsec guy [ID: 1234570]
```

To run planetbash.py with the "goon spy" key above, run the following:

```
$ ./planetbash.py 3
```

#### Running `planetbash.py` for all of your characters

To run the script on all of the keys simply wrap it in a for loop:

```
for i in {1..4}; do ./planetbash.py; done
```

### FAQ

Q: Why is this code so kludgy?

A: I've never built anything new in Python before! So I'm learning. If you have any suggestions, please submit a pull requiest or just let me know. :)

Q: Why a shell script?

A: Well, I've also never done anything with the EVE API (or any API) before, so this seemed like a good place to start since I have a ton of experience with shell scripting at my day job.

Q: Are you only making a shell script?

A: I hope not! Ideally I'd like to have this info displayed in a web app but that'll take some time - I really wanted to whip up a proof of concept to get this moving quickly. And in tne end, this turned out to be pretty neat! I actually use it daily to keep track of my 12 Planetary Interaction alt characters. So it seemed like a good time to share.

Q: These expiration times seem wonky. What gives?

A: Since I'm new to Python I'm still learning to wrangle lists and juggle variables properly. As soon as I figure that out the extractor expiration times are going to be more accurate! Right now its just pulling the expiration date of the last extractor on the last planet because, well, that was good enough for me to make this proof of concept work. But I don't like it and it'll be one of the first things I address.

Q: What's this "Pew" thing?

A: Pew is an API wrapper originally developed by github user crsmithdev. I found it here on Github and liked the looks of it so I decided to fork it and start improving it. I've added that more up to date fork to this project and its good enough for the needs of this script. But it needs a lot more work! I'm only about 5% of the way through testing it out and I haven't done any work on the actual test script in there. So if you want to help, that'd be awesome.
