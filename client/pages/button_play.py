from typing import Callable

import pygame

from client.assets import fonts
from client.settings import Settings
from common.data_types import Color, Vec2D

try:
    from PIL import Image, ImageFilter

    def drop_shadow(size: Vec2D, blur_radius: int = 50) -> pygame.Surface:
        img_size: tuple[int, int] = (size.x*4 + blur_radius*2, size.y*4 + blur_radius*2)

        # raw mask
        mask = pygame.Surface(img_size)
        mask.fill((0,0,0))
        pygame.draw.rect(mask, (255,255,255), pygame.Rect((img_size[0]-size.x)/2, (img_size[1]-size.y)/2, size.x, size.y)) #rect in center of img_size

        # blur mask
        pillow_mask: Image.Image = Image.frombytes("RGB", img_size, pygame.image.tobytes(mask, "RGB", False))
        blurred_mask = pillow_mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # grascale to alpha
        alpha_mask = blurred_mask.convert('L')

        shadow: Image.Image = Image.new("RGBA", img_size, (0, 0, 0)) # shadow color
        shadow.putalpha(alpha_mask)

        pygame_shadow = pygame.image.frombytes(shadow.tobytes(), img_size, "RGBA", False)

        return pygame_shadow

except ModuleNotFoundError:
    def drop_shadow(size: Vec2D, blur_radius: int = 50) -> pygame.Surface:
        new_rect: pygame.Rect = pygame.Rect(0, 0, size.x+4, size.y+4)

        shadow = pygame.Surface(new_rect.size, pygame.SRCALPHA)
        shadow.fill((0,0,0))
        shadow.set_alpha(25)

        return shadow


class PlayButton:

    def __init__(self) -> None:
        self.pos: Vec2D = Vec2D(556, 459)
        self.rect: pygame.Rect = pygame.Rect(self.pos.x, self.pos.y, 488, 154)

        self.alternate_color: bool = False

    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:

        # drop shadow
        shadow: pygame.Surface = drop_shadow(Vec2D(*scaler(self.rect).size))
        shadow_rect = shadow.get_rect()
        shadow_rect.center = scaler(self.rect).center

        screen.blit(shadow, shadow_rect)

        # border
        outline_color = Settings.color_menu_button_border_alt if self.alternate_color else Settings.color_menu_button_border

        translucent_outline: pygame.Surface = self._draw_bevelled_rect(scaler, self.rect, 28, outline_color)
        translucent_outline.set_alpha(65)
        screen.blit(translucent_outline, scaler(self.rect))

        outline_rect: pygame.Rect = pygame.Rect(self.rect.x+1, self.rect.y+1, self.rect.w-2, self.rect.h-2)
        screen.blit(self._draw_bevelled_rect(scaler, outline_rect, 28, outline_color), scaler(outline_rect).topleft)
        
        # outline
        outline_rect: pygame.Rect = pygame.Rect(self.rect.x+10, self.rect.y+10, self.rect.w-20, self.rect.h-20)
        outline: pygame.Surface = pygame.Surface(scaler(outline_rect).size, pygame.SRCALPHA)

        outline_curve_tl: pygame.Rect = scaler(pygame.Rect(20, 20, 20, 20))
        outline_curve_tr: pygame.Rect = scaler(pygame.Rect(outline_rect.w-20, 20, 20, 20))
        outline_curve_bl: pygame.Rect = scaler(pygame.Rect(20, outline_rect.h-20, 20, 20))
        outline_curve_br: pygame.Rect = scaler(pygame.Rect(outline_rect.w-20, outline_rect.h-20, 20, 20))

        pygame.draw.circle(outline, Settings.color_menu_button_outline_light.to_tuple(), outline_curve_tl.topleft, outline_curve_tl.w)
        pygame.draw.circle(outline, Settings.color_menu_button_outline_medium.to_tuple(), outline_curve_tr.topleft, outline_curve_tr.w)
        pygame.draw.circle(outline, Settings.color_menu_button_outline_medium.to_tuple(), outline_curve_bl.topleft, outline_curve_bl.w)
        pygame.draw.circle(outline, Settings.color_menu_button_outline_dark.to_tuple(), outline_curve_br.topleft, outline_curve_br.w)

        outline_rect_top: pygame.Rect = scaler(pygame.Rect(20, 0, outline_rect.w-40, 15))
        outline_rect_bottom: pygame.Rect = scaler(pygame.Rect(20, outline_rect.h-15, outline_rect.w-40, 15))
        outline_rect_left: pygame.Rect = scaler(pygame.Rect(0, 20, 15, outline_rect.h-40))
        outline_rect_right: pygame.Rect = scaler(pygame.Rect(outline_rect.w-15, 20, 15, outline_rect.h-40))

        pygame.draw.rect(outline, Settings.color_menu_button_outline_light.to_tuple(), outline_rect_top)
        pygame.draw.rect(outline, Settings.color_menu_button_outline_dark.to_tuple(), outline_rect_bottom)
        pygame.draw.rect(outline, Settings.color_menu_button_outline_light.to_tuple(), outline_rect_left)
        pygame.draw.rect(outline, Settings.color_menu_button_outline_dark.to_tuple(), outline_rect_right)

        screen.blit(outline, scaler(outline_rect))

        # block
        block_rect: pygame.Rect = pygame.Rect(self.rect.x+20, self.rect.y+20, self.rect.w-40, self.rect.h-40)
        screen.blit(self._draw_bevelled_rect(scaler, block_rect, 12, Settings.color_menu_button), scaler(block_rect))

        # text
        text_image: pygame.Surface; text_rect: pygame.Rect
        text_image, text_rect = fonts.dyuthi_b.render(text="Play", size=110, fgcolor=Settings.color_menu_button_border.to_tuple())
        text_rect.center = (809, 543)
        scaled_rect = scaler(text_rect)

        text_image = pygame.transform.smoothscale(text_image, scaled_rect.size)

        screen.blit(text_image, scaled_rect)

    @staticmethod
    def _draw_bevelled_rect(scaler: Callable[[pygame.Rect], pygame.Rect], rect: pygame.Rect, radius: int, color: Color) -> pygame.Surface:
        surf: pygame.Surface = pygame.Surface(scaler(rect).size, pygame.SRCALPHA)

        vertical: pygame.Rect = scaler(pygame.Rect(radius, 0, rect.w - radius*2, rect.h))
        pygame.draw.rect(surf, color.to_tuple(), vertical)

        horizontal: pygame.Rect = scaler(pygame.Rect(0, radius, rect.w, rect.h - radius*2))
        pygame.draw.rect(surf, color.to_tuple(), horizontal)

        curve_tl: pygame.Rect = scaler(pygame.Rect(radius, radius, radius, radius))
        curve_tr: pygame.Rect = scaler(pygame.Rect(rect.w-radius, radius, radius, radius))
        curve_bl: pygame.Rect = scaler(pygame.Rect(radius, rect.h-radius, radius, radius))
        curve_br: pygame.Rect = scaler(pygame.Rect(rect.w-radius, rect.h-radius, radius, radius))

        pygame.draw.circle(surf, color.to_tuple(), curve_tl.topleft, curve_tl.w)
        pygame.draw.circle(surf, color.to_tuple(), curve_tr.topleft, curve_tr.w)
        pygame.draw.circle(surf, color.to_tuple(), curve_bl.topleft, curve_bl.w)
        pygame.draw.circle(surf, color.to_tuple(), curve_br.topleft, curve_br.w)

        return surf
