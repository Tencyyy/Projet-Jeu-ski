import sys
import random
import pygame


WIDTH, HEIGHT = 900, 600
FPS = 60


class Gate:
    def __init__(self, y, gap_x, gap_w, speed):
        self.y = y
        self.gap_x = gap_x
        self.gap_w = gap_w
        self.speed = speed
        self.h = 60

    def update(self, dt):
        self.y += self.speed * dt

    def rects(self):
        left = pygame.Rect(0, int(self.y), int(self.gap_x), self.h)
        right = pygame.Rect(int(self.gap_x + self.gap_w), int(self.y), WIDTH - int(self.gap_x + self.gap_w), self.h)
        return left, right

    def draw(self, screen):
        left, right = self.rects()
        pygame.draw.rect(screen, (30, 110, 50), left)
        pygame.draw.rect(screen, (30, 110, 50), right)
        pygame.draw.rect(screen, (10, 70, 35), left, 2)
        pygame.draw.rect(screen, (10, 70, 35), right, 2)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def draw_background(screen, snowflakes):
    for i in range(HEIGHT):
        shade = 228 + int(16 * (i / HEIGHT))
        screen.fill((shade, shade + 6, 255), rect=pygame.Rect(0, i, WIDTH, 1))
    for f in snowflakes:
        pygame.draw.circle(screen, (245, 250, 255), (int(f["x"]), int(f["y"])), int(f["r"]))


def build_snowflakes(count=100):
    flakes = []
    for _ in range(count):
        r = random.choice([2, 2, 3])
        flakes.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT),
            "r": r,
            "spd": random.uniform(25, 60) if r >= 3 else random.uniform(30, 80),
            "drift": random.uniform(-18, 18),
        })
    return flakes


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ski Runner V3 - test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    big_font = pygame.font.SysFont("arial", 36)

    state = "menu"
    mode = 1  # 1 solo, 3 vs yeti
    running = True
    snowflakes = build_snowflakes(110)

    button_style = {
        "bg": (235, 245, 255),
        "border": (30, 60, 90),
        "active": (30, 60, 90),
        "text": (20, 30, 40),
    }

    def get_menu_buttons():
        panel_w, panel_h = 600, 360
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = HEIGHT // 2 - panel_h // 2
        btn_w, btn_h = 220, 46
        btn_solo = pygame.Rect(panel_x + 40, panel_y + 110, btn_w, btn_h)
        btn_vs = pygame.Rect(panel_x + 40, panel_y + 170, btn_w, btn_h)
        btn_start = pygame.Rect(panel_x + panel_w - btn_w - 40, panel_y + 230, btn_w, btn_h)
        return {
            "panel": (panel_x, panel_y, panel_w, panel_h),
            "solo": btn_solo,
            "vs": btn_vs,
            "start": btn_start,
        }

    def reset_game():
        return {
            "p1": {"x": WIDTH // 2 - 40, "y": HEIGHT - 140, "w": 26, "h": 38, "speed": 240},
            "p2": {"x": WIDTH // 2 + 40, "y": HEIGHT - 140, "w": 26, "h": 38, "speed": 240},
            "gates": [],
            "spawn_timer": 0.0,
            "score": 0,
            "time": 0.0,
            "over_text": "",
        }

    data = reset_game()

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_1:
                        mode = 1
                    if event.key == pygame.K_2:
                        mode = 3
                    if event.key == pygame.K_RETURN:
                        state = "play"
                        data = reset_game()
                elif state == "game_over":
                    if event.key == pygame.K_r:
                        state = "play"
                        data = reset_game()
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu":
                    btns = get_menu_buttons()
                    mx, my = event.pos
                    if btns["solo"].collidepoint(mx, my):
                        mode = 1
                    if btns["vs"].collidepoint(mx, my):
                        mode = 3
                    if btns["start"].collidepoint(mx, my):
                        state = "play"
                        data = reset_game()
                elif state == "game_over":
                    mx, my = event.pos
                    btn_retry = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 50, 140, 36)
                    btn_menu = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 50, 140, 36)
                    if btn_retry.collidepoint(mx, my):
                        state = "play"
                        data = reset_game()
                    if btn_menu.collidepoint(mx, my):
                        state = "menu"

        keys = pygame.key.get_pressed()

        if state == "play":
            data["time"] += dt
            data["score"] += int(12 * dt)

            p1 = data["p1"]
            p2 = data["p2"]

            # player 1 (arrows)
            if keys[pygame.K_LEFT]:
                p1["x"] -= p1["speed"] * dt
            if keys[pygame.K_RIGHT]:
                p1["x"] += p1["speed"] * dt
            if keys[pygame.K_UP]:
                p1["y"] -= p1["speed"] * dt
            if keys[pygame.K_DOWN]:
                p1["y"] += p1["speed"] * dt

            # player 2 (WASD) for duo / vs yeti
            if mode == 3:
                if keys[pygame.K_a]:
                    p2["x"] -= p2["speed"] * dt
                if keys[pygame.K_d]:
                    p2["x"] += p2["speed"] * dt
                if keys[pygame.K_w]:
                    p2["y"] -= p2["speed"] * dt
                if keys[pygame.K_s]:
                    p2["y"] += p2["speed"] * dt

            p1["x"] = clamp(p1["x"], 10, WIDTH - p1["w"] - 10)
            p1["y"] = clamp(p1["y"], 70, HEIGHT - p1["h"] - 10)
            p2["x"] = clamp(p2["x"], 10, WIDTH - p2["w"] - 10)
            p2["y"] = clamp(p2["y"], 70, HEIGHT - p2["h"] - 10)

            # gates
            data["spawn_timer"] += dt
            if data["spawn_timer"] >= 1.2:
                data["spawn_timer"] = 0.0
                gap_w = random.randint(160, 240)
                gap_x = random.randint(80, WIDTH - 80 - gap_w)
                data["gates"].append(Gate(-60, gap_x, gap_w, 220))

            for g in data["gates"][:]:
                g.update(dt)
                if g.y > HEIGHT + 60:
                    data["gates"].remove(g)

            # collisions
            p1_rect = pygame.Rect(int(p1["x"]), int(p1["y"]), p1["w"], p1["h"])
            p2_rect = pygame.Rect(int(p2["x"]), int(p2["y"]), p2["w"], p2["h"])

            for g in data["gates"]:
                left, right = g.rects()
                if p1_rect.colliderect(left) or p1_rect.colliderect(right):
                    data["over_text"] = "P1 touche un couloir"
                    state = "game_over"
            if mode == 3:
                if p1_rect.colliderect(p2_rect):
                    data["over_text"] = "YETI attrape P1"
                    state = "game_over"

        # draw
        for f in snowflakes:
            f["y"] += f["spd"] * dt
            f["x"] += f["drift"] * dt
            if f["y"] > HEIGHT + 10:
                f["y"] = random.randint(-200, -20)
                f["x"] = random.randint(0, WIDTH)
            if f["x"] < -10:
                f["x"] = WIDTH + 10
            if f["x"] > WIDTH + 10:
                f["x"] = -10

        draw_background(screen, snowflakes)
        pygame.draw.rect(screen, (210, 225, 235), (0, HEIGHT - 80, WIDTH, 80))

        if state == "menu":
            btns = get_menu_buttons()
            panel_x, panel_y, panel_w, panel_h = btns["panel"]

            shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 110))
            screen.blit(shadow, (panel_x - 7, panel_y - 4))

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            for i in range(panel_h):
                shade = 242 + int(8 * (i / panel_h))
                panel.fill((shade, shade + 4, 255, 230), rect=pygame.Rect(0, i, panel_w, 1))
            pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel, (255, 255, 255, 120), (6, 6, panel_w - 12, panel_h - 12), 1)
            pygame.draw.rect(panel, (220, 235, 248, 220), (0, 0, panel_w, 70))
            pygame.draw.line(panel, (170, 195, 215, 200), (24, 66), (panel_w - 24, 66), 2)
            screen.blit(panel, (panel_x, panel_y))

            title = big_font.render("V3 TEST - MODES", True, (30, 40, 60))
            subtitle = font.render("Choisis ton mode avec la souris", True, (60, 80, 110))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 16))
            screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, panel_y + 48))

            mouse = pygame.mouse.get_pos()
            for rect, label, active in [
                (btns["solo"], "SOLO", mode == 1),
                (btns["vs"], "1v1 YETI", mode == 3),
            ]:
                is_hover = rect.collidepoint(mouse)
                bg = button_style["active"] if active or is_hover else button_style["bg"]
                text_col = (235, 245, 255) if active or is_hover else button_style["text"]
                pygame.draw.rect(screen, bg, rect, border_radius=8)
                pygame.draw.rect(screen, button_style["border"], rect, 2, border_radius=8)
                txt = font.render(label, True, text_col)
                screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

            pygame.draw.rect(screen, (30, 60, 90), btns["start"], border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), btns["start"], 1, border_radius=8)
            start_txt = font.render("DEMARRER", True, (235, 245, 255))
            screen.blit(start_txt, (btns["start"].centerx - start_txt.get_width() // 2, btns["start"].centery - start_txt.get_height() // 2))

            tips = [
                "P1: fleches",
                "P2: WASD (yeti)",
                "Clique sur un mode puis demarrer",
            ]
            ty = panel_y + 120
            for line in tips:
                txt = font.render(line, True, (20, 30, 40))
                screen.blit(txt, (panel_x + panel_w - 240, ty))
                ty += 26

        elif state == "play":
            for g in data["gates"]:
                g.draw(screen)

            # players
            p1 = data["p1"]
            pygame.draw.rect(screen, (30, 60, 200), (int(p1["x"]), int(p1["y"]), p1["w"], p1["h"]))
            pygame.draw.circle(screen, (220, 230, 255), (int(p1["x"] + p1["w"] / 2), int(p1["y"] + 6)), 6)

            if mode in (2, 3):
                p2 = data["p2"]
                color = (200, 40, 40) if mode == 3 else (40, 120, 60)
                pygame.draw.rect(screen, color, (int(p2["x"]), int(p2["y"]), p2["w"], p2["h"]))
                pygame.draw.circle(screen, (240, 220, 220), (int(p2["x"] + p2["w"] / 2), int(p2["y"] + 6)), 6)

            hud_panel = pygame.Surface((WIDTH, 46), pygame.SRCALPHA)
            hud_panel.fill((245, 250, 255, 185))
            pygame.draw.line(hud_panel, (210, 225, 235, 200), (0, 44), (WIDTH, 44), 2)
            screen.blit(hud_panel, (0, 0))
            hud = font.render(f"Score: {data['score']}  Temps: {data['time']:.1f}s", True, (20, 30, 40))
            screen.blit(hud, (14, 12))

        else:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((15, 20, 30, 140))
            screen.blit(overlay, (0, 0))
            panel_w, panel_h = 420, 220
            panel_x = WIDTH // 2 - panel_w // 2
            panel_y = HEIGHT // 2 - panel_h // 2
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((250, 252, 255, 235))
            pygame.draw.rect(panel, (200, 220, 235, 220), (0, 0, panel_w, panel_h), 2)
            screen.blit(panel, (panel_x, panel_y))

            over = big_font.render("GAME OVER", True, (200, 40, 40))
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, panel_y + 20))
            reason = font.render(data.get("over_text", ""), True, (20, 20, 20))
            screen.blit(reason, (WIDTH // 2 - reason.get_width() // 2, panel_y + 70))

            btn_retry = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 50, 140, 36)
            btn_menu = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 50, 140, 36)
            pygame.draw.rect(screen, (30, 60, 90), btn_retry, border_radius=6)
            pygame.draw.rect(screen, (30, 60, 90), btn_menu, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), btn_retry, 1, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), btn_menu, 1, border_radius=6)
            retry_txt = font.render("REJOUER", True, (235, 245, 255))
            menu_txt = font.render("MENU", True, (235, 245, 255))
            screen.blit(retry_txt, (btn_retry.centerx - retry_txt.get_width() // 2, btn_retry.centery - retry_txt.get_height() // 2))
            screen.blit(menu_txt, (btn_menu.centerx - menu_txt.get_width() // 2, btn_menu.centery - menu_txt.get_height() // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
