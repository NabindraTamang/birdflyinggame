import pygame as pg
import sys, time, os
from bird import Bird
from pipe import Pipe

pg.init()

class Game:
    def __init__(self):
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("Flappy Bird - Nabindra")
        self.clock = pg.time.Clock()
        self.move_speed = 250

        self.loadHighScore()
        self.reset_game()
        self.setUpBgAndGround()
        self.state = "menu"
        
        self.gameLoop()

    def loadHighScore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        else:
            self.highscore = 0

    def saveHighScore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def reset_game(self):
        self.bird = Bird(self.scale_factor)
        self.pipes = []
        self.pipe_generate_counter = 71
        self.score = 0
        self.game_running = False

    def gameLoop(self):
        last_time = time.time()

        while True:
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.saveHighScore()
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if self.state == "menu":
                        if event.key == pg.K_RETURN:
                            self.state = "game"
                            self.game_running = True
                            self.bird.update_on = True

                    elif self.state == "game":
                        if event.key == pg.K_SPACE:
                            self.bird.flap(dt)

                    elif self.state == "gameover":
                        if event.key == pg.K_RETURN:
                            self.reset_game()
                            self.state = "menu"

            if self.state == "game":
                self.updateEverything(dt)
                self.checkCollisions()

            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    def checkCollisions(self):
        if len(self.pipes):

            if self.bird.rect.bottom > 568:
                self.endGame()
                return

            if (self.bird.rect.colliderect(self.pipes[0].rect_down) or
                self.bird.rect.colliderect(self.pipes[0].rect_up)):
                self.endGame()
                return

            if self.pipes[0].rect_up.right < self.bird.rect.left:
                self.score += 5
                self.pipes.pop(0)

    def endGame(self):
        self.bird.update_on = False
        self.game_running = False
        self.state = "gameover"

        if self.score > self.highscore:
            self.highscore = self.score
            self.saveHighScore()

    def updateEverything(self, dt):
        if self.game_running:
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0
                
            self.pipe_generate_counter += 1

            for pipe in self.pipes:
                pipe.update(dt)

        self.bird.update(dt)

    def drawEverything(self):
        self.win.blit(self.bg_img, (0, -300))

        for pipe in self.pipes:
            pipe.drawPipe(self.win)

        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        font = pg.font.SysFont(None, 60)

        if self.state == "menu":
            t = font.render("Press ENTER to Start", True, (255,255,0))
            self.win.blit(t, (120, 350))

        elif self.state == "game":
            score_text = font.render(f"{self.score}", True, (255,255,255))
            self.win.blit(score_text, (280, 30))

        elif self.state == "gameover":
            go = font.render("GAME OVER", True, (255,0,0))
            hs = font.render(f"High Score: {self.highscore}", True, (255,255,255))
            restart = font.render("Press ENTER to Restart", True, (255,255,0))
            
            self.win.blit(go, (200, 300))
            self.win.blit(hs, (170, 360))
            self.win.blit(restart, (100, 420))

    def setUpBgAndGround(self):
        self.bg_img = pg.transform.scale_by(pg.image.load("assets/bg.png").convert(), self.scale_factor)
        self.ground1_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)
        self.ground2_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)
        
        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

game = Game()
