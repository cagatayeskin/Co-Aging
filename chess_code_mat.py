import numpy as np
import chess
import chess.engine
import random
import matplotlib.pyplot as plt
import time
from multiprocessing import Pool, cpu_count, Process, Queue

#Material balance calculation
def material_balance(board):
    white = board.occupied_co[chess.WHITE]
    black = board.occupied_co[chess.BLACK]
    return (
        chess.popcount(white & board.pawns) +
        3 * (chess.popcount(white & board.knights))+
        3 * (chess.popcount(white & board.bishops))+
        5 * (chess.popcount(white & board.rooks))+
        9 * (chess.popcount(white & board.queens)),
        chess.popcount(black & board.pawns) +
        3 * (chess.popcount(black & board.knights)) +
        3 * (chess.popcount(black & board.bishops)) +
        5 * (chess.popcount(black & board.rooks)) +
        9 * (chess.popcount(black & board.queens))
    )

def play(_):
    engine1 = chess.engine.SimpleEngine.popen_uci('stockfish')
    engine2 = chess.engine.SimpleEngine.popen_uci('stockfish')
    engine3 = chess.engine.SimpleEngine.popen_uci('stockfish')
    board = chess.Board()
    time = 0
    game_result = 3
    while not board.is_game_over():

        result = engine1.play(board, chess.engine.Limit(time=0.01, depth=10)) #choose the move of whites

        #Check if the move is valid
        if result.move == None:
            game_result = 2 #if not stop the game and exclude it
            break

        #if move is valid, play it 
        board.push(result.move)

        #check if it is checkmate
        if board.is_checkmate() == True:
            game_result = 0 #means first machine won
            break

        result = engine2.play(board, chess.engine.Limit(time=0.01, depth=30)) #choose the move of blacks

        #Check if the move is valid
        if result.move == None:
            game_result = 2 #if not stop the game and exclude it
            break

        #if move is valid, play it 
        board.push(result.move)

        #check if it is checkmate
        if board.is_checkmate() == True:
            game_result = 1 #means second machine won
            break

        #increment the time and look at the material balance
        time += 1
        white_m, black_m = material_balance(board)
        if white_m <= 6 or black_m <= 6 :
            if white_m>black_m:
                game_result = 0 #means first machine won
            elif black_m>white_m:
                game_result = 1 #means second machine won
            break

    engine1.quit()
    engine2.quit()
    engine3.quit()

    return time, game_result

#save the play times in this array
living_times = []

#number of plays
simul_num = 10

#Parallellalized chess play function
pool_size = 4 
if __name__ == '__main__':
    start = time.time()
    with Pool(processes=pool_size) as pool:
        results = pool.map_async(play, range(simul_num))
        results = results.get()

    print(results)
    
    end = time.time()
    print(end - start)
