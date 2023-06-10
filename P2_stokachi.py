import numpy as np
import random
import pygame
import sys
import math
import time

BLACK = (0,0,0)
GREY = (128, 128, 128)
WHITE = (255,255,255)
BLUE =  (0,0,255)

BOARD_COLORS = {
	'Sepia': pygame.Color('#E3B778'),
	'Latte': pygame.Color('#E7C27D'),
	'Sand': pygame.Color('#D8B863'),
	'Granola': pygame.Color('#D6B85A'),
	'Sandcastle': pygame.Color('#DAC17C'),
	'Sand Dollar': pygame.Color('#EDE8BA'),
	'Hazelnut': pygame.Color('#BDA55D'),
	'Fawn': pygame.Color('#C8A951'),
	'Hazel Wood': pygame.Color('#C9BB8E'),
	'Egg Nog': pygame.Color('#FAE29C'),
	'Oat': pygame.Color('#DFC98A'),
	'Beige': pygame.Color('#EEDC9A'),
	'Macaroon': pygame.Color('#F9E076'),
	'Tan': pygame.Color('#E6DBAC'),
	'Biscotti': pygame.Color('#E3C565'),
	'Parmesean': pygame.Color('#FDE992'),
	'Buttermilk': pygame.Color('#FDEFB2'),
	'Sand': pygame.Color('#D8B863'),
}

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

ROW_COUNT = 6
COLUMN_COUNT = 7

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)

moves = 0
START_TIME = time.process_time()

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	for r in range(ROW_COUNT-1):
		for c in range(COLUMN_COUNT-1):
			if (board[r][c] == piece and board[r][c+1] == piece and board[r+1][c] == piece and board[r+1][c+1] == piece):
				return True 
	return False

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 7
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	''' This function scores each column according to how valuable that move would be. '''
	
	score = 0
	for r in range(ROW_COUNT-1):
		for c in range(COLUMN_COUNT-1):
			window = [board[r][c], board[r][c+1], board[r+1][c], board[r+1][c+1]]
			score += evaluate_window(window, piece)
	return score


def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, 100000000000000)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, AI_PIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):
	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BOARD_COLORS[result], (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, GREY, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, WHITE, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

'''User Input'''
def text_input(title):
	pygame.font.init()
	
	# assigning values to X and Y variable
	display_surface = pygame.display.set_mode((size))
	label_font = pygame.font.SysFont("calibri", 32)
	base_font = pygame.font.SysFont("calibri", 28)
	
	# create a text surface object on which the text is drawn.
	text = label_font.render('Enter the player name', True, WHITE, BLACK)
	
	# create a rectangular object for the text surface object
	textRect = text.get_rect()
	
	# set the center of the rectangular object.
	textRect.topleft = (100, 50)

	user_text = ''
	input_rect = pygame.Rect(100,100,140,32)
	color = pygame.Color('chartreuse4')

	# infinite loop
	while True:
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					user_text = ''
			else:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						return user_text
					# Check for backspace
					elif event.key == pygame.K_BACKSPACE:
						user_text = user_text[:-1]
					else:
						user_text += event.unicode

		display_surface.fill(BLACK)
		pygame.draw.rect(display_surface, color, input_rect)
		text_surface = base_font.render(user_text, True, (255, 255, 255))
      
   	
		display_surface.blit(text_surface, (input_rect.x+5, input_rect.y+5))
		input_rect.w = max(100, text_surface.get_width()+10)
      
		
		display_surface.blit(text, textRect)
		pygame.display.flip()


def options_input(options, title):
	pygame.init()
	display_surface = pygame.display.set_mode((size[0], size[1] + 100))
	title_font = pygame.font.SysFont("calibri", 32)
	option_font = pygame.font.SysFont("calibri", 28)
	text = title_font.render(title, True, WHITE, BLACK)
	text_rect = text.get_rect()
	text_rect.topleft = (50, 50)
	
	option_rects = []
	for i, option in enumerate(options):
        # create a Rect object for the current option
		option_text = option_font.render(option, True, WHITE, BLACK)
		option_rect = option_text.get_rect()
		option_rect.topleft = (50, 100 + i * 40)
		option_rects.append((option_rect, option_text, option))  

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1: 
					mouse_pos = event.pos
					for option_rect, option_text, option in option_rects:
						if option_rect.collidepoint(mouse_pos):
							return option 

		display_surface.fill(BLACK)
		display_surface.blit(text, text_rect)

		GREEN = (0,255,0)
		for option_rect, option_text, option in option_rects:
			pygame.draw.rect(display_surface, GREEN, option_rect, 4)
			
			display_surface.blit(option_text, option_rect)
		
		pygame.display.flip()
'''User Input End'''

def display_game_stats():
	''' This function displays total time elapsed and total moves made during the game.'''

	time_elapsed = str(round(time.process_time() - START_TIME, 2))
	total_moves = str(moves)
	print("Time elapse", time_elapsed)
	print("Total moves", total_moves)

	pygame.init()
	stats_display = pygame.display.set_mode(size)

	time_font = pygame.font.SysFont("calibri", 32)
	moves_font = pygame.font.SysFont("calibri", 32)

	time_text = time_font.render("Total time elapsed: " + time_elapsed + " seconds", True, WHITE, BLACK)
	moves_text = moves_font.render("Total moves: " + total_moves, True, WHITE, BLACK)
	
	time_rect = time_text.get_rect()
	moves_rect = moves_text.get_rect()

	time_rect.topleft = (50, 50)
	moves_rect.topleft = (50, 100)

	while True:
		stats_display.fill(BLACK)
		pygame.draw.rect(stats_display, WHITE, time_rect)
		pygame.draw.rect(stats_display, WHITE, moves_rect)
		
		stats_display.blit(time_text, time_rect)
		stats_display.blit(moves_text, moves_rect)
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			else:
				pygame.time.wait(6000)
				return 
			
pygame.init()

#Take input from the user
username = text_input('Enter player name')

turn = options_input([username, 'AI'], 'Who plays first?')
if turn == 'AI':
	turn = AI
else:
	turn = PLAYER

depth = int(options_input(['1', '2', '3', '4', '5'], 'Select the depth of MINIMAX search tree'))

result = options_input(BOARD_COLORS.keys(), "Select board color")


#Start game
board = create_board()
print_board(board)
game_over = False

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

#turn = random.randint(PLAYER, AI)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, GREY, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, BLACK, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, GREY, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)
					moves += 1

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render(str(username.capitalize()) + " wins!!", 1, WHITE)
						screen.blit(label, (40,10))
						game_over = True						

					turn += 1
					turn = turn % 2

					print_board(board)
					draw_board(board)

	if (len(get_valid_locations(board)) == 0):
		#print("inside the if before AI turn")
		r = myfont.render("Match Tie...", 1, WHITE)
		screen.blit(r, (40,10))
		print_board(board)
		draw_board(board)
		game_over = True

	# # Ask for Player 2 Input
	if turn == AI and not game_over:				

		#col = random.randint(0, COLUMN_COUNT-1)
		#col = pick_best_move(board, AI_PIECE)
		col, minimax_score = minimax(board, depth, -math.inf, math.inf, True)
		print(col, minimax_score)

		if is_valid_location(board, col):
			#pygame.time.wait(500)
			#print("Inside valid locations AI")
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)
			moves += 1

			if winning_move(board, AI_PIECE):
				label = myfont.render("AI wins!!", 1, BLACK)
				screen.blit(label, (40,10))
				game_over = True
				
			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(3000)
		display_game_stats()
		#quit()