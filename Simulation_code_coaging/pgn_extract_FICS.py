import numpy as np
import time
import re
import chess

def w_expected_outcome(wELO, bELO, wRD, bRD):
    q = np.log(10)/400
    return 1/(1+np.power(10, ((bELO-wELO)/(400*np.sqrt(1+3* q**2 * (wRD**2 + bRD**2)/np.pi**2)))))

def pgn(pgn_file):
    ext = 1000
    living_times_w = []
    living_times_b = []
    white_elo_pattern = re.compile(r'WhiteElo\s+"(\d+)"')
    black_elo_pattern = re.compile(r'BlackElo\s+"(\d+)"')
    white_RD_pattern = re.compile(r'WhiteRD\s+"(\d+.\d)"')
    black_RD_pattern = re.compile(r'BlackRD\s+"(\d+.\d)"')
    white_clock_pattern = re.compile(r'WhiteClock\s+"(\d+:\d+:\d+\.\d+)"')
    black_clock_pattern = re.compile(r'BlackClock\s+"(\d+:\d+:\d+\.\d+)"')
    plycount_pattern = re.compile(r'PlyCount\s+"(\d+)"')
    result_pattern = re.compile(r'Result\s+"((?:1-0|0-1|1/2-1/2))"', re.IGNORECASE)  # Updated pattern

    with open(pgn_file, 'r') as file:
        for line in file:
            if 'WhiteElo' in line:
                white_elo = int(white_elo_pattern.search(line).group(1))
                black_elo = int(black_elo_pattern.search(next(file)).group(1))
                whiteRD = white_RD_pattern.search(next(file))
                blackRD = black_RD_pattern.search(next(file))
                for _ in range(3):  # Skip irrelevant lines
                    next(file)
                if whiteRD and blackRD:
                    whiteRD = float(whiteRD.group(1))
                    blackRD = float(blackRD.group(1))
                    white_outcome = w_expected_outcome(white_elo, black_elo, whiteRD, blackRD)
                    white_clock = white_clock_pattern.search(next(file))
                    black_clock = black_clock_pattern.search(next(file))
                    if 0.8 >= white_outcome >= 0.7:
                        if white_clock and black_clock:
                            white_clock = white_clock.group(1)
                            black_clock = black_clock.group(1)
                            if white_clock == black_clock == '0:05:00.000':
                                next(file) #pass a line
                                plycount_match = plycount_pattern.search(next(file))
                                if plycount_match is not None:  # Check if match was found
                                    plycount = int(plycount_match.group(1))  # Extract ply count if match found
                                    if plycount > 10:  # Example condition, adjust as needed
                                        result_match = result_pattern.search(next(file))
                                        if result_match is not None:  # Check if match was found
                                            result = result_match.group(1)
                                            next(file) #skip the empty line
                                            gameplay = file.readline() #read the line of algebraic notation
                                            if "forfeit" not in gameplay and "disconnect" not in gameplay:  # Exclude forfeits due to disconnection
                                                if result == '1-0':
                                                    #print(whiteRD, blackRD)
                                                    if plycount%2 == 0: #normally whites only win in odd numbers but if they win at even, subtract one to keep plycount consistent
                                                        plycount -= 1
                                                    living_times_w.append(plycount + ext)
                                                    living_times_b.append((plycount + 1) // 2)
                                                elif result == '0-1':
                                                    #print(whiteRD, blackRD)
                                                    if plycount%2 == 1: #normally blacks only win in even numbers but if they win at even, subtract one to keep plycount consistent
                                                        plycount += 1
                                                    living_times_w.append(plycount // 2)
                                                    living_times_b.append(plycount + ext)
                                                elif result == '1/2-1/2':  # Handle draw result
                                                    # If draw do not take into consideration
                                                    pass

    return living_times_w, living_times_b

databases = [
'chess_database/database_blitz_2019.pgn',
'chess_database/database_blitz_2018.pgn',
'chess_database/database_blitz_2017.pgn',
'chess_database/database_blitz_2016.pgn',
'chess_database/database_blitz_2015.pgn']


start = time.time()
for database in databases:
    living_times = pgn(database)
    living_times_w = living_times[0]
    living_times_b = living_times[1]
    filew = open('extracted_data/plytimesw_blitz_80-70s_5min.txt', 'w')              
    filew.write(str(living_times_w))
    fileb = open('extracted_data/plytimesb_blitz_80-70s_5min.txt', 'w')   
    fileb.write(str(living_times_b))
filew.close()
fileb.close()
end = time.time()
print("Execution time:", end - start)

# def pgn(pgn_file):
#     start = time.time()
#     file = open(pgn_file, 'r')
#     contents = file.readlines()
#     living_times = [] 
#     living_times_w = []
#     living_times_b = []
#     ext = 1000
#     for i in range(len(contents)):
#         if (str(contents[i])[1:9]) == 'WhiteElo':
#             white_elo = re.findall(r'\d+', str(contents[i]))
#             black_elo = re.findall(r'\d+', str(contents[i+1]))
#             if 300>(int(white_elo[0])-int(black_elo[0]))>100:
#                     plytime = (re.findall(r'\d+', str(contents[i+11])))
#                     plytime = int(plytime[0])
#                     clock = int((re.findall(r'\d+', str(contents[i+8])))[1])
#                     print(clock)
#                     if plytime > 10:
#                         if (str(contents[i+12])[9:12]) == '1-0':
#                             if (plytime%2) == 0:
#                                 plytime -= 1
#                             living_times_w.append(plytime+ext)
#                             living_times_b.append(int((plytime-1)/2))
#                         elif (str(contents[i+12])[9:12]) == '0-1':
#                             if (plytime%2) != 0:
#                                 plytime += 1
#                             living_times_w.append(int(plytime/2))
#                             living_times_b.append(plytime+ext)
#     end = time.time()
#     print(end - start)
#     file.close()
#     return living_times_w, living_times_b
