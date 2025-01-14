from typing import Callable, override

import pygame

from client import keybinds
from client.pages import page_ids
from client.pages.button_play import Button
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
    
    def __init__(self, page_changer: Callable[[int], None], mouse_getter: Callable[[], Vec2D]) -> None:
        self.page_changer: Callable[[int], None] = page_changer
        self.mouse_getter: Callable[[], Vec2D] = mouse_getter

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
        
        self.play_button = Button("Play", Vec2D(556, 459), Vec2D(488, 154))

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
            if event.key == keybinds.EXIT:
                return 1
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                
                if self.play_button.rect.collidepoint(self.mouse_getter().to_tuple()):
                    self.page_changer(page_ids.PAGE_GAME)

                return 0
        
        return 0


    @override
    def update(self) -> None:
        if self.play_button.rect.collidepoint(self.mouse_getter().to_tuple()):
            self.play_button.alternate_color = True
        else:
            self.play_button.alternate_color = False

    @override
    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        screen.fill(Settings.color_menu_bg.to_tuple())

        for p in self.players:
            p.draw(screen, scaler)

        for l in self.lights:
            # rect: pygame.Rect = scaler(l[1])
            rect: pygame.Rect = l[1]
            blit_pos = rect.topleft

            # sf: float = rect.w / l[1].w

            image: pygame.Surface = l[0]

            screen.blit(image, blit_pos)
        
        self.play_button.draw(screen, scaler)

    
    @override
    def close(self) -> None:
        pass

    @override
    def on_resize(self, scale_factor: float) -> None:
        if self.current_sf == scale_factor:
            return
        self.current_sf = scale_factor

        self.generate_blobs()
