import pygame
import os

pygame.init()
pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 700
UI_WIDTH = 250 
TOTAL_WIDTH = WIDTH + UI_WIDTH
ROWS = 10
GAP = WIDTH // ROWS

WIN = pygame.display.set_mode((TOTAL_WIDTH, WIDTH))
pygame.display.set_caption("Agente Explorador A* - JH y JV")

FONT_MAIN = pygame.font.SysFont("Arial", int(GAP * 0.35), bold=True)
FONT_SUB = pygame.font.SysFont("Arial", int(GAP * 0.22))
FONT_HUD = pygame.font.SysFont("Arial", 20, bold=True)
FONT_HUD_TEXT = pygame.font.SysFont("Arial", 16)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 204, 113)    
RED = (231, 76, 60)        
BLUE = (52, 152, 219)    
PURPLE = (155, 89, 182)  
YELLOW = (241, 196, 15)  
GREY = (127, 140, 141)
HUD_BG = (44, 62, 80)
TEXT_LIGHT = (236, 240, 241)
HIGHLIGHT = (243, 156, 18)

def cargar_recurso(nombre, es_sonido=False):
    ruta = os.path.join(BASE_DIR, nombre)
    if not os.path.exists(ruta):
        return None
    return pygame.mixer.Sound(ruta) if es_sonido else pygame.image.load(ruta)

try:
    IMG_FONDO = pygame.transform.scale(cargar_recurso("suelo.png"), (GAP, GAP))
    IMG_PARED = pygame.transform.scale(cargar_recurso("pared.jfif"), (GAP, GAP))
    AGENT_IMG = pygame.transform.scale(cargar_recurso("robot.png").convert_alpha(), (GAP, GAP))
except:
    IMG_FONDO = IMG_PARED = AGENT_IMG = None

SOUND_STEP = cargar_recurso("pasos.mp3", True)
SOUND_SUCCESS = cargar_recurso("exito.mp3", True)