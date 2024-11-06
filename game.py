import pygame
import random
import string
import math
import json
from enum import Enum
from datetime import datetime

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4
    SETTINGS = 5
    STATISTICS = 6

class KeyboardTrainer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Инициализация звука
        self.WIDTH = 1200
        self.HEIGHT = 900
        # self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.fullscreen = False  # Добавьте флаг для отслеживания состояния полноэкранного режима
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)  # Начальный режим окна

        pygame.display.set_caption("Клавиатурный тренажёр")

        # Цвета
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)

        # Шрифты
        self.main_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 36)

        # Настройки сложности
        self.difficulty_levels = {
            "Легкий": {"speed": 2, "spawn_rate": 1.0, "letters": string.ascii_uppercase},
            "Средний": {"speed": 3, "spawn_rate": 1.2, "letters": string.ascii_uppercase + string.digits},
            "Сложный": {"speed": 5, "spawn_rate": 1.5, "letters": string.ascii_uppercase + string.digits}
        }
        self.current_difficulty = "Средний"
        
        # Настройки игры
        self.settings = {
            "sound_enabled": True,
            "particles_enabled": True,
            "dark_mode": True,
            "letter_effects": True
        }
        
        # Статистика
        self.stats = self.load_statistics()
        self.session_start_time = None
        
        # Игровое состояние
        self.game_state = GameState.MENU
        self.particles = []
        
        # Загрузка звуков
        self.sounds = {
            "correct": pygame.mixer.Sound("sounds/correct.mp3") if pygame.mixer.get_init() else None,
            "wrong": pygame.mixer.Sound("sounds/incorrect.mp3") if pygame.mixer.get_init() else None,
            "level_up": pygame.mixer.Sound("sounds/new_level.mp3") if pygame.mixer.get_init() else None
        }
        
        # Инициализация игровых параметров
        self.reset_game()

    def load_statistics(self):
        try:
            with open("statistics.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "total_games": 0,
                "total_time": 0,
                "best_scores": {"Легкий": 0, "Средний": 0, "Сложный": 0},
                "average_accuracy": 0,
                "total_keys_pressed": 0,
                "correct_keys_pressed": 0,
                "longest_combo": 0,
                "last_session": None
            }

    def save_statistics(self):
        with open("statistics.json", "w") as f:
            json.dump(self.stats, f)

    def reset_game(self):
        self.letters = []
        self.score = 0
        self.missed = 0
        self.base_speed = self.difficulty_levels[self.current_difficulty]["speed"]
        self.level = 1
        self.combo = 0
        self.max_combo = 0
        self.spawn_timer = 0
        self.total_keys_pressed = 0
        self.correct_keys_pressed = 0
        self.accuracy = 100
        self.session_start_time = datetime.now()
        self.particles = []

    def create_particle_effect(self, x, y, color):
        if self.settings["particles_enabled"]:
            for _ in range(10):
                angle = random.uniform(0, 360)
                speed = random.uniform(2, 5)
                self.particles.append({
                    'x': x,
                    'y': y,
                    'dx': speed * math.cos(math.radians(angle)),
                    'dy': speed * math.sin(math.radians(angle)),
                    'color': color,
                    'life': 1.0
                })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 0.02
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def spawn_letter(self):
        available_chars = self.difficulty_levels[self.current_difficulty]["letters"]
        letter = random.choice(available_chars)
        x = random.randint(50, self.WIDTH - 50)
        self.letters.append({
            'char': letter,
            'x': x,
            'y': 0,
            'speed': self.base_speed * (1 + self.level * 0.1),
            'color': self.WHITE,
            'scale': 1.0,
            'rotation': 0
        })

    def draw_menu(self):
        background_color = self.BLACK if self.settings["dark_mode"] else self.WHITE
        text_color = self.WHITE if self.settings["dark_mode"] else self.BLACK
        
        self.window.fill(background_color)
        
        title = self.main_font.render("Клавиатурный тренажёр", True, self.BLUE)
        start_text = self.menu_font.render("ПРОБЕЛ - Начать игру", True, text_color)
        settings_text = self.menu_font.render("S - Настройки", True, text_color)
        stats_text = self.menu_font.render("T - Статистика", True, text_color)
        difficulty_text = self.menu_font.render(f"Сложность: {self.current_difficulty} (←→)", True, text_color)
        
        texts = [
            (title, 100),
            (start_text, 250),
            (settings_text, 320),
            (stats_text, 390),
            (difficulty_text, 460)
        ]
        
        for text, y in texts:
            self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, y))

    def draw_settings(self):
        self.window.fill(self.BLACK)
        title = self.menu_font.render("Настройки", True, self.WHITE)
        self.window.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))

        settings_items = [
            ("Звук", self.settings["sound_enabled"]),
            ("Частицы", self.settings["particles_enabled"]),
            ("Тёмная тема", self.settings["dark_mode"]),
            ("Эффекты букв", self.settings["letter_effects"])
        ]

        for i, (setting_name, value) in enumerate(settings_items):
            text = self.menu_font.render(f"{setting_name}: {'Вкл' if value else 'Выкл'}", True, self.WHITE)
            self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, 150 + i * 60))

        back_text = self.small_font.render("ESC - Вернуться в меню", True, self.WHITE)
        self.window.blit(back_text, (self.WIDTH//2 - back_text.get_width()//2, self.HEIGHT - 50))

    def draw_statistics(self):
        self.window.fill(self.BLACK)
        title = self.menu_font.render("Статистика", True, self.WHITE)
        self.window.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))

        stats_items = [
            f"Всего игр: {self.stats['total_games']}",
            f"Общее время: {self.stats['total_time'] // 3600}ч {(self.stats['total_time'] % 3600) // 60}м",
            f"Рекорд (Легкий): {self.stats['best_scores']['Легкий']}",
            f"Рекорд (Средний): {self.stats['best_scores']['Средний']}",
            f"Рекорд (Сложный): {self.stats['best_scores']['Сложный']}",
            f"Средняя точность: {self.stats['average_accuracy']}%",
            f"Лучшее комбо: {self.stats['longest_combo']}"
        ]

        for i, stat in enumerate(stats_items):
            text = self.small_font.render(stat, True, self.WHITE)
            self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, 150 + i * 40))

        back_text = self.small_font.render("ESC - Вернуться в меню", True, self.WHITE)
        self.window.blit(back_text, (self.WIDTH//2 - back_text.get_width()//2, self.HEIGHT - 50))

    def draw_game(self):
        background_color = self.BLACK if self.settings["dark_mode"] else self.WHITE
        text_color = self.WHITE if self.settings["dark_mode"] else self.BLACK
        
        self.window.fill(background_color)
        
        # Отрисовка частиц
        if self.settings["particles_enabled"]:
            for particle in self.particles:
                alpha = int(255 * particle['life'])
                color = (*particle['color'][:3], alpha)
                pygame.draw.circle(self.window, color, 
                                 (int(particle['x']), int(particle['y'])), 3)

        # Отрисовка букв с эффектами
        for letter in self.letters:
            if self.settings["letter_effects"]:
                letter['rotation'] = math.sin(pygame.time.get_ticks() * 0.003) * 10
                letter['scale'] = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.1

            text = self.main_font.render(letter['char'], True, letter['color'])
            if self.settings["letter_effects"]:
                text = pygame.transform.rotozoom(text, letter['rotation'], letter['scale'])
            
            self.window.blit(text, (letter['x'] - text.get_width()//2, letter['y']))

        # Отрисовка игровой информации
        info_texts = [
            (f"Счёт: {self.score}", self.WHITE),
            (f"Уровень: {self.level}", self.GREEN),
            (f"Комбо: {self.combo}", self.BLUE),
            (f"Макс. комбо: {self.max_combo}", self.YELLOW),
            (f"Точность: {self.accuracy}%", self.WHITE)
        ]

        for i, (text, color) in enumerate(info_texts):
            surface = self.menu_font.render(text, True, color)
            self.window.blit(surface, (10, 10 + i * 50))

    def update_statistics(self):
        session_duration = int((datetime.now() - self.session_start_time).total_seconds())
        self.stats["total_games"] += 1
        self.stats["total_time"] += session_duration
        self.stats["best_scores"][self.current_difficulty] = max(
            self.stats["best_scores"][self.current_difficulty], 
            self.score
        )
        self.stats["longest_combo"] = max(self.stats["longest_combo"], self.max_combo)
        self.stats["total_keys_pressed"] += self.total_keys_pressed
        self.stats["correct_keys_pressed"] += self.correct_keys_pressed
        self.stats["average_accuracy"] = round(
            (self.stats["correct_keys_pressed"] / max(1, self.stats["total_keys_pressed"])) * 100
        )
        self.stats["last_session"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_statistics()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state in [GameState.SETTINGS, GameState.STATISTICS]:
                            self.game_state = GameState.MENU
                        elif self.game_state == GameState.PLAYING:
                            self.game_state = GameState.PAUSED

                    elif self.game_state == GameState.MENU:
                        if event.key == pygame.K_SPACE:
                            self.game_state = GameState.PLAYING
                            self.reset_game()
                        elif event.key == pygame.K_s:
                            self.game_state = GameState.SETTINGS
                        elif event.key == pygame.K_t:
                            self.game_state = GameState.STATISTICS
                        elif event.key == pygame.K_F11:  # F11 для переключения полноэкранного режима
                            self.fullscreen = not self.fullscreen
                            if self.fullscreen:
                                self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
                            else:
                                self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)

                        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            difficulties = list(self.difficulty_levels.keys())
                            current_index = difficulties.index(self.current_difficulty)
                            if event.key == pygame.K_LEFT:
                                self.current_difficulty = difficulties[(current_index - 1) % len(difficulties)]
                            else:
                                self.current_difficulty = difficulties[(current_index + 1) % len(difficulties)]
                            self.reset_game()

                    elif self.game_state == GameState.SETTINGS:
                        if event.key == pygame.K_1:
                            self.settings["sound_enabled"] = not self.settings["sound_enabled"]
                        elif event.key == pygame.K_2:
                            self.settings["particles_enabled"] = not self.settings["particles_enabled"]
                        elif event.key == pygame.K_3:
                            self.settings["dark_mode"] = not self.settings["dark_mode"]
                        elif event.key == pygame.K_4:
                            self.settings["letter_effects"] = not self.settings["letter_effects"]

                    elif self.game_state == GameState.PLAYING:
                        self.total_keys_pressed += 1
                        key_pressed = event.unicode.upper()
                        matched = False
                        
                        for letter in self.letters[:]:
                            if letter['char'] == key_pressed:
                                self.letters.remove(letter)
                                self.score += (1 + self.combo)
                                self.combo += 1
                                self.max_combo = max(self.max_combo, self.combo)
                                self.correct_keys_pressed += 1
                                matched = True
                                
                                # Эффекты при правильном нажатии
                                if self.settings["particles_enabled"]:
                                    self.create_particle_effect(letter['x'], letter['y'], self.GREEN)
                                
                                # Звуковой эффект
                                if self.settings["sound_enabled"] and self.sounds["correct"]:
                                    self.sounds["correct"].play()
                                
                                # Повышение уровня
                                if self.score > self.level * 100:
                                    self.level += 1
                                    if self.settings["sound_enabled"] and self.sounds["level_up"]:
                                        self.sounds["level_up"].play()
                                break
                        
                        if not matched:
                            self.combo = 0
                            if self.settings["sound_enabled"] and self.sounds["wrong"]:
                                self.sounds["wrong"].play()
                            if self.settings["particles_enabled"]:
                                self.create_particle_effect(
                                    self.WIDTH//2, 
                                    self.HEIGHT//2, 
                                    self.RED
                                )
                        
                        self.accuracy = round(
                            (self.correct_keys_pressed / max(1, self.total_keys_pressed)) * 100
                        )
                        
                    elif self.game_state == GameState.GAME_OVER:
                        if event.key == pygame.K_r:
                            self.update_statistics()
                            self.game_state = GameState.MENU
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False

                    elif self.game_state == GameState.PAUSED:
                        if event.key == pygame.K_SPACE:
                            self.game_state = GameState.PLAYING
                        elif event.key == pygame.K_q:
                            self.game_state = GameState.MENU

            if self.game_state == GameState.PLAYING:
                # Создание новых букв
                self.spawn_timer += 1
                spawn_rate = self.difficulty_levels[self.current_difficulty]["spawn_rate"]
                if self.spawn_timer >= 60 // (spawn_rate + self.level * 0.2):
                    self.spawn_letter()
                    self.spawn_timer = 0

                # Обновление позиций букв
                for letter in self.letters[:]:
                    letter['y'] += letter['speed']
                    # Изменение цвета буквы при приближении к низу экрана
                    danger_zone = self.HEIGHT * 0.7
                    if letter['y'] > danger_zone:
                        danger_factor = (letter['y'] - danger_zone) / (self.HEIGHT - danger_zone)
                        letter['color'] = (
                            int(255 * danger_factor),  # R
                            int(255 * (1 - danger_factor)),  # G
                            0  # B
                        )
                    
                    if letter['y'] > self.HEIGHT:
                        self.letters.remove(letter)
                        self.missed += 1
                        self.combo = 0
                        
                        if self.settings["particles_enabled"]:
                            self.create_particle_effect(
                                letter['x'],
                                self.HEIGHT,
                                self.RED
                            )
                        
                        if self.missed >= 10:
                            self.game_state = GameState.GAME_OVER
                            self.update_statistics()

                # Обновление частиц
                if self.settings["particles_enabled"]:
                    self.update_particles()

            # Отрисовка
            if self.game_state == GameState.MENU:
                self.draw_menu()
            elif self.game_state == GameState.PLAYING:
                self.draw_game()
            elif self.game_state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.game_state == GameState.SETTINGS:
                self.draw_settings()
            elif self.game_state == GameState.STATISTICS:
                self.draw_statistics()
            elif self.game_state == GameState.PAUSED:
                self.draw_pause_screen()

            pygame.display.update()
            clock.tick(60)

        pygame.quit()

    def draw_game_over(self):
        self.window.fill(self.BLACK)
        
        texts = [
            ("ИГРА ОКОНЧЕНА!", self.RED, self.main_font),
            (f"Финальный счёт: {self.score}", self.WHITE, self.menu_font),
            (f"Максимальное комбо: {self.max_combo}", self.BLUE, self.menu_font),
            (f"Точность: {self.accuracy}%", self.GREEN, self.menu_font),
            ("R - Начать заново", self.WHITE, self.menu_font),
            ("Q - Выйти", self.WHITE, self.menu_font)
        ]

        for i, (text, color, font) in enumerate(texts):
            surface = font.render(text, True, color)
            self.window.blit(
                surface,
                (self.WIDTH//2 - surface.get_width()//2, 150 + i * 70)
            )

    def draw_pause_screen(self):
        # Полупрозрачное затемнение
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.window.blit(overlay, (0, 0))

        texts = [
            ("ПАУЗА", self.WHITE, self.main_font),
            ("ПРОБЕЛ - Продолжить", self.WHITE, self.menu_font),
            ("Q - Выйти в меню", self.WHITE, self.menu_font)
        ]

        for i, (text, color, font) in enumerate(texts):
            surface = font.render(text, True, color)
            self.window.blit(
                surface,
                (self.WIDTH//2 - surface.get_width()//2, 200 + i * 70)
            )

if __name__ == "__main__":
    game = KeyboardTrainer()
    game.run()
