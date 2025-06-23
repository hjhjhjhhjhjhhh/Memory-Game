import pygame
import random
import time
import sys
import os

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 400
CARD_NUMBER = 5 # DEFAULT 

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("記憶遊戲")
clock = pygame.time.Clock()
font = pygame.font.Font(resource_path("MSJHBD.TTC"), 36)
font_small = pygame.font.Font(resource_path("MSJHBD.TTC"), 24)
big_font = pygame.font.SysFont(None, 96)
pygame.mixer.init()
pygame.mixer.music.load(resource_path("bgm.mp3"))


# Load and scale images
back_image = pygame.image.load(resource_path("images/back.png"))
back_image = pygame.transform.scale(back_image, (100, 150))

# 從 1–10 中隨機挑選指定數量的卡片
chosen_ids = random.sample(range(1, 12), CARD_NUMBER)
# 載入並縮放       
front_images = []
for idx in chosen_ids:
    img = pygame.image.load(resource_path(f"images/{idx}.png"))
    img = pygame.transform.scale(img, (100, 150))
    front_images.append(img)

CARD_WIDTH, CARD_HEIGHT = 100, 150
GAP = 20

# Function to calculate positions based on card number
def calculate_positions(card_count):
    total_width = card_count * CARD_WIDTH + (card_count - 1) * GAP
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 10
    return [pygame.Rect(start_x + i * (CARD_WIDTH + GAP), y_pos, CARD_WIDTH, CARD_HEIGHT) for i in range(card_count)]

# Initialize positions
positions = calculate_positions(CARD_NUMBER)

# State variables
shown = [False] * 7
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

show_choose_message = False
choose_message_start = None

# Menu Buttons
start_button = pygame.Rect(400, 100, 200, 50)
option_button = pygame.Rect(400, 180, 200, 50)
back_button = pygame.Rect(20, 20, 105, 40)
replay_button = pygame.Rect(440, 300, 120, 40)

# Option Slider
slider_rect = pygame.Rect(300, 120, 200, 10)
slider_knob = pygame.Rect(300 + int((show_duration - 300) / 2000 * 200), 110, 20, 30)
dragging = False

card_number=[]
for i in range(3):
    card_number.append(pygame.Rect(300 + i * 150, 270, 100, 60))

def draw_main_menu():
    global start_button, option_button 

    temp_start_button = start_button.copy()
    temp_option_button = option_button.copy()

    if start_button.collidepoint(pygame.mouse.get_pos()):
        temp_start_button.inflate_ip(10, 5)
        start_button_color = (0, 200, 0)
    else:
        start_button_color = (34, 139, 34)

    if option_button.collidepoint(pygame.mouse.get_pos()):
        temp_option_button.inflate_ip(10, 5)
        option_button_color = (0, 0, 200)
    else:
        option_button_color = (25, 25, 112)


    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, start_button_color, temp_start_button, border_radius=5)
    pygame.draw.rect(screen, option_button_color, temp_option_button, border_radius=5)
    text_surface = font.render("開始遊戲", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=start_button.center)
    screen.blit(text_surface, text_rect)

    text_surface = font.render("選項", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=option_button.center)
    screen.blit(text_surface, text_rect)
    pygame.display.update()


def draw_options():

    global back_button

    screen.fill((240, 240, 240))
    screen.blit(font.render("翻牌顯示時間", True, (0, 0, 0)), (385, 40))
    
    # Slider bar and knob
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)
    pygame.draw.rect(screen, (100, 100, 100), slider_knob)

    # Duration text
    value_text = font.render(f"{show_duration} ms", True, (0, 0, 0))
    screen.blit(value_text, (slider_rect.right + 20, slider_rect.y - 20))

    # 卡排數目
    screen.blit(font.render(f"當前選擇的牌數: {CARD_NUMBER} 張", True, (0, 0, 0)), (330, 205))

    for i in range(3):
        if card_number[i].collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (170, 170, 170), card_number[i], border_radius=5)
        else:
            pygame.draw.rect(screen, (200, 200, 200), card_number[i], border_radius=5)

        text_surface = font_small.render(f"{3+i*2}", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=card_number[i].center)
        screen.blit(text_surface, text_rect)

    # Display the selected card number (current choice)
    # selected_card_text = font.render(f"當前選擇的牌數: {CARD_NUMBER} 張", True, (0, 0, 0))
    # screen.blit(selected_card_text, (600, 325))  # Place it below the card options

    # Back button
    temp_back_button = back_button.copy()
    if back_button.collidepoint(pygame.mouse.get_pos()):
        temp_back_button.inflate_ip(10, 5)
        back_button_color = (150, 0, 0)
    else:
        back_button_color = (200, 0, 0)
        
    pygame.draw.rect(screen, back_button_color, temp_back_button, border_radius=5)
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

    for i in range(CARD_NUMBER):
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

    if show_choose_message:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        choose_text = big_font.render("Start!", True, (0, 0, 0))
        screen.blit(choose_text, (SCREEN_WIDTH//2 - choose_text.get_width()//2, SCREEN_HEIGHT//2 - choose_text.get_height()//2))       

    # Back button
    temp_back_button = back_button.copy()
    if back_button.collidepoint(pygame.mouse.get_pos()) and game_phase != "countdown":
        temp_back_button.inflate_ip(10, 5)
        back_button_color = (150, 0, 0)
    else:
        back_button_color = (200, 0, 0)

    pygame.draw.rect(screen, back_button_color, temp_back_button, border_radius=5)
    text_surface = font_small.render("回到主頁", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=back_button.center)
    screen.blit(text_surface, text_rect)

    if game_phase == "done":
        temp_replay_button = replay_button.copy()
        if replay_button.collidepoint(pygame.mouse.get_pos()) and game_phase != "countdown":
            temp_replay_button.inflate_ip(10, 5)
            replay_button_color = (0, 150, 0)
        else:
            replay_button_color = (0, 180, 0)

        pygame.draw.rect(screen, replay_button_color, temp_replay_button, border_radius=5)
        text_surface = font_small.render("重新遊玩", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=replay_button.center)
        screen.blit(text_surface, text_rect)

    pygame.display.update()

def calculate_accuracy():
    return sum(1 for i in range(CARD_NUMBER) if i < len(clicked_order) and clicked_order[i] == reveal_order[i])

def start_game():
    global reveal_order, shown, clicked_order, show_index, showing, show_timer, front_images, positions, show_choose_message, choose_message_start

    # randomly choose specified number of images
    chosen_ids = random.sample(range(1, 12), CARD_NUMBER)
    # load      
    front_images = []
    for idx in chosen_ids:
        img = pygame.image.load(resource_path(f"images/{idx}.png"))
        img = pygame.transform.scale(img, (100, 150))
        front_images.append(img)

    # Recalculate positions based on current CARD_NUMBER
    positions = calculate_positions(CARD_NUMBER)
    
    shown = [False] * 7     # should be set to maximum 
    clicked_order = []
    reveal_order = list(range(CARD_NUMBER))
    random.shuffle(reveal_order)
    show_index = 0
    showing = False
    show_timer = 0

    show_choose_message = False
    choose_message_start = None

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
                    start_game()
                    countdown_start = time.time()
                    game_phase = "countdown"
                elif option_button.collidepoint(event.pos):
                    game_phase = "options"

        elif game_phase == "options":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if slider_knob.collidepoint(event.pos):
                    dragging = True

                elif card_number[0].collidepoint(event.pos):
                    CARD_NUMBER = 3
                    # Recalculate positions when card number changes
                    positions = calculate_positions(CARD_NUMBER)

                elif card_number[1].collidepoint(event.pos):
                    CARD_NUMBER = 5
                    # Recalculate positions when card number changes
                    positions = calculate_positions(CARD_NUMBER)

                elif card_number[2].collidepoint(event.pos):
                    CARD_NUMBER = 7
                    # Recalculate positions when card number changes
                    positions = calculate_positions(CARD_NUMBER)

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
                        if len(clicked_order) == CARD_NUMBER:
                            end_time = time.time()
                            game_phase = "done"
                        elif len(clicked_order) == 1:
                            start_time =time.time()

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
        
        if game_phase in ("countdown", "game", "input", "done"):
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()


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
            if not show_choose_message:
                show_choose_message = True
                choose_message_start = time.time()
            elif time.time() - choose_message_start >= 1.5:  # Show for 1.5 seconds
                show_choose_message = False
                game_phase = "input"
        draw_game()

    elif game_phase == "done":
        total_time = round(end_time - start_time, 2)
        accuracy = calculate_accuracy()
        screen_text = f"時間: {total_time}s  正確率: {accuracy}/{CARD_NUMBER}"
        draw_game(screen_text)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()