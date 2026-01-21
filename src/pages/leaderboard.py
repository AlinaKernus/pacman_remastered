import pygame
import sys
import os
import requests
import random
import time
import copy
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config
from src.utils.music_manager import music_manager

from src.utils.path_helper import get_base_dir
BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "Jersey_10", "Jersey10-Regular.ttf")

class Leaderboard(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.deco1 = Widget(110, 91, image_cache_manager.deco, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.deco2 = Widget(1610, 91, image_cache_manager.deco, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.deco1, self.deco2,
            self.back_but
        ]
        
        # Leaderboard data
        self.leaderboard_data = []
        self.loading = False
        self.error_message = None
        self.last_update_time = 0
        self.update_interval = 5000  # Update every 5 seconds
        
        # Scrolling
        self.scroll_offset = 0
        self.max_visible_rows = 10  # Maximum rows visible at once
        
        # Current player data
        self.current_player_rank = None  # Will be fetched from API
        self.current_player_username = "Player123"  # Will get from settings
        self.current_player_score = None  # Will be fetched from API
        self.player_data_loaded = False
        
        # API URL (default to localhost, can be configured)
        self.api_url = "http://localhost:3000"
        
        # Font
        self.font_path = FONT_PATH if os.path.isfile(FONT_PATH) else None
        
        # Sorting test buttons and results
        self.sort_times = {
            'insertion': None,
            'heap': None,
            'radix': None
        }
        self.sort_button_rects = {}  # Will store button rectangles
    
    def _init_font(self, size=36):
        """Initialize font"""
        try:
            if self.font_path:
                return pygame.font.Font(self.font_path, size)
            else:
                return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.SysFont('arial', size)
    
    def _draw_current_player_row(self, surface, window_size, scale_w, scale_h, text_scale):
        """Draw fixed row with current player's information at the bottom"""
        font_entry = self._init_font(int(32 * text_scale))
        color_yellow = (255, 255, 0)
        color_white = (255, 255, 255)
        color_gray = (150, 150, 150)
        color_highlight = (100, 150, 255)  # Highlight color for current player
        
        # Position at the bottom with some margin (2 rows higher)
        row_height = int(50 * scale_h)
        row_y = int(window_size[1] - row_height - int(100 * scale_h) - 2 * row_height)
        row_width = int(1120 * scale_w)
        row_x = int(400 * scale_w)
        
        # Draw background with highlight
        row_bg = pygame.Rect(row_x, row_y, row_width, row_height)
        pygame.draw.rect(surface, (20, 40, 60), row_bg)  # Dark blue background
        pygame.draw.rect(surface, color_highlight, row_bg, 3)  # Highlight border
        
        # Label
        label_text = font_entry.render("Your Position:", True, color_highlight)
        label_x = row_x + int(20 * scale_w)
        label_y = row_y + (row_height - label_text.get_height()) // 2
        surface.blit(label_text, (label_x, label_y))
        
        # Rank
        rank_x = row_x + int(200 * scale_w)
        if self.current_player_rank is not None:
            rank_text = font_entry.render(f"#{self.current_player_rank}", True, color_white)
        else:
            rank_text = font_entry.render("-", True, color_gray)
        surface.blit(rank_text, (rank_x, label_y))
        
        # Username
        name_x = row_x + int(350 * scale_w)
        name_text = font_entry.render(str(self.current_player_username)[:20], True, color_white)
        surface.blit(name_text, (name_x, label_y))
        
        # Score
        score_x = row_x + int(800 * scale_w)
        if self.current_player_score is not None:
            score_text = font_entry.render(str(self.current_player_score), True, color_yellow)
        else:
            score_text = font_entry.render("-", True, color_gray)
        surface.blit(score_text, (score_x, label_y))
    
    def insertion_sort(self, arr, key_func):
        """Insertion Sort algorithm (descending order for leaderboard)"""
        arr = copy.deepcopy(arr)
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and key_func(arr[j]) < key_func(key):  # Descending: higher score first
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr
    
    def heap_sort(self, arr, key_func):
        """Heap Sort algorithm (descending order for leaderboard)"""
        arr = copy.deepcopy(arr)
        
        def heapify(arr, n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < n and key_func(arr[left]) > key_func(arr[largest]):
                largest = left
            if right < n and key_func(arr[right]) > key_func(arr[largest]):
                largest = right
            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                heapify(arr, n, largest)
        
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, n, i)
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            heapify(arr, i, 0)
        # Reverse for descending order (highest score first)
        return list(reversed(arr))
    
    def radix_sort(self, arr, key_func):
        """Radix Sort algorithm (for integers, descending order for leaderboard)"""
        arr = copy.deepcopy(arr)
        if not arr:
            return arr
        
        # Get max value to determine number of digits
        max_val = max(key_func(item) for item in arr)
        exp = 1
        
        while max_val // exp > 0:
            # Counting sort for each digit
            count = [0] * 10
            output = [None] * len(arr)
            
            # Count occurrences
            for item in arr:
                index = (key_func(item) // exp) % 10
                count[index] += 1
            
            # Change count to position
            for i in range(1, 10):
                count[i] += count[i - 1]
            
            # Build output array
            for i in range(len(arr) - 1, -1, -1):
                index = (key_func(arr[i]) // exp) % 10
                output[count[index] - 1] = arr[i]
                count[index] -= 1
            
            arr = output
            exp *= 10
        
        # Reverse for descending order (highest score first)
        return list(reversed(arr))
    
    def test_sort_algorithm(self, sort_type):
        """Test a sorting algorithm on shuffled leaderboard data"""
        if not self.leaderboard_data:
            return None
        
        # Create a copy and shuffle
        test_data = copy.deepcopy(self.leaderboard_data)
        random.shuffle(test_data)
        
        # Key function to extract score for sorting
        def get_score(item):
            if isinstance(item, dict):
                return item.get('score', 0)
            return 0
        
        # Measure time
        start_time = time.perf_counter()
        
        if sort_type == 'insertion':
            sorted_data = self.insertion_sort(test_data, get_score)
        elif sort_type == 'heap':
            sorted_data = self.heap_sort(test_data, get_score)
        elif sort_type == 'radix':
            sorted_data = self.radix_sort(test_data, get_score)
        else:
            return None
        
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return elapsed_time
    
    def _draw_sort_buttons(self, surface):
        """Draw sorting test buttons on the right side"""
        window_size = surface.get_size()
        scale_w = window_size[0] / Config.BASE_WIDTH
        scale_h = window_size[1] / Config.BASE_HEIGHT
        text_scale = min(scale_w, scale_h)
        
        font_button = self._init_font(int(24 * text_scale))
        font_result = self._init_font(int(20 * text_scale))
        
        color_yellow = (255, 255, 0)
        color_white = (255, 255, 255)
        color_gray = (150, 150, 150)
        color_button = (60, 60, 60)
        color_button_hover = (80, 80, 80)
        color_border = (255, 255, 0)
        
        # Button dimensions
        button_width = int(200 * scale_w)
        button_height = int(40 * scale_h)
        button_spacing = int(10 * scale_h)
        
        # Position on the right side (100 pixels more to the left)
        right_margin = int(150 * scale_w)  # 50 + 100 = 150
        start_x = int(window_size[0] - button_width - right_margin)
        start_y = int(250 * scale_h)
        
        # Button labels
        buttons = [
            ('insertion', 'INSERTION SORT'),
            ('heap', 'HEAP SORT'),
            ('radix', 'RADIX SORT')
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (sort_type, label) in enumerate(buttons):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(start_x, button_y, button_width, button_height)
            self.sort_button_rects[sort_type] = button_rect
            
            # Check if mouse is over button
            is_hover = button_rect.collidepoint(mouse_pos)
            bg_color = color_button_hover if is_hover else color_button
            
            # Draw button
            pygame.draw.rect(surface, bg_color, button_rect)
            pygame.draw.rect(surface, color_border, button_rect, 2)
            
            # Draw text
            text_surface = font_button.render(label, True, color_yellow)
            text_x = start_x + (button_width - text_surface.get_width()) // 2
            text_y = button_y + (button_height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
        
        # Draw results below buttons
        results_y = start_y + len(buttons) * (button_height + button_spacing) + int(20 * scale_h)
        
        for i, (sort_type, label) in enumerate(buttons):
            result_y = results_y + i * int(25 * scale_h)
            time_value = self.sort_times.get(sort_type)
            
            if time_value is not None:
                result_text = f"{label}: {time_value:.4f} ms"
                color = color_yellow
            else:
                result_text = f"{label}: -"
                color = color_gray
            
            text_surface = font_result.render(result_text, True, color)
            surface.blit(text_surface, (start_x, result_y))
    
    def fetch_leaderboard(self):
        """Fetch leaderboard data from API"""
        try:
            url = f"{self.api_url}/leaderboard"
            print(f"[Leaderboard] Fetching from {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[Leaderboard] Received data: {data}")
                
                # Expected format: list of {username, score} or {rank, username, score}
                if isinstance(data, list):
                    self.leaderboard_data = data
                elif isinstance(data, dict) and 'leaderboard' in data:
                    self.leaderboard_data = data['leaderboard']
                else:
                    self.leaderboard_data = []
                    print(f"[Leaderboard] Unexpected data format: {data}")
                
                self.error_message = None
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('message', f'Error {response.status_code}')
                self.error_message = error_msg
                print(f"[Leaderboard] Error {response.status_code}: {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.error_message = f"Connection error: {str(e)}"
            print(f"[Leaderboard] Request exception: {str(e)}")
            return False
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            print(f"[Leaderboard] Exception: {str(e)}")
            return False
    
    def fetch_player_data(self, username):
        """Fetch current player's rank and score from API"""
        try:
            url = f"{self.api_url}/leaderboard/player/{username}"
            print(f"[Leaderboard] Fetching player data from {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[Leaderboard] Player data received: {data}")
                
                # Expected format: {rank, username, score} or similar
                if isinstance(data, dict):
                    self.current_player_rank = data.get('rank', None)
                    self.current_player_score = data.get('score', None)
                    self.player_data_loaded = True
                    return True
                else:
                    print(f"[Leaderboard] Unexpected player data format: {data}")
                    self.current_player_rank = None
                    self.current_player_score = None
                    self.player_data_loaded = True
                    return False
            elif response.status_code == 404:
                # Player not found - set to None to show "-"
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('message', 'Player not found')
                print(f"[Leaderboard] Player not found (404): {error_msg}")
                self.current_player_rank = None
                self.current_player_score = None
                self.player_data_loaded = True
                return True  # Not an error, just player not in leaderboard
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('message', f'Error {response.status_code}')
                print(f"[Leaderboard] Error {response.status_code} fetching player data: {error_msg}")
                # Don't set error_message here, just log it
                return False
        except requests.exceptions.RequestException as e:
            print(f"[Leaderboard] Request exception fetching player data: {str(e)}")
            return False
        except Exception as e:
            print(f"[Leaderboard] Exception fetching player data: {str(e)}")
            return False
    
    def _draw_leaderboard(self, surface):
        """Draw leaderboard table"""
        window_size = surface.get_size()
        scale_w = window_size[0] / Config.BASE_WIDTH
        scale_h = window_size[1] / Config.BASE_HEIGHT
        text_scale = min(scale_w, scale_h)
        
        # Fonts
        font_title = self._init_font(int(64 * text_scale))
        font_header = self._init_font(int(36 * text_scale))
        font_entry = self._init_font(int(32 * text_scale))
        font_error = self._init_font(int(28 * text_scale))
        
        # Colors
        color_yellow = (255, 255, 0)
        color_white = (255, 255, 255)
        color_gray = (150, 150, 150)
        color_error = (255, 0, 0)
        
        # Title
        title = font_title.render("Global Leaderboard", True, color_yellow)
        title_x = int(640 * scale_w) - title.get_width() // 2
        title_y = int(150 * scale_h)
        surface.blit(title, (title_x, title_y))
        
        # Table position
        table_start_x = int(400 * scale_w)
        table_start_y = int(250 * scale_h)
        table_width = int(1120 * scale_w)
        row_height = int(50 * scale_h)
        
        # Headers
        header_bg = pygame.Rect(table_start_x, table_start_y, table_width, row_height)
        pygame.draw.rect(surface, (40, 40, 40), header_bg)
        pygame.draw.rect(surface, color_yellow, header_bg, 2)
        
        rank_header = font_header.render("Rank", True, color_yellow)
        name_header = font_header.render("Username", True, color_yellow)
        score_header = font_header.render("Score", True, color_yellow)
        
        rank_x = table_start_x + int(20 * scale_w)
        name_x = table_start_x + int(200 * scale_w)
        score_x = table_start_x + int(800 * scale_w)
        
        header_y = table_start_y + (row_height - rank_header.get_height()) // 2
        surface.blit(rank_header, (rank_x, header_y))
        surface.blit(name_header, (name_x, header_y))
        surface.blit(score_header, (score_x, header_y))
        
        # Error message
        if self.error_message:
            error_text = font_error.render(self.error_message, True, color_error)
            error_x = int(640 * scale_w) - error_text.get_width() // 2
            error_y = table_start_y + int(100 * scale_h)
            surface.blit(error_text, (error_x, error_y))
            return
        
        # Loading message
        if self.loading:
            loading_text = font_entry.render("Loading...", True, color_gray)
            loading_x = int(640 * scale_w) - loading_text.get_width() // 2
            loading_y = table_start_y + int(100 * scale_h)
            surface.blit(loading_text, (loading_x, loading_y))
            return
        
        # No data message
        if not self.leaderboard_data:
            no_data_text = font_entry.render("No leaderboard data available", True, color_gray)
            no_data_x = int(640 * scale_w) - no_data_text.get_width() // 2
            no_data_y = table_start_y + int(100 * scale_h)
            surface.blit(no_data_text, (no_data_x, no_data_y))
            return
        
        # Leaderboard entries with scrolling
        total_entries = len(self.leaderboard_data)
        max_scroll = max(0, total_entries - self.max_visible_rows)
        self.scroll_offset = min(self.scroll_offset, max_scroll)
        self.scroll_offset = max(0, self.scroll_offset)
        
        visible_start = self.scroll_offset
        visible_end = min(visible_start + self.max_visible_rows, total_entries)
        
        for i in range(visible_start, visible_end):
            entry = self.leaderboard_data[i]
            display_index = i - visible_start
            row_y = table_start_y + row_height + (display_index * row_height)
            
            # Alternate row background
            if i % 2 == 0:
                row_bg = pygame.Rect(table_start_x, row_y, table_width, row_height)
                pygame.draw.rect(surface, (30, 30, 30), row_bg)
            
            # Get data
            rank = entry.get('rank', i + 1) if isinstance(entry, dict) else i + 1
            username = entry.get('username', 'Unknown') if isinstance(entry, dict) else str(entry.get('username', 'Unknown'))
            score = entry.get('score', 0) if isinstance(entry, dict) else entry.get('score', 0)
            
            # Render text
            rank_text = font_entry.render(f"#{rank}", True, color_white)
            name_text = font_entry.render(str(username)[:20], True, color_white)  # Limit username length
            score_text = font_entry.render(str(score), True, color_yellow)
            
            # Position text
            rank_y = row_y + (row_height - rank_text.get_height()) // 2
            surface.blit(rank_text, (rank_x, rank_y))
            surface.blit(name_text, (name_x, rank_y))
            surface.blit(score_text, (score_x, rank_y))
        
        # Draw scroll indicator if needed
        if total_entries > self.max_visible_rows:
            scroll_indicator = font_entry.render(f"Scroll: {self.scroll_offset + 1}-{visible_end} of {total_entries}", True, color_gray)
            indicator_x = table_start_x + table_width - scroll_indicator.get_width() - int(20 * scale_w)
            indicator_y = table_start_y - int(30 * scale_h)
            surface.blit(scroll_indicator, (indicator_x, indicator_y))
        
        # Draw fixed current player row at the bottom (always show, even if no data)
        self._draw_current_player_row(surface, window_size, scale_w, scale_h, text_scale)

    def run(self, surface):
        clock = pygame.time.Clock()
        self.on_resize(surface.get_size())
        
        # Load current player username from settings
        from src.utils.settings_manager import settings_manager
        self.current_player_username = settings_manager.get_setting("username", "Player123")
        
        # Initial fetch
        self.loading = True
        self.fetch_leaderboard()
        # Fetch player data if username is available
        if self.current_player_username:
            self.fetch_player_data(self.current_player_username)
        self.loading = False
        self.last_update_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            
            # Auto-refresh every update_interval
            if current_time - self.last_update_time > self.update_interval:
                self.loading = True
                self.fetch_leaderboard()
                # Refresh player data too
                if self.current_player_username:
                    self.fetch_player_data(self.current_player_username)
                self.loading = False
                self.last_update_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h),
                                                     pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
                    self.on_resize(surface.get_size())
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if sorting button was clicked
                    if event.button == 1:  # Left mouse button
                        mouse_pos = event.pos
                        for sort_type, button_rect in self.sort_button_rects.items():
                            if button_rect.collidepoint(mouse_pos):
                                # Test the sorting algorithm
                                elapsed_time = self.test_sort_algorithm(sort_type)
                                if elapsed_time is not None:
                                    self.sort_times[sort_type] = elapsed_time
                                break
                elif event.type == pygame.MOUSEWHEEL:
                    # Scroll leaderboard
                    if len(self.leaderboard_data) > self.max_visible_rows:
                        scroll_amount = event.y * 3  # Scroll 3 rows at a time
                        self.scroll_offset = max(0, min(self.scroll_offset - scroll_amount, 
                                                       len(self.leaderboard_data) - self.max_visible_rows))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Manual refresh with R key
                        self.loading = True
                        self.fetch_leaderboard()
                        # Refresh player data too
                        if self.current_player_username:
                            self.fetch_player_data(self.current_player_username)
                        self.loading = False
                        self.last_update_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_UP:
                        # Scroll up
                        if len(self.leaderboard_data) > self.max_visible_rows:
                            self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                        # Scroll down
                        if len(self.leaderboard_data) > self.max_visible_rows:
                            self.scroll_offset = min(self.scroll_offset + 1, 
                                                     len(self.leaderboard_data) - self.max_visible_rows)

            self.draw(surface)
            self.deco1.draw(surface)
            self.deco2.draw(surface)
            
            # Draw leaderboard
            self._draw_leaderboard(surface)
            
            # Draw sorting test buttons
            self._draw_sort_buttons(surface)

            if self.back_but.draw(surface):
                return "menu"
            
            # Отрисовка и обработка иконки звука
            if self.sound_icon.draw(surface):
                music_manager.toggle_all_sounds()

            pygame.display.flip()
            clock.tick(60)
