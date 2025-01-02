from typing import Callable, override

import pygame

from client import keybinds
from client.pages.button_play import PlayButton
from client.pages.page import Page
from client.player import ClientPlayer
from client.settings import Settings
from common.data_types import Color, Vec2D

try:
    from PIL import Image, ImageFilter

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

except ModuleNotFoundError:
    def create_blob(radius: int, color: Color, blur_radius: int = 50) -> pygame.Surface:
        circle = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(circle, color.to_tuple(), (radius, radius), radius)

        return circle


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

        for l in self.light_builder:
            light = create_blob(l[0], l[1])
            light.set_alpha(161)
            size = light.get_size()

            center = l[2].to_tuple()
            rect = pygame.Rect(center[0]-size[0]/2, center[1]-size[1]/2, size[0], size[1])
            
            self.lights.append((light, rect))
        
        self.play_button = PlayButton()




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
            blit_pos = scaler(l[1]).topleft

            screen.blit(l[0], blit_pos)
        
        self.play_button.draw(screen, scaler)

    
    @override
    def close(self) -> None:
        pass
