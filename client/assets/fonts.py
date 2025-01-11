import pygame.freetype


pygame.freetype.init()

_font_dir: str = "client/assets/fonts"

dyuthi_b: pygame.freetype.Font = pygame.freetype.Font(file= _font_dir+"/Dyuthi-Regular.ttf")
dyuthi_b.style = pygame.freetype.STYLE_STRONG

d_la_cruz: pygame.freetype.Font = pygame.freetype.Font(file= _font_dir+"/d-la-cruz-font.ttf")
d_la_cruz.wide = False
