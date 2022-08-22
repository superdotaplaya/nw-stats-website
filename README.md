![image](https://user-images.githubusercontent.com/22628539/185342924-31a11309-a5ef-42f4-8120-58ef4b36a641.png)

**NW-Stats.com is a stat tracking website for the New World game made by Amazon Game Studios.**

This website uses screenshots of war scoreboards submitted by the community to gather stats about players. All stats are recorded into a database that allows for data analysis to take place and offer it to the players! See below for a list of features that are currently implemented on the website! This project has been created in Python using the Flask framework for loading webpages and information into them.

							War stat submission

![image](https://user-images.githubusercontent.com/22628539/185343098-37bd7470-469e-4cfa-bbe4-0186f99f8204.png)

  War stats are submitted in our official discord server (which is linked on the website), in conjunction witha discord bot I created, it takes those screenshots and uses the Microsoft Computervision API to get all of the data we need! From there we verify the data is correct, and then run a bot command to add the stats to the databse.

						Discord Login and Verification System
![image](https://user-images.githubusercontent.com/22628539/185343191-77456ff6-44e5-4fb6-8c02-dc9d8ed3c19a.png)
![image](https://user-images.githubusercontent.com/22628539/185343284-0e13baa8-c143-4c58-82d2-530c77a432b3.png)

  Users are able to login using Discords Oauth system to customize their own experience on the website. Users are able to change the colors of the site, and various elements, add their character name and server to get quick access to their own stats via a "profile" button in the header! Users are able to request verification by posting a screenshot of their character bio screen in game in our discord from the same account they logged into the website from. Once verified users are able to edit whawt role they played in each war, as well as add videos to their profile to show their gameplay to those that view it.

							Stat Analysis:
![image](https://user-images.githubusercontent.com/22628539/185343387-d467a211-9eac-4610-9a08-5cacce3c6738.png)

  All stats are recorded into a databse and are sorted by war. Users are able to use the index to select a war to view. When they select a war it will load the scorebaord (all 100+ players for that war). The scoreboard can be sorted by the varios metrics used to analayze a players performance (healing, damage, kills, assists, etc.). On the scoreboard users can click on a players name to view that players profile. At the bottom of each war scoreboard page there are some simple graphs to show a visual representation of the amount of healing and damage each team did during that war. Each war scoreboard has a spot where users can uplaod a recording of the war so people who may have missed it can catch up on the action.

							Player Profiles:
![image](https://user-images.githubusercontent.com/22628539/185343449-80504c1f-06a4-4341-931b-051a13834b3c.png)
![image](https://user-images.githubusercontent.com/22628539/185343486-3da36be4-d241-4784-a62d-579b630b6088.png)

  Each player that is recorded in a war will have their own profile, which will display their own stats for all wars (averages, maximums, and totals). These can be sorted by server, role, or both! If a player has filled out what role they play, they are able to view how their stats compare to the average player in that role on that server.

I am sure I am missing some things, and will update this as they pop up in my head, but for now if you have suggestions or ideas, please shoot me a message! I am creating this as I learn, so some of this is going to be a mess, but I am working to get better at programming in general through this project, while creating a useful tool for the community!
