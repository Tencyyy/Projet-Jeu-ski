import sys
import pygame
import random


WIDTH, HEIGHT = 800, 500
FPS = 60
TREE_SIZE = 26
GAP_WIDTH = 140
OBSTACLE_SPAWN_SEC = 0.9
OBSTACLE_SPEED = 3
GAP_CENTER_X = WIDTH // 2


def draw_stickman(screen, x, y):
    # bonhomme ultra simple (prototype)
    head_r = 12
    pygame.draw.circle(screen, (20, 20, 20), (int(x), int(y)), head_r, 2)
    body_y = y + head_r
    pygame.draw.line(screen, (20, 20, 20), (x, body_y), (x, body_y + 30), 2)
    pygame.draw.line(screen, (20, 20, 20), (x, body_y + 8), (x - 12, body_y + 18), 2)
    pygame.draw.line(screen, (20, 20, 20), (x, body_y + 8), (x + 12, body_y + 18), 2)
    pygame.draw.line(screen, (20, 20, 20), (x, body_y + 30), (x - 10, body_y + 45), 2)
    pygame.draw.line(screen, (20, 20, 20), (x, body_y + 30), (x + 10, body_y + 45), 2)

def spawn_obstacle_row():
    half_gap = GAP_WIDTH // 2
    min_center = half_gap + TREE_SIZE
    max_center = WIDTH - half_gap - TREE_SIZE
    gap_center = random.randint(min_center, max_center)
    gap_left = gap_center - half_gap
    gap_right = gap_center + half_gap
    y = -TREE_SIZE
    rects = []
    x = 0
    while x < WIDTH:
        next_x = x + TREE_SIZE
        if next_x <= gap_left or x >= gap_right:
            rects.append(pygame.Rect(x, y, TREE_SIZE, TREE_SIZE))
        x += TREE_SIZE
    return {
        "rects": rects,
        "gap_left": gap_left,
        "gap_right": gap_right,
        "checked": False,
    }


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ski Runner v1 - proto")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 20)
    big_font = pygame.font.SysFont("arial", 36)

    menu_bg = None
    try:
        menu_bg = pygame.image.load("assets/24.10.24-Milano-Cortina-1.webp").convert()
        menu_bg = pygame.transform.smoothscale(menu_bg, (WIDTH, HEIGHT))
    except pygame.error:
        menu_bg = None

    state = "menu"
    running = True

    # position du bonhomme
    px, py = WIDTH // 2, HEIGHT // 2
    speed = 4
    score = 0
    obstacles = []
    spawn_timer = 0.0
    paused = False

    while running:
        dt = clock.tick(FPS)
        dt_sec = dt / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if state == "menu" and event.key == pygame.K_RETURN:
                    state = "play"
                    score = 0
                    obstacles = []
                    spawn_timer = 0.0
                    paused = False
                    px, py = WIDTH // 2, HEIGHT // 2
                elif state == "game_over" and event.key == pygame.K_r:
                    state = "play"
                    score = 0
                    obstacles = []
                    spawn_timer = 0.0
                    paused = False
                    px, py = WIDTH // 2, HEIGHT // 2
                elif state == "game_over" and event.key == pygame.K_RETURN:
                    state = "menu"
                elif state == "play" and event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if state == "play" and not paused:
            # deplacement basique (pas d acceleration, pas de collision)
            if keys[pygame.K_LEFT]:
                px -= speed
            if keys[pygame.K_RIGHT]:
                px += speed
            if keys[pygame.K_UP]:
                py -= speed
            if keys[pygame.K_DOWN]:
                py += speed

            # bordures rough
            if px < 20:
                px = 20
            if px > WIDTH - 20:
                px = WIDTH - 20
            if py < 20:
                py = 20
            if py > HEIGHT - 20:
                py = HEIGHT - 20

            # spawn + move obstacles
            spawn_timer += dt_sec
            if spawn_timer >= OBSTACLE_SPAWN_SEC:
                spawn_timer = 0.0
                obstacles.append(spawn_obstacle_row())

            for row in obstacles:
                for rect in row["rects"]:
                    rect.y += OBSTACLE_SPEED

            # check pass/fail at player Y
            for row in obstacles:
                if not row["checked"] and row["rects"][0].y + TREE_SIZE >= py:
                    row["checked"] = True
                    if row["gap_left"] <= px <= row["gap_right"]:
                        score += 100
                    else:
                        state = "game_over"

            # remove offscreen
            obstacles = [row for row in obstacles if row["rects"][0].y < HEIGHT + TREE_SIZE]

        # rendu
        screen.fill((230, 240, 250))
        pygame.draw.rect(screen, (210, 225, 235), (0, HEIGHT - 80, WIDTH, 80))

        if state == "menu":
            if menu_bg:
                screen.blit(menu_bg, (0, 0))
            title = big_font.render("SKI RUNNER v1", True, (10, 10, 10))
            hint1 = font.render("ENTRER pour jouer", True, (10, 10, 10))
            hint2 = font.render("Fleches pour bouger", True, (10, 10, 10))
            hint3 = font.render("P pour pause", True, (10, 10, 10))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))
            screen.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 200))
            screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 230))
            screen.blit(hint3, (WIDTH // 2 - hint3.get_width() // 2, 260))
        elif state == "play":
            for row in obstacles:
                for rect in row["rects"]:
                    pygame.draw.rect(screen, (40, 170, 60), rect)
            draw_stickman(screen, px, py)
            hud = font.render(f"Score: {score}  (proto)", True, (10, 10, 10))
            screen.blit(hud, (10, 10))
            if paused:
                pause_txt = big_font.render("PAUSE", True, (10, 10, 10))
                screen.blit(pause_txt, (WIDTH // 2 - pause_txt.get_width() // 2, 120))
        else:
            over = big_font.render("GAME OVER (TEST)", True, (10, 10, 10))
            hint1 = font.render("R pour rejouer", True, (10, 10, 10))
            hint2 = font.render("ENTRER pour menu", True, (10, 10, 10))
            score_txt = font.render(f"Ton score: {score}", True, (10, 10, 10))
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, 160))
            screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 210))
            screen.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 250))
            screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 280))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
