import random
import pygame
import os

pygame.init()
pygame.font.init()

pygame.display.set_caption("Flappy Circle")

DEATH_FONT = pygame.font.Font(os.path.join("Assets","DeathFont.otf"), 100)
SCORE_FONT = pygame.font.Font(os.path.join("Assets", "JetBrainsMono-Regular.ttf"), 20)

WIDTH, HEIGHT = 800, 700
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

NEWPIPE = pygame.USEREVENT + 0
TIME = 1200
pygame.time.set_timer(NEWPIPE, TIME)

BIRD_RADIUS = 20
BIRD_GRAV = 0.3
BIRD_FLAP_STRENGHT = 11
BIRD_IMAGE = pygame.image.load(os.path.join("Assets", "Bird.png")).convert_alpha()

PIPE_WIDTH = 70
PIPE_SPEED = 4
PIPE_GAP = 160

AIR = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "air.jpg")), (WIDTH, HEIGHT))

BLUE_BACKGROUND = (50, 150, 255)
YELLOW = (255,255,0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

class Bird():
    def __init__(self):
        self.bird = pygame.draw.circle(WIN, YELLOW, (100, HEIGHT/2 - BIRD_RADIUS), BIRD_RADIUS)
        self.vel = 0
        self.flap = False
        self.dead = False
        self.score = 0
        self.score_list = []

    def move(self):
        self.vel += BIRD_GRAV if self.vel < 15 else 0
        if self.flap:
            self.vel -= BIRD_FLAP_STRENGHT
            self.vel = max(self.vel, -5)
            self.flap = False
        self.bird.y += self.vel
        self.bird.y = max(min(HEIGHT-BIRD_RADIUS, self.bird.y), 0 + BIRD_RADIUS )  

    def collision(self, pipe_list):
        for pipe in pipe_list:
            if self.bird.x + BIRD_RADIUS > pipe.pipe.x and self.bird.x - BIRD_RADIUS < pipe.pipe.x + PIPE_WIDTH: # pylint: disable=line-too-long
                if pipe.is_top:
                    if self.bird.y - BIRD_RADIUS < pipe.pipe.y + pipe.pipe.height and self.bird.y - BIRD_RADIUS > 0: # pylint: disable=line-too-long
                        self.dead = True
                else:
                    if self.bird.y + BIRD_RADIUS > pipe.pipe.y and self.bird.y - BIRD_RADIUS < HEIGHT: # pylint: disable=line-too-long
                        self.dead = True

    def update_score(self):
        if self.score_list:
            if self.bird.x > self.score_list[0].pipe.x:
                self.score += 1
                self.score_list.remove(self.score_list[0])


class Pipe():  # pylint: disable=too-few-public-methods
    def __init__(self, top, bottom, is_top):
        self.pipe = pygame.draw.rect(WIN, GREEN, (WIDTH - 1, top, PIPE_WIDTH, bottom))
        self.pipe.width = PIPE_WIDTH
        self.is_top = is_top

    def move(self, pipe_list):
        self.pipe.x -= PIPE_SPEED
        if self.pipe.x + PIPE_WIDTH < 0:
            pipe_list.remove(self)

# create a new pair of pipes
def create_pipe(bird, pipe_list):
    start_gap = random.randint(150, HEIGHT - 150 - PIPE_GAP)
    end_gap = start_gap + PIPE_GAP
    pipe1 = Pipe(0, start_gap, True)
    pipe2 = Pipe(end_gap, HEIGHT, False)
    pipe_list.append(pipe1)
    pipe_list.append(pipe2)
    bird.score_list.append(pipe1)
    return pipe_list

# return or update the highscore
def handle_highscore(highscore=0, new_score=False):
    if new_score and new_score > int(highscore):
        with open('highscore.txt', 'w') as file:
            file.write(str(new_score))
            return True
    else:
        try:
            with open('highscore.txt', 'r') as file:
                highscore = file.read()
                return highscore
        except FileNotFoundError:
            return 0

def draw_window(bird, pipe_list, highscore):
    WIN.blit(AIR, (0, 0))
    WIN.blit(BIRD_IMAGE, (bird.bird.x-BIRD_RADIUS, bird.bird.y-BIRD_RADIUS))
    for pipe in pipe_list:
        pygame.draw.rect(WIN, GREEN, (pipe.pipe.x, pipe.pipe.y, PIPE_WIDTH, pipe.pipe.height))
    score_text = SCORE_FONT.render("SCORE:" + str(bird.score), 1, BLACK)
    WIN.blit(score_text, (10, 10))
    highscore_text = SCORE_FONT.render("HIGHSCORE:" + str(highscore), 1, BLACK)
    WIN.blit(highscore_text, (WIDTH - highscore_text.get_width() - 10, 10))
    pygame.display.update()

def dead():
    draw_text = DEATH_FONT.render("YOU DIED!", 1, RED)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width()/2, HEIGHT/2 - draw_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1500)


def main():
    bird = Bird()
    pipe_list = []
    clock = pygame.time.Clock()
    run = True
    highscore = handle_highscore()
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap = True
                if event.key == pygame.K_p:
                    pygame.time.delay(5000)
            if event.type == NEWPIPE:
                pipe_list = create_pipe(bird, pipe_list)

        for pipe in pipe_list:
            pipe.move(pipe_list)

        bird.move()
        bird.collision(pipe_list)
        bird.update_score()
        draw_window(bird, pipe_list, highscore)

        if bird.dead:
            dead()
            break

    handle_highscore(highscore, bird.score)
    bird = None
    pipe_list = []
    pygame.event.get()
    main()


if __name__ == "__main__":
    main()
