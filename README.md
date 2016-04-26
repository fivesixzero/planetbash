# planetbash.py

Tired of losing track of your extractor timings? Don't want to click 10 times in existing character info apps to drill down to each character's PI info? This might be the tool for you! :D

As the project name suggests, this script was intended to be launched within a bash CLI environment. It may work in a pure Windows environment but I haven't tested that.

### Output:

```
$ ./planetbash.py 4
{12345678} Minmatar Citizen 19591231 (Corporaion Name Here) [Alliance Name Here]
--- LIST: Saranen I, Saranen II, Saranen III, Saranen IV, Saranen V
--- Next Expiration:    Wed, Apr 20 at 03:01 PM CDT
--- Time Until Expiry:  2 days, 20 hours, 34 minutes [Next: Saranen III]
{12345679} Amarr Citizen 75189232 (Corporaion Name Here) [Alliance Name Here]
--- LIST: Poitot I, Poitot II, Poitot III, Poitot IV, Poitot V
--- Next Expiration:    Wed, Apr 20 at 02:33 PM CDT
--- Time Until Expiry:  2 days, 20 hours, 6 minutes [Next: Poitot II]
{12345680} Gallente Citizen 859081023 (Corporaion Name Here) [Alliance Name Here]
--- LIST: B-R5RB I, B-R5RB II, B-R5RB III, B-R5RB IV, B-R5RB V, B-R5RB VI
--- Next Expiration:    ### EXPIRED ON Sun, 04/17 ###
--- Time Since Expiry:  1 days, 2 hours, 6 minutes --- EXPIRED! [First: B-R5RB V]
```

### Dependencies:

This was written for Python 2.7 so you'll need that installed.

Make sure these guys are available via 'pip install'!

* DateTime (4.0.1)
* tzlocal (1.2.2)

### Usage:

1. Clone this repo locally
2. Create `.eve_apis` CSV file
3. Run `./planetbash.py` at the CLI
4. Observe the short and simple next-expiration outupt

#### `.eve_apis` CSV file

To use this script all you've got to do is drop a few API keys (or a bunch of API kes) into a file named `.eve_apis` in the project root. The first line is ignored to allow for a proper `CSV` header.

```
id,verification,nickname,type
1234567,QVxblnXnr5FLWlWlkx4San0XMeHLygYz5zr6LhFcqyZ6LUakD5npFAhbd0glegPe,main account,char
1234568,o3YhqmeQtbITAZLkhadVha76i9d2LgXJsIkzUY1vdzW1Seqy4gg3NGIhWRcNqDCh,industry alts,char
1234569,MYhnV6RlzhzMA31L9iqi5rg6Zl3TBhuisdX1vR6pX6hgmbIeOTN7nVsfm7ukeV6Y,goon spy,char
1234570,Up1c1rwGqqiKefeYBb5gliZmk7yfzVgAVdynqyJ6SGtVsOVgW9erOqFnQZorZoCV,boring highsec guy,char
1234568,o3YhqmeQtbITAZLkhadVha76i9d2LgXJsIkzUY1vdzW1Seqy4gg3NGIhWRcNqDCh,corp key,corp
```

The `type` field should be either `char` or `corp` - anything else will be ignored. Corp keys are currently unused but may be used by future iterations.

*NOTE: The `.gitignore` file includes `.eve_apis` so this file will never be seen by git for commits! This repo doesn't want your API keys, ever. :)*

#### Running `planetbash.py` for all of your characters

To run the script on all of the keys simply build the CSV as noted above and execute `./planetbash.py`.

The script will run using all API keys in the `.eve_apis` CSV file one at a time.

### FAQ

Q: Why is this code so kludgy?

A: I've never built anything new in Python before! So I'm learning. If you have any suggestions, please submit a pull requiest or just let me know. :)

Q: Why a shell script?

A: Well, I've also never done anything with the EVE API (or any API) before, so this seemed like a good place to start since I have a ton of experience with shell scripting at my day job.

Q: Are you only making a shell script?

A: I hope not! Ideally I'd like to have this info displayed in a web app but that'll take some time - I really wanted to whip up a proof of concept to get this moving quickly. And in tne end, this turned out to be pretty neat! I actually use it daily to keep track of my 12 Planetary Interaction alt characters. So it seemed like a good time to share.

Q: What's this "Pew" thing?

A: Pew is an API wrapper originally developed by github user crsmithdev. I found it here on Github and liked the looks of it so I decided to fork it and start improving it. I've added that more up to date fork to this project and its good enough for the needs of this script. But it needs a lot more work! I'm only about 5% of the way through testing it out and I haven't done any work on the actual test script in there. So if you want to help, that'd be awesome.
