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
