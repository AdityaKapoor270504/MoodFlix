"""Regenerates data/movies.csv (sample dataset of 50 well-known films).
To use a bigger dataset, keep the same columns: title,year,genres,runtime,rating,pacing,moods,overview"""
import csv
from pathlib import Path

rows = [
("The Intouchables",2011,"Comedy|Drama",112,8.5,"medium","heartwarming|uplifting|funny","A wealthy man and his unlikely caregiver form a joyful friendship."),
("Paddington 2",2017,"Comedy|Family|Adventure",104,7.8,"medium","comforting|heartwarming|funny","A kind bear is framed for theft and wins everyone over."),
("Inside Out",2015,"Animation|Comedy|Family",95,8.1,"medium","cathartic|heartwarming|funny","A girl's emotions struggle to guide her through a big move."),
("3 Idiots",2009,"Comedy|Drama",170,8.4,"medium","funny|inspiring|uplifting","Engineering students challenge the pressure to just chase grades."),
("Zindagi Na Milegi Dobara",2011,"Comedy|Drama",155,8.2,"medium","uplifting|adventurous|funny","Three friends take a road trip that changes how they see life."),
("Queen",2013,"Comedy|Drama",146,8.2,"medium","inspiring|uplifting|funny","A jilted bride goes on her honeymoon alone and finds herself."),
("Piku",2015,"Comedy|Drama",123,7.6,"slow","comforting|funny|heartwarming","A daughter and her quirky father go on a road trip to Kolkata."),
("Dil Chahta Hai",2001,"Comedy|Drama|Romance",183,8.1,"medium","funny|romantic|comforting","Three close friends navigate love and growing up."),
("The Secret Life of Walter Mitty",2013,"Adventure|Comedy|Drama",114,7.3,"medium","adventurous|inspiring|escapist","A daydreamer finally sets out on a real adventure."),
("Soul",2020,"Animation|Comedy|Fantasy",100,8.0,"medium","thoughtful|heartwarming|uplifting","A musician explores what makes life worth living."),
("Little Miss Sunshine",2006,"Comedy|Drama",101,7.8,"medium","funny|heartwarming|cathartic","A dysfunctional family drives across the country for a pageant."),
("Good Will Hunting",1997,"Drama",126,8.3,"medium","cathartic|inspiring|thoughtful","A gifted janitor learns to open up with help from a therapist."),
("Eternal Sunshine of the Spotless Mind",2004,"Drama|Romance|Sci-Fi",108,8.3,"medium","melancholic|mind-bending|romantic","A couple erases each other from memory, then reconsiders."),
("Lost in Translation",2003,"Drama|Romance",102,7.7,"slow","melancholic|thoughtful|comforting","Two lonely strangers connect in Tokyo."),
("Her",2013,"Drama|Romance|Sci-Fi",126,8.0,"slow","melancholic|thoughtful|romantic","A lonely writer falls for an AI operating system."),
("Manchester by the Sea",2016,"Drama",137,7.8,"slow","melancholic|cathartic|dark","A man returns home to care for his nephew after a loss."),
("Wonder",2017,"Drama|Family",113,7.9,"medium","heartwarming|inspiring|cathartic","A boy with facial differences starts school for the first time."),
("Taare Zameen Par",2007,"Drama|Family",165,8.3,"medium","cathartic|heartwarming|inspiring","A teacher discovers why a struggling child can't keep up."),
("Udaan",2010,"Drama",134,7.9,"slow","inspiring|cathartic|melancholic","A teenager escapes a strict father to chase his dream of writing."),
("Wake Up Sid",2009,"Drama|Romance",138,7.6,"slow","comforting|romantic|thoughtful","A directionless young man grows up after meeting a new friend."),
("Jab We Met",2007,"Comedy|Drama|Romance",138,7.9,"medium","romantic|funny|uplifting","A heartbroken businessman meets a talkative, free-spirited traveler."),
("Spirited Away",2001,"Animation|Adventure|Fantasy",125,8.6,"medium","escapist|adventurous|comforting","A girl must work in a spirit bathhouse to rescue her parents."),
("Your Name",2016,"Animation|Drama|Romance|Fantasy",106,8.4,"medium","romantic|melancholic|escapist","Two teenagers mysteriously swap bodies and search for each other."),
("Interstellar",2014,"Adventure|Drama|Sci-Fi",169,8.7,"slow","thoughtful|mind-bending|cathartic","Astronauts travel through a wormhole to save humanity."),
("Inception",2010,"Action|Sci-Fi|Thriller",148,8.8,"fast","mind-bending|thrilling|tense","A thief enters dreams to plant an idea in someone's mind."),
("The Prestige",2006,"Drama|Mystery|Sci-Fi",130,8.5,"medium","mind-bending|dark|tense","Two rival magicians destroy each other chasing the perfect trick."),
("Knives Out",2019,"Comedy|Crime|Mystery",130,7.9,"medium","funny|thrilling|escapist","A detective investigates the death of a wealthy novelist."),
("Parasite",2019,"Drama|Thriller|Comedy",132,8.5,"medium","dark|tense|thoughtful","A poor family schemes its way into a rich household."),
("Drishyam",2015,"Crime|Drama|Thriller",163,8.2,"medium","tense|thrilling|thoughtful","A father goes to great lengths to protect his family."),
("Andhadhun",2018,"Crime|Comedy|Thriller",139,8.2,"fast","thrilling|funny|dark","A pianist pretending to be blind witnesses a crime."),
("Mad Max: Fury Road",2015,"Action|Adventure|Sci-Fi",120,8.1,"fast","energetic|thrilling|adventurous","A relentless chase across a desert wasteland."),
("John Wick",2014,"Action|Crime|Thriller",101,7.4,"fast","energetic|thrilling|dark","A retired hitman hunts those who wronged him."),
("Top Gun: Maverick",2022,"Action|Drama",130,8.2,"fast","energetic|thrilling|inspiring","A veteran pilot trains a new generation for a dangerous mission."),
("Rocky",1976,"Drama|Sport",119,8.1,"medium","inspiring|cathartic|energetic","A small-time boxer gets a shot at the heavyweight title."),
("Chak De! India",2007,"Drama|Sport",153,8.1,"medium","inspiring|energetic|cathartic","A disgraced coach turns a women's hockey team into winners."),
("Dangal",2016,"Action|Biography|Drama|Sport",161,8.3,"medium","inspiring|energetic|cathartic","A father trains his daughters to become wrestling champions."),
("The Pursuit of Happyness",2006,"Biography|Drama",117,8.0,"medium","inspiring|cathartic|melancholic","A struggling father fights to build a better life for his son."),
("Forrest Gump",1994,"Drama|Romance",142,8.8,"medium","heartwarming|thoughtful|comforting","A kind man drifts through decades of American history."),
("The Grand Budapest Hotel",2014,"Adventure|Comedy|Crime",99,8.1,"fast","funny|escapist|comforting","A hotel concierge is pulled into a caper over a stolen painting."),
("Superbad",2007,"Comedy",113,7.6,"fast","funny|energetic|escapist","Two teens try to score alcohol for a party before graduation."),
("The Hangover",2009,"Comedy",100,7.7,"fast","funny|energetic|escapist","Three friends piece together a wild night in Las Vegas."),
("Hera Pheri",2000,"Comedy",156,8.2,"medium","funny|comforting|escapist","Three broke men stumble into a chaotic kidnapping mix-up."),
("Spider-Man: Into the Spider-Verse",2018,"Animation|Action|Adventure",117,8.4,"fast","energetic|uplifting|adventurous","A teen becomes Spider-Man and meets heroes from other worlds."),
("Coco",2017,"Animation|Family|Fantasy",105,8.4,"medium","heartwarming|cathartic|uplifting","A boy who loves music enters the Land of the Dead."),
("Amelie",2001,"Comedy|Romance",122,8.3,"medium","comforting|romantic|escapist","A shy Parisian quietly improves the lives of those around her."),
("The Truman Show",1998,"Comedy|Drama|Sci-Fi",103,8.2,"medium","thoughtful|mind-bending|funny","A man slowly learns his whole life is a TV show."),
("Get Out",2017,"Horror|Mystery|Thriller",104,7.8,"medium","tense|dark|thrilling","A visit to his girlfriend's family turns sinister."),
("A Quiet Place",2018,"Drama|Horror|Sci-Fi",90,7.5,"medium","tense|thrilling|dark","A family survives in silence among sound-hunting creatures."),
("Gully Boy",2019,"Drama|Music",153,7.9,"medium","inspiring|energetic|uplifting","A Mumbai slum kid rises through the underground rap scene."),
("Life of Pi",2012,"Adventure|Drama|Fantasy",127,7.9,"slow","adventurous|thoughtful|escapist","A boy survives at sea sharing a lifeboat with a tiger."),
]
out = Path(__file__).parent / "movies.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["title","year","genres","runtime","rating","pacing","moods","overview"])
    w.writerows(rows)
print(f"Wrote {len(rows)} movies to {out}")
