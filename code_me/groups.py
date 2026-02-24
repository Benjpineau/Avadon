from settings import *
from support import import_image
from entities import Entity

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        self.shadow_surf = import_image('graphics','other','shadow',scale_factor=0.4)

    def draw(self, player_center):
        self.offset.x = -(player_center[0] - WINDOW_WIDTH/2)
        self.offset.y = -(player_center[1] - WINDOW_HEIGHT/2)

        bg_sprites = [sprite for sprite in self if sprite.z < WORLD_LAYERS['main']]
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key= lambda sprite: sprite.y_sort)
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        for layer in (bg_sprites,main_sprites,fg_sprites):
            for sprite in layer:
                if isinstance(sprite,Entity):
                    self.display_surface.blit(self.shadow_surf, sprite.rect.topleft + self.offset+vector(15,40))
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

                # # Draw hitbox (for debugging purposes)
                # if hasattr(sprite, 'hitbox'):
                #     hitbox_rect = sprite.hitbox.move(self.offset)
                #     pygame.draw.rect(self.display_surface, (255, 0, 0), hitbox_rect, 2)  # Red hitbox
