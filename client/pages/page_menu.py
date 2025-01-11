from typing import Callable, Optional, override

import pygame

from client import keybinds
from client.assets import fonts, textures
from client.pages.button_play import PlayButton
from client.pages.page import Page
from client.player import ClientPlayer
from client.settings import Settings
from common.data_types import Color, Vec2D

try:
    from PIL import Image, ImageFilter, ImageOps

    def create_blob(radius: int, color: Color, blur_radius: int = 50) -> pygame.Surface:
        img_size: tuple[int, int] = (radius*4 + blur_radius*2, radius*4 + blur_radius*2)
        centre: tuple[int, int] = (img_size[0]//2, img_size[0]//2)

        # raw mask
        mask = pygame.Surface(img_size)
        mask.fill((0,0,0))
        pygame.draw.circle(mask, (255,255,255), centre, radius)

        # blur mask
        pillow_mask: Image.Image = Image.frombytes("RGB", img_size, pygame.image.tobytes(mask, "RGB", False))
        blurred_mask = pillow_mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # grascale to alpha
        alpha_mask = blurred_mask.convert('L')

        blob: Image.Image = Image.new("RGBA", img_size, color.to_tuple())
        blob.putalpha(alpha_mask)

        pygame_blob = pygame.image.frombytes(blob.tobytes(), img_size, "RGBA", False)

        return pygame_blob

    def title_drop_shadow(text: pygame.Surface, blur_radius: int = 10) -> pygame.Surface:
        size: Vec2D = Vec2D(*text.get_size())
        size += Vec2D(blur_radius*8, blur_radius*8)

        bg_text = pygame.Surface(size.to_tuple())
        bg_text.fill((255,255,255))
        bg_text.blit(text, (blur_radius*4, blur_radius*4))

        pillow_text: Image.Image = Image.frombytes("RGB", size.to_tuple(), pygame.image.tobytes(bg_text, "RGB", False))

        blurred_mask = pillow_text.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        alpha_mask = ImageOps.invert(blurred_mask.convert('L'))

        shadow: Image.Image = Image.new("RGBA", size.to_tuple(), (0, 0, 0)) # shadow color
        shadow.putalpha(alpha_mask)

        pygame_shadow = pygame.image.frombytes(shadow.tobytes(), size.to_tuple(), "RGBA", False)

        return pygame_shadow

except ModuleNotFoundError:
    def create_blob(radius: int, color: Color, blur_radius: int = 50) -> pygame.Surface:
        circle = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(circle, color.to_tuple(), (radius, radius), radius)

        return circle
    
    def title_drop_shadow(text: pygame.Surface, blur_radius: int = 50) -> pygame.Surface:
        new_rect: pygame.Rect = pygame.Rect(0, 0, *(Vec2D(*text.get_size())+Vec2D(blur_radius//2, blur_radius//2)).to_tuple())

        shadow = pygame.Surface(new_rect.size, pygame.SRCALPHA)
        shadow.fill((0,0,0))
        shadow.set_alpha(25)

        return shadow


class MenuPage(Page):
    
    def __init__(self) -> None:
        self.players: list[ClientPlayer] = [
            ClientPlayer(0, Vec2D(210, 235), Color(72, 155, 126)),
            ClientPlayer(1, Vec2D(830, 330), Color(121, 137, 210)),
            ClientPlayer(2, Vec2D(1420, 725), Color(205, 72, 118)),
        ]

        self.light_builder: list[tuple[int, Color, Vec2D]] = [
            (300, Color(222, 223, 197), Vec2D(400, 450)),
            (200, Color(221, 199, 223), Vec2D(1325, 650)),
        ]
        self.lights: list[tuple[pygame.Surface, pygame.Rect]] = []

        self.current_sf: float = 1
        self.generate_blobs()
        
        self.play_button = PlayButton()

        self.title_drop_shadow: Optional[pygame.Surface] = None

    def generate_blobs(self) -> None:
        self.lights.clear()

        for l in self.light_builder:
            light: pygame.Surface = create_blob(int(l[0]*self.current_sf), l[1])
            light.set_alpha(161)
            size = light.get_size()

            center = l[2]
            rect = pygame.Rect(center.x*self.current_sf-size[0]/2, center.y*self.current_sf-size[1]/2, size[0], size[1])
            
            self.lights.append((light, rect))


    @override
    def check_event(self, event: pygame.event.Event) -> int:
        if event.type == pygame.KEYDOWN:
            match event.key:
                case keybinds.EXIT:
                    return 1
                case _:
                    return 0
        
        return 0


    @override
    def update(self) -> None:
        pass

    @override
    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        screen.fill(Settings.color_menu_bg.to_tuple())

        for p in self.players:
            p.draw(screen, scaler)

        for l in self.lights:
            rect: pygame.Rect = scaler(l[1])
            rect: pygame.Rect = l[1]
            blit_pos = rect.topleft

            # sf: float = rect.w / l[1].w

            image: pygame.Surface = l[0]

            screen.blit(image, blit_pos)
        
        self.play_button.draw(screen, scaler)

        # title
        text_image: pygame.Surface; text_rect: pygame.Rect
        text_image, text_rect = fonts.d_la_cruz.render(text="SQUARES", size=190, fgcolor=Settings.color_menu_title_outline.to_tuple())
        text_rect.center = (816, 171)
        scaled_rect = scaler(text_rect)

        text_image = pygame.transform.smoothscale(text_image, scaled_rect.size)

        # filling
        text_filling = pygame.transform.smoothscale(textures.menu_title_filling, scaled_rect.size)
        text_filling.set_alpha(220)

        # shadow
        shadow: pygame.Surface
        if self.title_drop_shadow is None:
            shadow = title_drop_shadow(text_image)
            self.title_drop_shadow = shadow
        else:
            shadow = self.title_drop_shadow

        shadow_rect = shadow.get_rect()
        shadow_rect.center = scaled_rect.center

        screen.blit(shadow, shadow_rect)

        screen.blit(text_filling, scaled_rect)

        screen.blit(text_image, scaled_rect)

    
    @override
    def close(self) -> None:
        pass

    @override
    def on_resize(self, scale_factor: float) -> None:
        if self.current_sf == scale_factor:
            return
        self.current_sf = scale_factor

        self.title_drop_shadow = None

        self.generate_blobs()

        self.play_button.on_resize()
