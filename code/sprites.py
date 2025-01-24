from settings import *
from timing import Timer


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class Bullet(Sprite):
    def __init__(self, pos, surf, direction, groups):
        super().__init__(pos, surf, groups)
        self.direction = direction
        self.speed = 850

        # adjustment
        self.image = pygame.transform.flip(self.image, direction == -1, False)

    def move(self, dt):
        self.rect.x += self.direction * self.speed * dt

    def update(self, dt):
        self.move(dt)


class Fire(Sprite):
    def __init__(self, pos, surf, groups, player):
        super().__init__(pos, surf, groups)
        self.player = player
        self.flip = player.flip
        self.timer = Timer(100, func=self.kill, autostart=True)
        self.y_offset = pygame.Vector2(0, 8)

        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset

    def update(self, dt):
        self.timer.update()

        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset

        if self.flip != self.player.flip:
            self.kill()


class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames, self.frame_index, self.animation_speed = frames, 0, 10
        super().__init__(pos, self.frames[self.frame_index], groups)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]


class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, frames, create_bullet):
        super().__init__(frames, pos, groups)
        self.hitbox_rect = self.rect.inflate(-10, 0)
        self.flip = False
        self.create_bullet = create_bullet

        # movement
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 400
        self.gravity = 50
        self.on_floor = False

        # timer
        self.shoot_timer = Timer(500)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_q]
        )
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -20

        if keys[pygame.K_RETURN] and not self.shoot_timer:
            self.create_bullet(self.rect.center, -1 if self.flip else 1)
            self.shoot_timer.activate()

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
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    self.direction.y = 0

    def check_floor(self):
        bottom_rect = pygame.Rect((0, 0), (self.hitbox_rect.width, 2)).move_to(
            midtop=self.hitbox_rect.midbottom
        )
        self.on_floor = (
            True
            if bottom_rect.collidelist(
                [sprite.rect for sprite in self.collision_sprites]
            )
            >= 0
            else False
        )

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += self.animation_speed * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0

        if not self.on_floor:
            self.frame_index = 1

        self.image = self.frames[int(self.frame_index % len(self.frames))]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def update(self, dt):
        self.shoot_timer.update()
        self.check_floor()
        self.input()
        self.move(dt)
        self.animate(dt)
