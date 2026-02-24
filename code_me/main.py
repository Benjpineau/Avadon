from settings import *
from pytmx.util_pygame import load_pygame
from os.path import join 
from sprites import Sprite, PatchSprite, BorderSprite, TransitionSprite
from entities import Player, Character
from groups import AllSprites
from support import *
from game_data import TRAINER_DATA
from dialog import DialogTree








class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        pygame.display.set_caption('Avadon')
        self.clock = pygame.time.Clock()

        #Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.character_sprites = pygame.sprite.Group()
        self.transition_sprites = pygame.sprite.Group()

        #Transition/tint
        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 255
        self.tint_direction = -1
        self.tint_speed = 200

        self.import_assests()
        self.setup(self.tmx_maps['old_town'], 'old_town_swamp')

        self.dialog_tree = None



    def import_assests(self):
        self.tmx_maps={"city" : load_pygame(join('data','maps','map','city.tmx')),
                       "swamp" : load_pygame(join('data','maps','map','swamp.tmx')),
                       "old_town" : load_pygame(join('data','maps','map','old_town.tmx'))}
        

        self.overwolrd_frames = {
            'characters' : all_character_import('graphics','characters')
        }

        self.fonts = {
            'dialog' : pygame.font.Font(join('graphics','fonts','PixeloidSans.ttf'),30)
        }
     



    def setup(self, tmx_map, player_start_pos):
        #Clear the map
        for group in (self.all_sprites,self.collision_sprites,self.transition_sprites,self.character_sprites):
            group.empty()


        #Terrain
        for layer in ['water','tree_water','stone_ground','up_stone','ground','rocks','Dirt','Ground','Swamp','Bridge','Sand','Grass','Water','Town_floor','Town']:
            try:
                for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                    Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,WORLD_LAYERS['bg'])
            except ValueError:
                pass

        #Town
        for layer in ['Town_floor','Town']:
            try:
                for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                    Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,WORLD_LAYERS['main'])
            except ValueError:
                pass
        


        for layer in ['plants','fences','Plants']:
            try:
                for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                    Sprite((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,WORLD_LAYERS['main'])
            except ValueError:
                pass

        for layer in ['Entrance']:
            try:
                for obj in tmx_map.get_layer_by_name(layer):
                    PatchSprite((obj.x, obj.y), obj.image, self.all_sprites,obj.properties['offset'])
            except ValueError:
                pass


        #Objects
        for layer in ['Trees','buildings']:
            try:
                for obj in tmx_map.get_layer_by_name(layer):
                    if hasattr(obj, 'properties') and 'offset' in obj.properties and not hasattr(obj, 'properties') and 'scale' in obj.properties:
                        PatchSprite((obj.x, obj.y), obj.image, self.all_sprites ,obj.properties['offset'])
                    elif hasattr(obj, 'properties') and 'offset' in obj.properties and hasattr(obj, 'properties') and 'scale' in obj.properties:
                        PatchSprite((obj.x, obj.y), obj.image, self.all_sprites,obj.properties['offset'],scale=obj.properties['scale'])
                    else:
                        PatchSprite((obj.x, obj.y), obj.image, self.all_sprites,0)
            except ValueError:
                pass



        #Transition Object
        for obj in tmx_map.get_layer_by_name('Transition'):
            TransitionSprite((obj.x,obj.y),(obj.width, obj.height) ,(obj.properties['target'],obj.properties['pos']), self.transition_sprites)    



        #Collision Objects

        for obj in tmx_map.get_layer_by_name('Collisions'):
            BorderSprite((obj.x, obj.y),pygame.Surface((obj.width, obj.height)),self.collision_sprites)


        #Entities
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == "Player":
                if obj.properties['pos']==player_start_pos:
                    self.player = Player(
                        pos=(obj.x, obj.y),
                        frames=self.overwolrd_frames['characters']['mc_mini'],
                        groups=self.all_sprites,
                        facing_direction=obj.properties['direction'],
                        collision_sprites = self.collision_sprites)
                    
            else:
                Character(
                        pos=(obj.x, obj.y),
                        frames=self.overwolrd_frames['characters'][obj.properties['graphic']],
                        groups=(self.all_sprites,self.collision_sprites,self.character_sprites),
                        facing_direction=obj.properties['direction'],
                        character_data=TRAINER_DATA[obj.properties['character_id']])

        


    def input(self):
        if not self.dialog_tree:
            keys = pygame.key.get_just_pressed()
            if keys[pygame.K_SPACE]:
                for character in self.character_sprites:
                    if check_connections(100,self.player, character):
                        #block player input
                        self.player.block()
                        #Entities face each other
                        character.change_facing_direction(self.player.rect.center)

                        #Create Dialog
                        self.create_dialog(character)

    def create_dialog(self,character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(character, self.player, self.all_sprites, self.fonts['dialog'],self.end_dialog)

    def end_dialog(self,character):
        self.dialog_tree = None
        self.player.unblock()


    def transition_check(self):
        sprites = [sprite for sprite in self.transition_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites:
            self.player.block()
            self.transition_target = sprites[0].target
            self.tint_mode = 'tint'
    
    def tint_screen(self,dt):

        if self.tint_mode=='untint':
            self.tint_progress -= self.tint_speed*dt


        if self.tint_mode == 'tint':
            self.tint_progress += self.tint_speed*dt
            if self.tint_progress >= 255:
                self.setup(self.tmx_maps[self.transition_target[0]],self.transition_target[1])
                self.tint_mode = 'untint'
                self.transition_target = None

        self.tint_progress = max(0, min(self.tint_progress,255))
        print(self.tint_progress)
        self.tint_surf.set_alpha(self.tint_progress)
        if self.tint_progress !=0:
            self.display_surface.blit(self.tint_surf, (0,0))




    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            self.display_surface.fill('black')
            #Looping events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


            #Update
            self.input()
            self.transition_check()
            self.all_sprites.update(dt)

            #Drawing
            self.all_sprites.draw(self.player.rect.center)

            self.tint_screen(dt)
            pygame.display.update()

            #Overlays

            if self.dialog_tree: self.dialog_tree.update()
            


if __name__ == "__main__":
    game = Game()
    game.run()