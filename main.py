import pygame
import random
from queue import PriorityQueue
from configuracionyvariable import *

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row, self.col = row, col
        self.x, self.y = row * width, col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.is_wall = False
        self.f = self.g = self.h = None

    def get_pos(self): return self.row, self.col

    def update_neighbors(self, grid):
        self.neighbors = []
        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            r, c = self.row + dr, self.col + dc
            if (r, c) in grid and not grid[(r, c)].is_wall:
                self.neighbors.append(grid[(r, c)])

def draw_hud(win, stats):
    pygame.draw.rect(win, HUD_BG, (WIDTH, 0, UI_WIDTH, WIDTH))
    y_offset = 20
    info = [("ESTADÍSTICAS", FONT_HUD, YELLOW),
            (f"Visitados: {stats['visited']}", FONT_HUD_TEXT, TEXT_LIGHT),
            (f"Costo: {stats['cost']}", FONT_HUD_TEXT, TEXT_LIGHT),
            (f"Tiempo: {stats['time']:.2f}ms", FONT_HUD_TEXT, TEXT_LIGHT),
            ("CONTROLES", FONT_HUD, YELLOW),
            ("[R] Aleatorio", FONT_HUD_TEXT, TEXT_LIGHT),
            ("[Espacio] Resolver", FONT_HUD_TEXT, TEXT_LIGHT)]
    
    for text, font, color in info:
        surf = font.render(text, True, color)
        win.blit(surf, (WIDTH + 10, y_offset))
        y_offset += 40

def render_node(node, win):
    # Fondo
    if node.is_wall:
        if IMG_PARED: win.blit(IMG_PARED, (node.x, node.y))
        else: pygame.draw.rect(win, BLACK, (node.x, node.y, node.width, node.width))
    else:
        if IMG_FONDO: win.blit(IMG_FONDO, (node.x, node.y))
        else: pygame.draw.rect(win, WHITE, (node.x, node.y, node.width, node.width))
    
    # Capa de color
    if node.color != WHITE:
        pygame.draw.rect(win, node.color, (node.x, node.y, node.width, node.width))
        pygame.draw.rect(win, GREY, (node.x, node.y, node.width, node.width), 1)

    # Métricas
    if not node.is_wall and node.f is not None:
        f_surf = FONT_MAIN.render(str(int(node.f)), True, BLACK)
        win.blit(f_surf, (node.x + node.width//2 - f_surf.get_width()//2, node.y + 2))
        g_surf = FONT_SUB.render(str(int(node.g)), True, BLACK)
        win.blit(g_surf, (node.x + 2, node.y + node.width - g_surf.get_height() - 2))
        h_surf = FONT_SUB.render(str(int(node.h)), True, BLACK)
        win.blit(h_surf, (node.x + node.width - h_surf.get_width() - 2, node.y + node.width - h_surf.get_height() - 2))

def draw_agent(win, node, prev):
    if AGENT_IMG:
        angle = 0
        if prev:
            dr, dc = node.row - prev.row, node.col - prev.col
            angle = { (1,0): 270, (-1,0): 90, (0,1): 0, (0,-1): 180 }.get((dr, dc), 0)
        img = pygame.transform.rotate(AGENT_IMG, angle)
        win.blit(img, (node.x, node.y))
    else:
        pygame.draw.rect(win, BLUE, (node.x, node.y, node.width, node.width))

def reconstruct_path(came_from, current, draw_func, start, end):
    path = []
    temp = current
    while temp in came_from:
        path.append(temp)
        temp = came_from[temp]
    path.append(temp)
    path.reverse()
    for i, node in enumerate(path):
        if node != start and node != end: node.color = YELLOW
        draw_func()
        draw_agent(WIN, node, path[i-1] if i > 0 else None)
        if SOUND_STEP: SOUND_STEP.play()
        pygame.display.update()
        pygame.time.delay(150)
            
def a_star(draw_func, grid, start, end):
    start_ticks = pygame.time.get_ticks()
    count, open_set = 0, PriorityQueue()
    open_set.put((0, count, start))
    came_from, g_score = {}, {node: float("inf") for node in grid.values()}
    g_score[start] = 0
    open_set_hash = {start}
    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(came_from, end, draw_func, start, end)
            if SOUND_SUCCESS: SOUND_SUCCESS.play()
            return True, count, g_score[end], pygame.time.get_ticks() - start_ticks
        for neighbor in current.neighbors:
            temp_g = g_score[current] + 1
            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                neighbor.f = temp_g + abs(neighbor.row-end.row) + abs(neighbor.col-end.col)
                neighbor.g = temp_g
                neighbor.h = abs(neighbor.row-end.row) + abs(neighbor.col-end.col)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end: neighbor.color = GREEN
        draw_func()
    return False, 0, 0, 0

def main(win, width):
    grid = { (i,j): Node(i, j, width//ROWS, ROWS) for i in range(ROWS) for j in range(ROWS) }
    start, end = grid[(0,0)], grid[(ROWS-1, ROWS-1)]
    stats = {'visited': 0, 'cost': 0, 'time': 0}
    run = True
    while run:
        win.fill(WHITE)
        for node in grid.values(): render_node(node, win)
        draw_hud(win, stats)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    for n in grid.values(): n.is_wall = (random.random() < 0.25); n.color = WHITE; n.f = None
                    grid[(0,0)].is_wall = grid[(ROWS-1, ROWS-1)].is_wall = False
                    for n in grid.values(): n.update_neighbors(grid)
                if event.key == pygame.K_SPACE:
                    for n in grid.values(): n.update_neighbors(grid)
                    _, v, c, t = a_star(lambda: (win.fill(WHITE), [render_node(n, win) for n in grid.values()], draw_hud(win, stats), pygame.display.update()), grid, start, end)
                    stats = {'visited': v, 'cost': c, 'time': t}
    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)