from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class Player(Sprite):
    def __init__(self, pos, groups, collision_sprites):
        surf = pygame.image.load(join("images", "player", "0.png")).convert_alpha()
        super().__init__(pos, surf, groups)
        # self.load_images()
        self.state = "stand"
        self.frame_index = 0
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-10, 0)

        # movement
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 400
        self.gravity = 50

    def load_images(self):
        self.frames = []

        for folder_path, sub_folders, files_names in walk(join("images", "player")):
            if files_names:
                for file_name in sorted(files_names, key=lambda name: int(name.split(".")[0])):
                    full_path = join(folder_path, file_name)
                    surface = pygame.image.load(full_path).convert_alpha()
                    self.frames.append(surface)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_q]
        )

    def move(self, dt):
        # horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision("horizontal")

        # vertical
        self.direction.y += self.gravity * dt
        self.hitbox_rect.y += self.direction.y
        self.collision("vertical")

        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if self.hitbox_rect.colliderect(sprite.rect):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                        self.direction.y = 0
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        pass
        # # get state
        # if self.direction.x != 0:
        #     self.state = "right" if self.direction.x > 0 else "left"
        # if self.direction.y != 0:
        #     self.state = "down" if self.direction.y > 0 else "up"

        # # animate
        # if self.direction:
        #     self.frame_index += 5 * dt
        # else:
        #     self.frame_index = 0
        # self.image = self.frames[self.state][
        #     int(self.frame_index) % len(self.frames[self.state])
        # ]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
