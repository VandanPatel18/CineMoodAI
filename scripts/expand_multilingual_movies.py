"""Build tmdb_5000_movies.csv with English + multilingual catalog for CineMood AI."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "tmdb_5000_movies.csv"

HEADER = [
    "id", "title", "overview", "genres", "keywords", "poster_path",
    "original_language", "runtime", "release_date", "vote_average", "popularity",
    "cast", "crew",
]

def row(movie_id, title, overview, genre_names, keywords, lang, runtime, date, rating, pop, cast, director):
    genres = "[" + ", ".join(f'{{"id": {i}, "name": "{g}"}}' for i, g in enumerate(genre_names, 1)) + "]"
    kws = "[" + ", ".join(f'{{"id": {i}, "name": "{k}"}}' for i, k in enumerate(keywords, 1)) + "]"
    cast_json = f'[{{"name": "{cast}"}}]'
    crew_json = f'[{{"job": "Director", "name": "{director}"}}]'
    return [
        movie_id, title, overview, genres, kws, f"/m{movie_id}.jpg",
        lang, runtime, date, rating, pop, cast_json, crew_json,
    ]

MOVIES = [
    # English (original samples)
    row(1, "The Sample Comfort", "A warm comforting story about friendship and second chances.", ["Comedy", "Drama"], ["friendship", "warm"], "en", 95, "2015-06-12", 7.2, 12.5, "Actor A", "Director A"),
    row(2, "Relaxing Evening", "Soft melodies and gentle humor make this an easy watch after a long day.", ["Comedy"], ["relaxing", "light"], "en", 88, "2018-11-02", 6.8, 8.3, "Actor B", "Director B"),
    row(3, "Mind Bender", "A cerebral sci-fi that twists perception and reality.", ["Science Fiction", "Thriller"], ["mind-bending", "twist"], "en", 150, "2014-09-07", 8.3, 22.1, "Actor C", "Director C"),
    row(4, "Uplift", "An inspiring tale that uplifts and motivates.", ["Drama"], ["inspiring", "hope"], "en", 110, "2016-03-15", 7.6, 10.2, "Actor D", "Director D"),
    row(5, "Thrill Night", "High-octane thrills and edge-of-seat suspense.", ["Action", "Thriller"], ["suspense", "action"], "en", 105, "2019-07-19", 7.9, 18.4, "Actor E", "Director E"),
    row(6, "The Quiet Shore", "A reflective English drama about healing and new beginnings.", ["Drama"], ["healing", "calm"], "en", 118, "2020-02-14", 7.4, 14.0, "Emma Stone", "Mike Leigh"),
    # Hindi
    row(101, "3 Idiots", "Two friends search for their lost college buddy while recalling reckless youth and chasing real passion.", ["Comedy", "Drama"], ["friendship", "college", "inspiring"], "hi", 170, "2009-12-25", 8.4, 52.0, "Aamir Khan", "Rajkumar Hirani"),
    row(102, "Dangal", "A former wrestler trains his daughters to become world-class fighters against all odds.", ["Drama", "Action"], ["sports", "family", "underdog"], "hi", 161, "2016-12-23", 8.3, 48.5, "Aamir Khan", "Nitesh Tiwari"),
    row(103, "Zindagi Na Milegi Dobara", "Three friends on a bachelor road trip confront fear friendship and what they truly want from life.", ["Drama", "Comedy"], ["travel", "friendship", "life"], "hi", 155, "2011-07-15", 8.1, 35.2, "Hrithik Roshan", "Zoya Akhtar"),
    row(104, "Queen", "A shy woman embarks on a solo honeymoon trip and discovers independence confidence and joy.", ["Comedy", "Drama"], ["empowerment", "travel", "growth"], "hi", 146, "2014-03-07", 8.2, 31.0, "Kangana Ranaut", "Vikas Bahl"),
    row(105, "Andhadhun", "A blind pianist becomes entangled in a twisting mystery full of dark humor and surprises.", ["Thriller", "Comedy"], ["mystery", "twist", "dark"], "hi", 139, "2018-10-05", 8.3, 29.8, "Ayushmann Khurrana", "Sriram Raghavan"),
    row(106, "Dil Chahta Hai", "Three inseparable friends navigate love ambition and the ache of growing apart.", ["Drama", "Comedy"], ["friendship", "youth", "nostalgia"], "hi", 183, "2001-08-10", 8.0, 27.5, "Aamir Khan", "Farhan Akhtar"),
    # Korean
    row(201, "Parasite", "Greed and class tension explode when a poor family infiltrates a wealthy household.", ["Drama", "Thriller"], ["class", "family", "satire"], "ko", 132, "2019-05-30", 8.5, 61.0, "Song Kang-ho", "Bong Joon-ho"),
    row(202, "Train to Busan", "Passengers fight to survive a zombie outbreak on a speeding train.", ["Action", "Horror"], ["zombie", "survival", "intense"], "ko", 118, "2016-07-01", 7.6, 40.2, "Gong Yoo", "Yeon Sang-ho"),
    row(203, "Decision to Leave", "A detective falls for a murder suspect blurring duty desire and obsession.", ["Romance", "Thriller"], ["mystery", "obsession", "noir"], "ko", 138, "2022-06-29", 7.3, 18.5, "Park Hae-il", "Park Chan-wook"),
    row(204, "Past Lives", "Two childhood friends reunite decades later and weigh paths not taken.", ["Drama", "Romance"], ["nostalgia", "fate", "longing"], "ko", 106, "2023-06-02", 8.0, 22.4, "Greta Lee", "Celine Song"),
    # Japanese
    row(301, "Spirited Away", "A girl enters a spirit world and must work in a bathhouse to save her parents.", ["Animation", "Fantasy"], ["magical", "coming-of-age", "wonder"], "ja", 125, "2001-07-20", 8.6, 55.0, "Rumi Hiiragi", "Hayao Miyazaki"),
    row(302, "Your Name", "Two teenagers mysteriously swap bodies and search for each other across time.", ["Animation", "Romance"], ["fate", "romance", "supernatural"], "ja", 106, "2016-08-26", 8.4, 44.0, "Ryunosuke Kamiki", "Makoto Shinkai"),
    row(303, "Drive My Car", "A grieving actor directs a play and bonds with his reserved chauffeur.", ["Drama"], ["grief", "theatre", "healing"], "ja", 179, "2021-08-20", 7.6, 19.2, "Hidetoshi Nishijima", "Ryusuke Hamaguchi"),
    row(304, "Shoplifters", "A poor family survives through small crimes until a secret reshapes their bonds.", ["Drama"], ["family", "poverty", "moral"], "ja", 121, "2018-06-08", 7.9, 16.8, "Lily Franky", "Hirokazu Kore-eda"),
    # Tamil
    row(401, "Ponniyin Selvan: I", "Epic Chola-era intrigue as warriors and royals battle for the throne.", ["Action", "Drama"], ["historical", "epic", "betrayal"], "ta", 167, "2022-09-30", 7.8, 28.5, "Vikram", "Mani Ratnam"),
    row(402, "Super Deluxe", "Strangers collide in a wild day of crime faith and dark comedy.", ["Drama", "Comedy"], ["chaos", "morality", "twist"], "ta", 176, "2019-03-29", 8.3, 12.4, "Vijay Sethupathi", "Thiagarajan Kumararaja"),
    row(403, "96", "Two school sweethearts meet again at a reunion stirring buried love and regret.", ["Romance", "Drama"], ["nostalgia", "love", "reunion"], "ta", 158, "2018-10-04", 8.5, 15.6, "Vijay Sethupathi", "C. Prem Kumar"),
    # Telugu
    row(501, "RRR", "Two legendary revolutionaries unite against colonial rule in a spectacular epic.", ["Action", "Drama"], ["epic", "friendship", "freedom"], "te", 187, "2022-03-25", 7.8, 47.0, "N. T. Rama Rao Jr.", "S. S. Rajamouli"),
    row(502, "Baahubali: The Beginning", "A displaced heir discovers his royal destiny amid war and betrayal.", ["Action", "Fantasy"], ["epic", "kingdom", "revenge"], "te", 159, "2015-07-10", 8.0, 42.3, "Prabhas", "S. S. Rajamouli"),
    row(503, "Jersey", "A failed cricketer fights for one last innings to redeem himself for his son.", ["Drama", "Sport"], ["sports", "redemption", "father"], "te", 157, "2019-04-19", 8.0, 11.2, "Nani", "Gowtam Tinnanuri"),
    # Malayalam
    row(601, "Drishyam", "A father builds an elaborate cover story when his family faces a deadly secret.", ["Thriller", "Drama"], ["family", "mystery", "clever"], "ml", 160, "2013-12-19", 8.4, 24.0, "Mohanlal", "Jeethu Joseph"),
    row(602, "Kumbalangi Nights", "Four troubled brothers slowly open their hearts on a quiet backwater island.", ["Drama"], ["family", "healing", "brothers"], "ml", 135, "2019-02-07", 8.3, 9.8, "Shane Nigam", "Madhu C. Narayanan"),
    # Spanish
    row(701, "Pan's Labyrinth", "A girl escapes into a dark fairy world while Franco-era Spain rages outside.", ["Fantasy", "Drama"], ["fairy tale", "war", "dark"], "es", 118, "2006-10-11", 8.2, 33.5, "Ivana Baquero", "Guillermo del Toro"),
    row(702, "The Secret in Their Eyes", "A retired investigator revisits an unsolved murder and a love he never confessed.", ["Thriller", "Drama"], ["mystery", "romance", "justice"], "es", 129, "2009-08-13", 8.0, 21.0, "Ricardo Darin", "Juan Jose Campanella"),
    row(703, "Roma", "A housekeeper's life unfolds against personal pain and political upheaval in 1970s Mexico.", ["Drama"], ["family", "memory", "loss"], "es", 135, "2018-11-21", 7.7, 18.2, "Yalitza Aparicio", "Alfonso Cuaron"),
    # French
    row(801, "Amelie", "A shy Paris waitress secretly improves strangers' lives while seeking her own joy.", ["Comedy", "Romance"], ["whimsical", "paris", "kindness"], "fr", 122, "2001-04-25", 8.3, 38.0, "Audrey Tautou", "Jean-Pierre Jeunet"),
    row(802, "The Intouchables", "An aristocrat and his ex-con caregiver form an unlikely life-changing friendship.", ["Comedy", "Drama"], ["friendship", "uplifting", "disability"], "fr", 112, "2011-11-02", 8.3, 36.5, "Omar Sy", "Olivier Nakache"),
    # German
    row(901, "Run Lola Run", "Lola races through Berlin to save her boyfriend in a breathless time-loop thriller.", ["Thriller", "Action"], ["time", "urgency", "stylish"], "de", 80, "1998-08-20", 7.6, 14.5, "Franka Potente", "Tom Tykwer"),
    row(902, "Good Bye Lenin!", "A son hides the fall of the Berlin Wall from his fragile socialist mother.", ["Comedy", "Drama"], ["family", "history", "satire"], "de", 121, "2003-02-14", 7.7, 12.8, "Daniel Bruhl", "Wolfgang Becker"),
    # Chinese
    row(1001, "In the Mood for Love", "Two neighbors bond when they suspect their spouses are having an affair.", ["Romance", "Drama"], ["longing", "elegant", "melancholy"], "zh", 98, "2000-09-29", 8.1, 22.0, "Maggie Cheung", "Wong Kar-wai"),
    row(1002, "Crouching Tiger Hidden Dragon", "Warriors pursue a stolen sword while hidden passions threaten ancient codes.", ["Action", "Drama"], ["martial arts", "honor", "romance"], "zh", 120, "2000-12-08", 7.6, 26.4, "Chow Yun-fat", "Ang Lee"),
    # Portuguese
    row(1101, "City of God", "Youth in a Rio favela chase power and survival through crime and ambition.", ["Crime", "Drama"], ["poverty", "violence", "youth"], "pt", 130, "2002-08-30", 8.6, 30.5, "Alexandre Rodrigues", "Fernando Meirelles"),
    # Italian
    row(1201, "Cinema Paradiso", "A filmmaker remembers the Sicilian projectionist who shaped his childhood love of movies.", ["Drama"], ["nostalgia", "cinema", "friendship"], "it", 155, "1988-11-17", 8.5, 20.1, "Philippe Noiret", "Giuseppe Tornatore"),
    # Arabic
    row(1301, "Theeb", "A young Bedouin boy is drawn into danger on a desert railway during World War I.", ["Drama", "Adventure"], ["desert", "coming-of-age", "survival"], "ar", 100, "2014-09-19", 7.3, 6.5, "Jacir Eid Al-Hwietat", "Naji Abu Nowar"),
    # Marathi
    row(1401, "Sairat", "Star-crossed lovers flee caste violence but society closes in with brutal force.", ["Romance", "Drama"], ["love", "caste", "tragedy"], "mr", 174, "2016-04-29", 8.2, 10.5, "Rinku Rajguru", "Nagraj Manjule"),
    # Bengali
    row(1501, "Pather Panchali", "A poor rural family endures hardship as their curious son Apu grows up.", ["Drama"], ["poverty", "childhood", "classic"], "bn", 125, "1955-08-26", 8.3, 8.2, "Subir Banerjee", "Satyajit Ray"),
    # Kannada
    row(1601, "Kantara", "A forest officer clashes with a village ritual defender in a mythic coastal conflict.", ["Action", "Drama"], ["folklore", "ritual", "nature"], "kn", 148, "2022-09-30", 8.2, 19.4, "Rishab Shetty", "Rishab Shetty"),
    # Punjabi
    row(1701, "Chauthi Koot", "Stories of fear and resilience unfold during Punjab's turbulent 1980s.", ["Drama"], ["history", "fear", "rural"], "pa", 115, "2015-05-19", 7.2, 4.5, "Gurvinder Singh", "Gurvinder Singh"),
    # Indonesian
    row(1801, "The Raid", "SWAT officers fight floor by floor through a tower controlled by a ruthless crime lord.", ["Action", "Thriller"], ["martial arts", "siege", "intense"], "id", 101, "2011-11-23", 7.6, 25.0, "Iko Uwais", "Gareth Evans"),
    # Crime & thriller — English
    row(7, "Se7en", "Two detectives hunt a serial killer who uses the seven deadly sins as his blueprint.", ["Crime", "Thriller", "Mystery"], ["dark", "serial killer", "suspense"], "en", 127, "1995-09-22", 8.6, 45.0, "Brad Pitt", "David Fincher"),
    row(8, "The Godfather", "The aging patriarch of a crime dynasty transfers control to his reluctant son.", ["Crime", "Drama"], ["mafia", "family", "power"], "en", 175, "1972-03-24", 9.2, 58.0, "Marlon Brando", "Francis Ford Coppola"),
    row(9, "Shutter Island", "A U.S. Marshal investigates a disappearance at a hospital for the criminally insane.", ["Thriller", "Mystery"], ["twist", "paranoia", "investigation"], "en", 138, "2010-02-19", 8.2, 36.0, "Leonardo DiCaprio", "Martin Scorsese"),
    row(10, "Knives Out", "A master detective unravels a web of lies after a wealthy novelist is found dead.", ["Crime", "Comedy", "Mystery"], ["whodunit", "twist", "family"], "en", 130, "2019-11-27", 7.9, 32.0, "Daniel Craig", "Rian Johnson"),
    row(11, "The Dark Knight", "Batman faces the Joker who plunges Gotham into anarchy and moral chaos.", ["Action", "Crime", "Drama"], ["villain", "chaos", "hero"], "en", 152, "2008-07-18", 9.0, 55.0, "Christian Bale", "Christopher Nolan"),
    row(12, "Get Out", "A young man uncovers disturbing secrets when he meets his girlfriend's family.", ["Horror", "Thriller", "Mystery"], ["social horror", "twist", "suspense"], "en", 104, "2017-02-24", 7.7, 28.0, "Daniel Kaluuya", "Jordan Peele"),
    row(13, "Gone Girl", "Media frenzy erupts when a man becomes the prime suspect in his wife's disappearance.", ["Thriller", "Drama", "Mystery"], ["marriage", "media", "twist"], "en", 149, "2014-10-03", 8.1, 30.0, "Rosamund Pike", "David Fincher"),
    row(14, "Prisoners", "A desperate father takes matters into his own hands when his daughter vanishes.", ["Crime", "Drama", "Thriller"], ["kidnapping", "moral", "dark"], "en", 153, "2013-09-20", 8.1, 24.0, "Hugh Jackman", "Denis Villeneuve"),
    row(15, "The Silence of the Lambs", "An FBI trainee seeks help from a brilliant cannibal killer to catch another murderer.", ["Crime", "Horror", "Thriller"], ["serial killer", "psychological", "intense"], "en", 118, "1991-02-14", 8.6, 40.0, "Jodie Foster", "Jonathan Demme"),
    # Crime & thriller — Hindi
    row(107, "Kahaani", "A pregnant woman searches Kolkata for her missing husband and uncovers a conspiracy.", ["Thriller", "Mystery"], ["investigation", "twist", "suspense"], "hi", 122, "2012-03-09", 8.1, 18.0, "Vidya Balan", "Sujoy Ghosh"),
    row(108, "Gangs of Wasseypur", "Generations of a crime family clash in a brutal saga of revenge and power.", ["Crime", "Action", "Drama"], ["revenge", "gangster", "epic"], "hi", 321, "2012-06-22", 8.2, 22.0, "Manoj Bajpayee", "Anurag Kashyap"),
    row(109, "Tumbbad", "A man hunts a mythical treasure guarded by an ancient evil in a cursed village.", ["Horror", "Fantasy", "Mystery"], ["folklore", "dark", "supernatural"], "hi", 104, "2018-10-12", 8.2, 14.0, "Sohum Shah", "Rahi Anil Barve"),
    row(110, "Badla", "A businesswoman accused of murder rebuilds the case with a cunning lawyer.", ["Crime", "Thriller", "Mystery"], ["murder", "twist", "investigation"], "hi", 118, "2019-03-08", 7.8, 12.0, "Taapsee Pannu", "Sujoy Ghosh"),
    row(111, "Drishyam (Hindi)", "A father scrambles to protect his family when they become entangled in a crime.", ["Crime", "Thriller", "Drama"], ["family", "cover-up", "suspense"], "hi", 163, "2015-07-31", 8.2, 20.0, "Ajay Devgn", "Nishikant Kamat"),
    row(112, "Special 26", "A con artist and his crew pose as CBI officers to pull off daring heists.", ["Crime", "Thriller", "Drama"], ["heist", "con", "twist"], "hi", 144, "2013-02-07", 8.0, 16.0, "Akshay Kumar", "Neeraj Pandey"),
    # Crime & thriller — Korean / Japanese
    row(205, "Memories of Murder", "Detectives hunt a serial killer in 1980s rural Korea with few leads and mounting pressure.", ["Crime", "Drama", "Thriller"], ["serial killer", "investigation", "dark"], "ko", 132, "2003-05-02", 8.1, 20.0, "Song Kang-ho", "Bong Joon-ho"),
    row(206, "Oldboy", "A man freed after 15 years of captivity seeks brutal revenge on his unknown captor.", ["Action", "Drama", "Mystery"], ["revenge", "twist", "violence"], "ko", 120, "2003-11-21", 8.3, 26.0, "Choi Min-sik", "Park Chan-wook"),
    row(305, "Ring", "A journalist investigates a cursed videotape that kills viewers after seven days.", ["Horror", "Mystery"], ["curse", "supernatural", "dread"], "ja", 96, "1998-01-31", 7.2, 15.0, "Nanako Matsushima", "Hideo Nakata"),
    row(306, "Confessions", "A teacher's chilling lecture sets off a chain of revenge after a classroom tragedy.", ["Crime", "Drama", "Thriller"], ["revenge", "moral", "dark"], "ja", 106, "2010-06-05", 7.8, 11.0, "Takako Matsu", "Tetsuya Nakashima"),
    # Crime & thriller — Tamil / Telugu / Malayalam
    row(404, "Vikram Vedha", "A cop hunts a gangster whose stories blur the line between good and evil.", ["Action", "Crime", "Thriller"], ["cat and mouse", "moral", "twist"], "ta", 147, "2017-07-21", 8.3, 14.0, "Madhavan", "Pushkar-Gayathri"),
    row(405, "Ratsasan", "A rookie cop tracks a serial killer targeting schoolgirls in a tense manhunt.", ["Crime", "Thriller", "Horror"], ["serial killer", "investigation", "intense"], "ta", 170, "2018-10-05", 8.4, 13.0, "Vishnu Vishal", "Ram Kumar"),
    row(504, "Evaru", "A police officer unravels conflicting testimonies in a high-profile murder case.", ["Crime", "Thriller", "Mystery"], ["murder", "twist", "investigation"], "te", 100, "2019-08-15", 7.6, 8.5, "Adivi Sesh", "Venkat Ramji"),
    row(603, "Joseph", "A retired police officer's investigation into an organ trafficking ring turns personal.", ["Crime", "Thriller", "Drama"], ["investigation", "medical", "dark"], "ml", 138, "2018-11-16", 8.0, 9.0, "Joju George", "M. Padmakumar"),
    # More genres — Romance / Sci-Fi / War / Family
    row(16, "La La Land", "An aspiring actress and a jazz musician chase dreams and love in modern Los Angeles.", ["Romance", "Drama", "Musical"], ["love", "music", "dreams"], "en", 128, "2016-12-09", 8.0, 34.0, "Emma Stone", "Damien Chazelle"),
    row(17, "Interstellar", "Explorers travel through a wormhole in space to secure humanity's future.", ["Science Fiction", "Drama", "Adventure"], ["space", "time", "family"], "en", 169, "2014-11-07", 8.7, 50.0, "Matthew McConaughey", "Christopher Nolan"),
    row(18, "Saving Private Ryan", "Soldiers cross enemy lines to retrieve a paratrooper after D-Day.", ["War", "Drama", "Action"], ["war", "brotherhood", "sacrifice"], "en", 169, "1998-07-24", 8.6, 38.0, "Tom Hanks", "Steven Spielberg"),
    row(113, "Zindagi Gulzar Hai", "Two people from different worlds connect through letters and quiet longing.", ["Romance", "Drama"], ["love", "class", "poetry"], "hi", 300, "2012-11-30", 8.8, 10.0, "Fawad Khan", "Sultana Siddiqui"),
    row(114, "URI: The Surgical Strike", "Indian forces plan a covert strike against militants in a tense military operation.", ["Action", "War", "Drama"], ["military", "patriotism", "intense"], "hi", 138, "2019-01-11", 8.2, 28.0, "Vicky Kaushal", "Aditya Dhar"),
    row(207, "Along with the Gods", "A firefighter must pass seven trials in the afterlife to earn reincarnation.", ["Fantasy", "Adventure", "Drama"], ["afterlife", "redemption", "epic"], "ko", 139, "2017-12-20", 7.3, 16.0, "Cha Tae-hyun", "Kim Yong-hwa"),
    row(307, "Grave of the Fireflies", "Two siblings struggle to survive in Japan during the final months of World War II.", ["Animation", "Drama", "War"], ["war", "loss", "family"], "ja", 89, "1988-04-16", 8.5, 18.0, "Tsutomu Tatsumi", "Isao Takahata"),
    row(506, "Maharshi", "A ruthless CEO rediscovers purpose when he returns to the village that raised him.", ["Drama", "Action"], ["transformation", "rural", "inspiring"], "te", 176, "2019-05-09", 7.5, 12.0, "Mahesh Babu", "Vamshi Paidipally"),
    row(702, "Elite Squad", "Rio police prepare a brutal raid on a drug lord's stronghold in the favelas.", ["Action", "Crime", "Drama"], ["police", "violence", "corruption"], "pt", 115, "2007-10-05", 8.0, 14.0, "Wagner Moura", "Jose Padilha"),
    row(803, "Tell No One", "A doctor becomes a fugitive when his murdered wife suddenly sends him a message.", ["Crime", "Drama", "Mystery"], ["conspiracy", "chase", "twist"], "fr", 131, "2006-11-01", 7.5, 10.0, "Francois Cluzet", "Guillaume Canet"),
]

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(HEADER)
        writer.writerows(MOVIES)
    print(f"Wrote {len(MOVIES)} movies to {OUT}")

if __name__ == "__main__":
    main()
