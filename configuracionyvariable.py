import pygame

pygame.init()

WIDTH = 700
ROWS = 10
GAP = WIDTH // ROWS

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Agente Explorador A* - JH y JV")

FONT_MAIN = pygame.font.SysFont("Arial", int(GAP * 0.35), bold=True)
FONT_SUB = pygame.font.SysFont("Arial", int(GAP * 0.22))

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (46, 204, 113)    
RED    = (231, 76, 60)       
BLUE   = (52, 152, 219)     
PURPLE = (155, 89, 182)   
YELLOW = (241, 196, 15)   
GREY   = (127, 140, 141)

try:
    IMG_FONDO = pygame.transform.scale(pygame.image.load("suelo.png"), (GAP, GAP))
    IMG_PARED = pygame.transform.scale(pygame.image.load("pared.jfif"), (GAP, GAP))
    AGENT_IMG = pygame.image.load("robot.png").convert_alpha()
    AGENT_IMG = pygame.transform.scale(AGENT_IMG, (GAP, GAP))
except Exception as e:
    print(f"Pequeno mensaje de advertencia: No se pudieron cargar las imágenes ({e})")
    IMG_FONDO = None
    IMG_PARED = None
    AGENT_IMG = None