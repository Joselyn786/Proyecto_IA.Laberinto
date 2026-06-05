import pygame
import random
from queue import PriorityQueue

# Configuración
WIDTH = 700
ROWS = 10 
GAP = WIDTH // ROWS
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Agente Explorador A*")

# Inicializar fuentes de Pygame
pygame.font.init()
# Ajustamos el tamaño de la fuente dinámicamente según el tamaño de la celda
FONT_MAIN = pygame.font.SysFont("Arial", int(GAP * 0.35), bold=True)
FONT_SUB = pygame.font.SysFont("Arial", int(GAP * 0.22))

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 204, 113)    # Un verde más sutil
RED = (231, 76, 60)       # Un rojo más sutil
BLUE = (52, 152, 219)     # Azul para el camino
PURPLE = (155, 89, 182)   # Morado para inicio/fin
YELLOW = (241, 196, 15)   # Amarillo para nodos evaluados con éxito
GREY = (127, 140, 141)

# Carga de imágenes
try:
    IMG_FONDO = pygame.transform.scale(pygame.image.load("suelo.png"), (GAP, GAP))
    IMG_PARED = pygame.transform.scale(pygame.image.load("pared.jfif"), (GAP, GAP))
    AGENT_IMG = pygame.image.load("robot.png").convert_alpha()
    AGENT_IMG = pygame.transform.scale(AGENT_IMG, (GAP, GAP))
except:
    IMG_FONDO = None
    IMG_PARED = None
    AGENT_IMG = None

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.is_wall = False
        
        # Nuevos atributos para almacenar las métricas de A*
        self.f = None
        self.g = None
        self.h = None

    def get_pos(self):
        return self.row, self.col

    def draw(self, win):
        # 1. Dibujar el fondo base (Pared o Suelo)
        if self.is_wall:
            if IMG_PARED: win.blit(IMG_PARED, (self.x, self.y))
            else: pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.width))
        else:
            if IMG_FONDO: win.blit(IMG_FONDO, (self.x, self.y))
            else: pygame.draw.rect(win, WHITE, (self.x, self.y, self.width, self.width))
        
        # 2. Si el nodo cambió de estado (tiene color), rellenamos con una capa translúcida o sólida
        if self.color != WHITE:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
            # Dibujar un borde tenue para mantener la cuadrícula visible
            pygame.draw.rect(win, GREY, (self.x, self.y, self.width, self.width), 1)

        # 3. Dibujar las métricas numéricas (f, g, h) si han sido calculadas
        if not self.is_wall and self.f is not None:
            # Color del texto (negro para contrastar bien)
            text_color = BLACK
            
            # F (Centro o arriba al centro, número grande)
            f_surface = FONT_MAIN.render(str(int(self.f)), True, text_color)
            f_rect = f_surface.get_rect(center=(self.x + self.width // 2, self.y + self.width // 3 + 2))
            win.blit(f_surface, f_rect)
            
            # G (Esquina inferior izquierda)
            g_surface = FONT_SUB.render(str(int(self.g)), True, text_color)
            win.blit(g_surface, (self.x + 4, self.y + self.width - g_surface.get_height() - 2))
            
            # H (Esquina inferior derecha)
            h_surface = FONT_SUB.render(str(int(self.h)), True, text_color)
            win.blit(h_surface, (self.x + self.width - h_surface.get_width() - 4, self.y + self.width - h_surface.get_height() - 2))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall:
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall:
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall: 
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall: 
            self.neighbors.append(grid[self.row][self.col - 1])

def randomize_walls(grid, rows):
    for row in grid:
        for node in row:
            node.is_wall = False
            node.color = WHITE
            node.f = None
            node.g = None
            node.h = None
            if random.random() < 0.25: # Ajustado a 25% para que se parezca más a tus imágenes
                node.is_wall = True
    grid[0][0].is_wall = False
    grid[rows-1][rows-1].is_wall = False
    
    grid[0][0].color = PURPLE
    grid[rows-1][rows-1].color = PURPLE

def draw_agent(win, current, previous):
    if AGENT_IMG:
        angle = 0
        if previous:
            dr = current.row - previous.row
            dc = current.col - previous.col
            if dr == 1: angle = 270
            elif dr == -1: angle = 90
            elif dc == 1: angle = 0
            else: angle = 180
        img = pygame.transform.rotate(AGENT_IMG, angle)
        win.blit(img, (current.x, current.y))
    else:
        pygame.draw.rect(win, BLUE, (current.x, current.y, current.width, current.width))

def h(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def reconstruct_path(came_from, current, draw_func, start, end):
    path = []
    temp = current
    while temp in came_from:
        path.append(temp)
        temp = came_from[temp]
    path.append(temp)
    path.reverse()
    
    # Marcar camino permanente
    for node in path:
        if node != start and node != end:
            node.color = YELLOW  # Conserva el color amarillo de la ruta óptima
    
    # Animar movimiento del agente
    for i in range(len(path)):
        draw_func()
        prev = path[i-1] if i > 0 else None
        draw_agent(WIN, path[i], prev)
       
        pygame.draw.rect(WIN, PURPLE, (start.x, start.y, start.width, start.width), 3)
        pygame.draw.rect(WIN, PURPLE, (end.x, end.y, end.width, end.width), 3)
        
        pygame.display.update()
        pygame.time.delay(100)

def a_star(draw_func, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    
    # Asignar valores iniciales al nodo de salida
    start.g = 0
    start.h = h(start.get_pos(), end.get_pos())
    start.f = start.g + start.h

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw_func, start, end)
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                
                # Calculamos y guardamos H y F en el objeto Nodo para que draw() los pinte
                neighbor.g = temp_g_score
                neighbor.h = h(neighbor.get_pos(), end.get_pos())
                neighbor.f = neighbor.g + neighbor.h
                
                f_score[neighbor] = neighbor.f
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:
                        neighbor.color = GREEN  # Nodos en Open Set (Verde)
                        
        draw_func()
        if current != start: 
            current.color = RED  # Nodos ya evaluados/Closed Set (Rojo)
            
    return False

def make_grid(rows, width):
    return [[Node(i, j, width // rows, rows) for j in range(rows)] for i in range(rows)]

def draw(win, grid):
    win.fill(WHITE)
    for row in grid:
        for node in row: 
            node.draw(win)
            
    start = grid[0][0]
    end = grid[len(grid)-1][len(grid)-1]
    pygame.draw.rect(win, PURPLE, (start.x, start.y, start.width, start.width), 3)
    pygame.draw.rect(win, PURPLE, (end.x, end.y, end.width, end.width), 3)
    
    pygame.display.update()
    
def main(win, width):
    grid = make_grid(ROWS, width)
    start = grid[0][0]
    end = grid[ROWS-1][ROWS-1]
    
    start.color = PURPLE
    end.color = PURPLE
    
    run = True
    while run:
        draw(win, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    randomize_walls(grid, ROWS)
                    for row in grid:
                        for node in row: node.update_neighbors(grid)
                
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row: node.update_neighbors(grid)
                    a_star(lambda: draw(win, grid), grid, start, end)
                    
    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)