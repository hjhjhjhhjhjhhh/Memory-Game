import pygame
import random
import time

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("記憶遊戲")
clock = pygame.time.Clock()
font = pygame.font.Font("MSJHBD.TTC", 36)
font_small = pygame.font.Font("MSJHBD.TTC", 24)
big_font = pygame.font.SysFont(None, 96)


# Load and scale images
back_image = pygame.image.load("images/back.png")
back_image = pygame.transform.scale(back_image, (100, 150))
#front_images = [pygame.image.load(f"images/{i}.png") for i in range(1, 6)]
#front_images = [pygame.image.load(f"images/1.png") for i in range(1, 6)]
#front_images = [pygame.transform.scale(img, (100, 150)) for img in front_images]
# 從 1–10 中隨機挑 5 張
chosen_ids = random.sample(range(1, 12), 5)
# 載入並縮放       
front_images = []
for idx in chosen_ids:
    img = pygame.image.load(f"images/{idx}.png")
    img = pygame.transform.scale(img, (100, 150))
    front_images.append(img)

CARD_WIDTH, CARD_HEIGHT = 100, 150
GAP = 20
TOTAL_WIDTH = 5 * CARD_WIDTH + 4 * GAP
START_X = (SCREEN_WIDTH - TOTAL_WIDTH) // 2
Y_POS = (SCREEN_HEIGHT - CARD_HEIGHT) // 2
positions = [pygame.Rect(START_X + i * (CARD_WIDTH + GAP), Y_POS, CARD_WIDTH, CARD_HEIGHT) for i in range(5)]

# State variables
shown = [False] * 5
clicked_order = []
reveal_order = []
start_time = None
end_time = None
game_phase = "menu"
show_index = 0
showing = False
show_timer = 0
show_duration = 1500

countdown_start = None

# Menu Buttons
start_button = pygame.Rect(300, 100, 200, 50)
option_button = pygame.Rect(300, 180, 200, 50)
back_button = pygame.Rect(20, 20, 100, 40)
replay_button = pygame.Rect(20, 230, 100, 40)


# Option Slider
slider_rect = pygame.Rect(300, 150, 200, 10)
slider_knob = pygame.Rect(300 + int((show_duration - 300) / 2000 * 200), 140, 20, 30)
dragging = False

def draw_main_menu():
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0, 200, 0), start_button)
    pygame.draw.rect(screen, (0, 0, 200), option_button)
    text_surface = font.render("開始遊戲", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=start_button.center)
    screen.blit(text_surface, text_rect)

    text_surface = font.render("選項", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=option_button.center)
    screen.blit(text_surface, text_rect)
    pygame.display.update()


def draw_options():
    screen.fill((240, 240, 240))
    screen.blit(font.render("翻牌顯示時間", True, (0, 0, 0)), (300, 80))
    
    # Slider bar and knob
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)
    pygame.draw.rect(screen, (100, 100, 100), slider_knob)

    # Duration text
    value_text = font.render(f"{show_duration} ms", True, (0, 0, 0))
    screen.blit(value_text, (slider_rect.right + 20, slider_rect.y - 10))


    # 卡排數目 (尚未做)
    # screen.blit(font.render("幾張牌數", True, (0, 0, 0)), (300, 200))


    # Back button
    pygame.draw.rect(screen, (150, 0, 0), back_button)
    text_surface = font_small.render("回到主頁", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=back_button.center)
    screen.blit(text_surface, text_rect)

    pygame.display.update()


def draw_countdown():
    elapsed = time.time() - countdown_start
    number = 3 - int(elapsed)

    if number > 0:
        text = big_font.render(str(number), True, (0, 0, 0))
    elif elapsed <= 3.5:
        text = big_font.render("Go!", True, (0, 0, 0))    
    else:
        return True, None  # Countdown finished

    return False, text  # Still counting


def draw_game(screen_text="", countdown_text=""):
    screen.fill((255, 255, 255))

    for i in range(5):
        img = front_images[i] if shown[i] else back_image
        screen.blit(img, positions[i])

        if game_phase == "done":
            if i in clicked_order:
                click_index = clicked_order.index(i)
                color = (0, 255, 0) if reveal_order[click_index] == i else (255, 0, 0)
            else:
                color = (200, 200, 200)
            pygame.draw.rect(screen, color, positions[i], 4)

    if screen_text:
        # rendered = font.render(text, True, (0, 0, 0))
        # screen.blit(rendered, (50, 20))
        rendered = font.render(screen_text, True, (0, 0, 0))
        text_rect = rendered.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.top = 20  # Adjust this as needed for vertical spacing
        screen.blit(rendered, text_rect)


    # Add a semi-transparent overlay in countdown phase 
    if game_phase == "countdown": 
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        if countdown_text: 
            screen.blit(countdown_text, (SCREEN_WIDTH//2 - countdown_text.get_width()//2, SCREEN_HEIGHT//2 - countdown_text.get_height()//2))       

    # Draw back button
    pygame.draw.rect(screen, (150, 0, 0), back_button)
    text_surface = font_small.render("回到主頁", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=back_button.center)
    screen.blit(text_surface, text_rect)

    if game_phase == "done":
        pygame.draw.rect(screen, (0, 150, 0), replay_button)
        text_surface = font_small.render("重新遊玩", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=replay_button.center)
        screen.blit(text_surface, text_rect)


    pygame.display.update()


def calculate_accuracy():
    return sum(1 for i in range(5) if i < len(clicked_order) and clicked_order[i] == reveal_order[i])


def start_game():
    global reveal_order, shown, clicked_order, show_index, showing, show_timer, front_images

    # randomly choose 5 image
    chosen_ids = random.sample(range(1, 12), 5)
    # load      
    front_images = []
    for idx in chosen_ids:
        img = pygame.image.load(f"images/{idx}.png")
        img = pygame.transform.scale(img, (100, 150))
        front_images.append(img)

    shown = [False] * 5
    clicked_order = []
    reveal_order = list(range(5))
    random.shuffle(reveal_order)
    show_index = 0
    showing = False
    show_timer = 0


running = True
while running:
    now = pygame.time.get_ticks()
    elapsed = 0
    screen_text = ""

    # --- HANDLE EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_phase == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    countdown_start = time.time()
                    game_phase = "countdown"
                elif option_button.collidepoint(event.pos):
                    game_phase = "options"

        elif game_phase == "options":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if slider_knob.collidepoint(event.pos):
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                x = min(max(slider_rect.x, event.pos[0]), slider_rect.x + slider_rect.width)
                slider_knob.x = x
                ratio = (x - slider_rect.x) / slider_rect.width
                show_duration = int(300 + ratio * 2000)

        elif game_phase == "input":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(positions):
                    if rect.collidepoint(event.pos) and not shown[i] and i not in clicked_order:
                        clicked_order.append(i)
                        shown[i] = True
                        draw_game()
                        if len(clicked_order) == 5:
                            end_time = time.time()
                            game_phase = "done"
        
        elif game_phase == "done":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    game_phase = "menu"
                elif replay_button.collidepoint(event.pos):
                    start_game()
                    countdown_start = time.time()
                    game_phase = "countdown"

        # handle back to menu
        if game_phase in ("options", "game", "input", "done"):
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                game_phase = "menu"

    # --- UPDATE GAME STATE ---
    if game_phase == "menu":
        draw_main_menu()

    elif game_phase == "options":
        draw_options()


    elif game_phase == "countdown":
        countdown_finished, countdown_text = draw_countdown()
        draw_game(countdown_text=countdown_text)
        if countdown_finished:
            start_game()
            game_phase = "game"
            start_time = time.time()


    elif game_phase == "game":
        if not showing and show_index < len(reveal_order):
            showing = True
            shown[reveal_order[show_index]] = True
            show_timer = now
        elif showing and now - show_timer >= show_duration:
            shown[reveal_order[show_index]] = False
            show_index += 1
            showing = False
            show_timer = now
        elif show_index >= len(reveal_order):
            game_phase = "input"
        draw_game()

    elif game_phase == "done":
        total_time = round(end_time - start_time, 2)
        accuracy = calculate_accuracy()
        screen_text = f"時間: {total_time}s  正確率: {accuracy}/5"
        draw_game(screen_text)

    pygame.display.flip()
    clock.tick(30)


pygame.quit()
