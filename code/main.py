from settings import *
from sprites import *
from groups import *
from support import *
from timing import Timer
from random import randint


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Platgaetformer")
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.gift_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game
        self.load_assets()
        self.setup()

        # timers
        self.bee_timer = Timer(500, func=self.create_bee, repeat=True, autostart=True)

        # score
        self.score = 0
        self.font = pygame.font.Font(None, 60)

    def load_assets(self):
        # graphics
        self.player_frames = import_folder("images", "player")
        self.bullet_surf = import_image("images", "gun", "bullet")
        self.fire_surf = import_image("images", "gun", "fire")
        self.gift_surf = import_image("images", "gift", "gift")
        self.bee_frames = import_folder("images", "enemies", "bee")
        self.homeless_frames = import_folder("images", "enemies", "homeless")

        # sounds
        self.audio = audio_importer("audio")

    def create_bee(self):
        x = self.level_width + WINDOW_WIDTH
        y = randint(0, self.level_height)
        Bee(
            self.bee_frames,
            (x, y),
            (self.all_sprites, self.enemy_sprites),
            randint(300, 500),
        )

    def create_bullet(self, pos, direction):
        if direction == 1:
            x = pos[0] + direction * 34
        else:
            x = pos[0] + direction * 34 - self.bullet_surf.get_width()

        Bullet(
            (x, pos[1]),
            self.bullet_surf,
            direction,
            (self.all_sprites, self.bullet_sprites),
        )
        Fire(pos, self.fire_surf, self.all_sprites, self.player)

        self.audio["shoot"].play()
        self.audio["shoot"].set_volume(0.2)

    # sprites
    def setup(self):
        map = load_pygame(join("data", "maps", "world.tmx"))
        self.level_width = map.width * TILE_SIZE
        self.level_height = map.height * TILE_SIZE

        for x, y, image in map.get_layer_by_name("Main").tiles():
            Sprite(
                (x * TILE_SIZE, y * TILE_SIZE),
                image,
                (self.all_sprites, self.collision_sprites),
            )

        for x, y, image in map.get_layer_by_name("Decoration").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites,
                    self.player_frames,
                    self.create_bullet,
                )
            if obj.name == "Homeless":
                Homeless(
                    self.homeless_frames,
                    pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                    (self.all_sprites, self.enemy_sprites),
                )
            if obj.name == "Gift":
                Sprite(
                    (obj.x, obj.y),
                    self.gift_surf,
                    (self.all_sprites, self.gift_sprites),
                )

        self.audio["music"].play(loops=-1)
        self.audio["music"].set_volume(0.1)

    def collision(self):
        # bullets / enemies
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(
                bullet, self.enemy_sprites, False, pygame.sprite.collide_mask
            )
            if sprite_collision:
                self.audio["impact"].play()
                self.audio["impact"].set_volume(0.3)
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()

        # player / gifts
        sprite_collision = pygame.sprite.spritecollide(
            self.player, self.gift_sprites, True, pygame.sprite.collide_mask
        )
        if sprite_collision:
            self.score += 1

        # player / enemies
        if pygame.sprite.spritecollide(
            self.player, self.enemy_sprites, False, pygame.sprite.collide_mask
        ):
            self.running = False

    def display_score(self):
        score_surface = self.font.render(
            str(f"{self.score} / 3"), True, "lightskyblue4"
        )
        score_rect = score_surface.get_frect(topright=(WINDOW_WIDTH - 20, 20))
        self.display_surface.blit(score_surface, score_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()

            # draw
            self.display_surface.fill(BG_COLOR)
            self.display_score()
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
