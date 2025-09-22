#
# Created by Arsen Djurdjev on 12-Nov-24.
#



import pygame
import random
import os
import requests

# Constants for colors and dimensions
CELL_SIZE = 20
GRID_SIZE = 30
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
LIGHT_BROWN = (222, 184, 135)
BROWN_DARKEN_STEP = 10
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT_SIZE = 20
RESTART_DELAY = 3000
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 20
BUTTON_NORDEUS_COLOR = (231, 72, 42)

BUTTON_COLOR = BUTTON_NORDEUS_COLOR

BUTTON_NORDEUS_HOVER_COLOR = (231, 152, 42)

BUTTON_HOVER_COLOR = BUTTON_NORDEUS_HOVER_COLOR

#Class which will be used to create the clouds
class Cloud:
    def __init__(self, image, x, y, speed, shadow):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.shadow = shadow 

    def update(self):
        self.x += self.speed
        if self.x > WINDOW_SIZE:
            self.x = -self.image.get_width()  

    def draw(self, screen):
        screen.blit(self.shadow, (self.x + 10, self.y + 8))  # Slight offset for shadow
        screen.blit(self.image, (self.x, self.y))

    def render(self, screen):
        self.draw(screen)



#Class which will be used to create the buttons
class Button:
    def __init__(self, x, y, width, height, color, text, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color if hover_color else color
        self.text = text
        self.font = pygame.font.Font(None, FONT_SIZE)

    def render(self, screen):
        current_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        text_surf = self.font.render(self.text, True, WHITE)
        screen.blit(text_surf, (
            self.rect.x + (self.rect.width - text_surf.get_width()) // 2,
            self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        ))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
    

#Class which will be used to create the cells of the grid
class Cell:
    def __init__(self, x, y, height, water_sprite, land_sprite):
        self.x = x
        self.y = y
        self.height = height
        self.is_land = height > 0
        self.visited = False
        self.water_sprite = water_sprite
        self.land_sprite = land_sprite
        self.darken_cache = {}

    def get_darker_sprite(self, factor):
        if factor not in self.darken_cache:
            darkened_sprite = self.darken_sprite(self.land_sprite if self.is_land else self.water_sprite, factor)
            self.darken_cache[factor] = darkened_sprite
        return self.darken_cache[factor]

    def darken_sprite(self, sprite, factor):
        darkened_sprite = sprite.copy()
        darkened_sprite.lock()  # Lock the surface for pixel access
        width, height = darkened_sprite.get_size()

        for x in range(width):
            for y in range(height):
                color = darkened_sprite.get_at((x, y))
                r, g, b, a = color
                # Darken the color by the factor, ensuring the values remain within valid range
                r = max(0, int(r * factor))
                g = max(0, int(g * factor))
                b = max(0, int(b * factor))
                darkened_sprite.set_at((x, y), (r, g, b, a))

        darkened_sprite.unlock()  # Unlock the surface
        return darkened_sprite

    def render(self, screen):
        darkening_factor = max(0.5, 1 - self.height * 0.05)  # Adjust the factor for desired effect
        sprite = self.land_sprite if self.is_land else self.water_sprite
        darkened_sprite = self.get_darker_sprite(darkening_factor)
        screen.blit(darkened_sprite, (self.x * CELL_SIZE, self.y * CELL_SIZE))

#Class which will be used to create the islands
class Island:
    def __init__(self, cells):
        self.cells = cells

    def average_height(self):
        total_height = sum(cell.height for cell in self.cells)
        return total_height / len(self.cells) if self.cells else 0

    def render(self, screen, highlight=False):
        color = GREEN if highlight else LIGHT_BROWN
        for cell in self.cells:
            pygame.draw.rect(screen, color, (cell.x * CELL_SIZE, cell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

#Class which will be used to create the grid map of the game
class GridMap:
    def __init__(self, size=GRID_SIZE, difficulty='easy', water_sprite=None, land_sprite=None, predefined_matrix=None):
        self.size = size
        self.difficulty = difficulty
        self.grid = []

        if predefined_matrix:
            # Use the predefined matrix to set up grid
                self.grid = [[Cell(x, y, predefined_matrix[x][y], water_sprite, land_sprite) for y in range(size)] for x in range(size)]
                self.islands = []
                self.find_islands()
        else:
            # Otherwise, generate grid with random land heights
            self.grid = [[Cell(x, y, 0, water_sprite, land_sprite) for y in range(size)] for x in range(size)]
            self.islands = []
            self._generate_land_with_priority()

    def _generate_land_with_priority(self):
        # Only used if no predefined matrix is given
        for x in range(self.size):
            for y in range(self.size):
                height = random.choices([0, random.randint(1, 5)], weights=[0.8, 0.2])[0]
                self.grid[x][y].height = height
                self.grid[x][y].is_land = height > 0

        self.find_islands()

        # Identify the maximum island(s)
        max_island = max(self.islands, key=lambda island: len(island.cells), default=None)
        max_height_islands = [island for island in self.islands if island.average_height() == max_island.average_height()]

        # For 'easy' difficulty, set the max height island's cells to 10
        if self.difficulty == 'easy' and max_island:
            for cell in max_island.cells:
                cell.height = 10
        else:
            # In 'hard' mode, make one of the max height islands slightly taller
            if len(max_height_islands) > 1:
                island_to_increase = random.choice(max_height_islands)
                for cell in island_to_increase.cells:
                    cell.height = random.randint(7, 10)  # Assign a slightly larger height range

            # Set other islands' heights (for non-max islands, randomize a bit)
            for island in self.islands:
                if island != max_island:
                    for cell in island.cells:
                        if len(island.cells) > 1:
                            cell.height = min(9, cell.height + random.randint(3, 5))
                        elif cell.height > 0:
                            cell.height = min(cell.height, random.randint(1, 7))

    def find_islands(self):
        for row in self.grid:
            for cell in row:
                cell.visited = False

        for x in range(self.size):
            for y in range(self.size):
                cell = self.grid[x][y]
                if cell.is_land and not cell.visited:
                    island_cells = self._get_connected_land_cells(cell)
                    self.islands.append(Island(island_cells))

    def _get_connected_land_cells(self, start_cell):
        stack = [start_cell]
        connected_cells = []

        while stack:
            cell = stack.pop()
            if cell.visited:
                continue
            cell.visited = True
            connected_cells.append(cell)

            for neighbor in self._get_neighbors(cell):
                if neighbor.is_land and not neighbor.visited:
                    stack.append(neighbor)

        return connected_cells

    def _get_neighbors(self, cell):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []

        for dx, dy in directions:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append(self.grid[nx][ny])

        return neighbors

    def render(self, screen):
        for row in self.grid:
            for cell in row:
                cell.render(screen)


#Class which will be used to create the game itself
class Game:
    def __init__(self, map_size=GRID_SIZE, difficulty='easy', water_sprite=None, land_sprite=None, predefined_matrix=None):
        self.predifined_matrix = predefined_matrix
        self.map = GridMap(map_size, difficulty, water_sprite, land_sprite, predefined_matrix)
        self.map.find_islands()
        self.target_island = max(self.map.islands, key=lambda island: island.average_height())
        self.attempts = 3
        self.correct_guess = False
        self.message = "Click on an island to guess!"
        self.hover_message = ""
        self.cheats_enabled = False
        self.game_over_time = None

    def guess_island(self, cell):
        if self.attempts == 0 or self.correct_guess:
            return

        guessed_island = next((island for island in self.map.islands if cell in island.cells), None)

        if guessed_island == self.target_island:
            self.correct_guess = True
            self.message = "Congratulations! You found the highest island! New game in 3 seconds"

            # play sound located in sound folder where script is
            script_dir = os.path.dirname(__file__)

            sound = pygame.mixer.Sound(os.path.join(script_dir, 'sound', 'correct.ogg'))
            sound.set_volume(0.3)
            sound.play()



            self.game_over_time = pygame.time.get_ticks()
        else:
            self.attempts -= 1

            # play sound located in sound folder where script is
            script_dir = os.path.dirname(__file__)

            sound = pygame.mixer.Sound(os.path.join(script_dir, 'sound', 'wrong.ogg'))
            sound.set_volume(0.1)
            sound.play()

            self.message = f"Wrong guess! Attempts left: {self.attempts}" if self.attempts > 0 else "Game over! Restarting in 3 seconds."
            if self.attempts == 0:
                self.game_over_time = pygame.time.get_ticks()

    def update_hover_message(self, cell):
        if self.cheats_enabled:
            island = next((island for island in self.map.islands if cell in island.cells), None)
            self.hover_message = f"Island Average Height: {island.average_height():.2f}" if island else ""
        else:
            self.hover_message = ""

    def restart_game(self, difficulty):
        self.__init__(self.map.size, difficulty)

    def render(self, screen, font):
        self.map.render(screen)
        if self.correct_guess:
            self.target_island.render(screen, highlight=True)

        message_text = font.render(self.message, True, (0,0,0))
        screen.blit(message_text, (10, WINDOW_SIZE - 30))

        if self.hover_message:
            hover_text = font.render(self.hover_message, True, (0,0,0))
            screen.blit(hover_text, (10, WINDOW_SIZE - 60))


class PauseMenu:
    def __init__(self, screen, font, app):
        self.screen = screen
        self.font = font
        self.app = app  # Reference to GameApp for music control and main app flow
        self.is_paused = False
        # Conditionally add resume button only if a game exists
        self.resume_button = Button(WINDOW_SIZE // 2 - BUTTON_WIDTH // 2, 150, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "Resume", BUTTON_HOVER_COLOR)
        self.new_game_button = Button(WINDOW_SIZE // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "New Game", BUTTON_HOVER_COLOR)
        self.cheats_button = Button(WINDOW_SIZE // 2 - BUTTON_WIDTH // 2, 250, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "Cheats", BUTTON_HOVER_COLOR)
        self.music_button = Button(WINDOW_SIZE // 2 - BUTTON_WIDTH // 2, 300, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "Music", BUTTON_HOVER_COLOR)
        self.exit_button = Button(WINDOW_SIZE // 2 - BUTTON_WIDTH // 2, 350, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "Exit", BUTTON_HOVER_COLOR)


        # Volume slider
        self.volume_slider_rect = pygame.Rect(WINDOW_SIZE // 2 - 75, 400, 150, 20)
        self.volume_level = 0.15  # Initial volume level
        self.min_volume = 0  # Minimum volume level
        self.max_volume = 0.3  # Maximum volume level
        self.is_cheats_enabled = False  # Initialize cheats as off
        self.is_music_on = True

    def render(self):
        if self.is_paused:
            self.screen.fill((0, 0, 0, 150))  
            if self.app.game is not None:
                self.resume_button.render(self.screen)
            self.new_game_button.render(self.screen)
            if self.app.game is not None:
                self.cheats_button.render(self.screen)
            self.music_button.render(self.screen)
            self.exit_button.render(self.screen)
            pygame.draw.rect(self.screen, (200, 200, 200), self.volume_slider_rect)
            pygame.draw.rect(self.screen, (231, 72, 42), pygame.Rect(
                self.volume_slider_rect.x,
                self.volume_slider_rect.y,
                (self.volume_level - self.min_volume) / (self.max_volume - self.min_volume) * self.volume_slider_rect.width,
                self.volume_slider_rect.height
            ))
            # Display volume percentage text
            volume_percent = int((self.volume_level - self.min_volume) / (self.max_volume - self.min_volume) * 100)
            volume_text = self.font.render(f"Volume: {volume_percent}%", True, WHITE)
            self.screen.blit(volume_text, (self.volume_slider_rect.x + 5, self.volume_slider_rect.y - 25))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.resume_button.is_clicked(event):
                self.is_paused = False
            elif self.new_game_button.is_clicked(event):
                self.start_new_game()
            elif self.cheats_button.is_clicked(event):
                self.is_cheats_enabled = not self.is_cheats_enabled
                self.app.game.cheats_enabled = self.is_cheats_enabled
                self.is_paused = False

            elif self.music_button.is_clicked(event):
                self.toggle_music()
            elif self.exit_button.is_clicked(event):
                pygame.quit()
                quit()
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            if event.pos[0] in range(self.volume_slider_rect.x, self.volume_slider_rect.x + self.volume_slider_rect.width) and \
               event.pos[1] in range(self.volume_slider_rect.y, self.volume_slider_rect.y + self.volume_slider_rect.height):
                self.volume_level = self.min_volume + (event.pos[0] - self.volume_slider_rect.x) / self.volume_slider_rect.width * (self.max_volume - self.min_volume)
                pygame.mixer.music.set_volume(self.volume_level)

    def start_new_game(self):
        # Show difficulty options when starting a new game
        difficulty = self.show_difficulty_selection()
        if difficulty:
            self.app.difficulty = difficulty
            self.app.start_game(difficulty)
            self.is_paused = False
            self.toggle_music()


    def show_difficulty_selection(self):
        easy_button = Button(WINDOW_SIZE // 4 - BUTTON_WIDTH // 2, WINDOW_SIZE // 2, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "Easy", BUTTON_HOVER_COLOR)
        hard_button = Button(3 * WINDOW_SIZE // 4 - BUTTON_WIDTH // 2, WINDOW_SIZE // 2, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, "Hard", BUTTON_HOVER_COLOR)
        nordeus_button = Button(WINDOW_SIZE // 2 - BUTTON_WIDTH // 2, WINDOW_SIZE // 2 + 50, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_NORDEUS_COLOR, "Nordeus", BUTTON_NORDEUS_HOVER_COLOR)

        
        
        
        while True:
            self.screen.fill(WHITE)
            easy_button.render(self.screen)
            hard_button.render(self.screen)
            nordeus_button.render(self.screen)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif easy_button.is_clicked(event):
                    return 'easy'
                elif hard_button.is_clicked(event):
                    return 'hard'
                elif nordeus_button.is_clicked(event):
                    return 'nordeus'

    def toggle_music(self):
        self.app.current_music = (self.app.current_music + 1) % len(self.app.music_tracks)
        pygame.mixer.music.load(self.app.music_tracks[self.app.current_music])
        pygame.mixer.music.play(-1, 0.0)

#Class which will be used to create the game app
class GameApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Island Guessing Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.running = True
        self.load_sprites()
        self.pause_menu = PauseMenu(self.screen, self.font, self)
        self.pause_menu.is_paused = True  # Show pause menu on startup
        self.load_music()
        self.game = None  # Initialize game to None so resume and cheats are hidden initially

        print("GameApp initialized successfully.")

 

    
    def load_music(self):
        script_dir = os.path.dirname(__file__)

        # Load music tracks
        self.music_tracks = [
            os.path.join(script_dir, 'music', 'track1.ogg'),
            os.path.join(script_dir, 'music', 'track2.ogg'),
            os.path.join(script_dir, 'music', 'track3.ogg')
        ]
        self.current_music = random.randint(0, len(self.music_tracks) - 1)  # Randomly select a music track
        pygame.mixer.music.load(self.music_tracks[self.current_music])
        pygame.mixer.music.play(-1, 0.0)  # Loop music indefinitely
        pygame.mixer.music.set_volume(self.pause_menu.volume_level)



    def load_sprites(self):
        try:
            script_dir = os.path.dirname(__file__)

            # Load water and land sprites
            self.water_sprite = pygame.image.load(os.path.join(script_dir, 'texture', 'Tex_Water_img.png')).convert_alpha()
            self.land_sprite = pygame.image.load(os.path.join(script_dir, 'texture', 'Tex_SmoothDirt_img.png')).convert_alpha()

            # Resize the water and land sprites to match the cell size
            self.water_sprite = pygame.transform.scale(self.water_sprite, (CELL_SIZE, CELL_SIZE))
            self.land_sprite = pygame.transform.scale(self.land_sprite, (CELL_SIZE, CELL_SIZE))

            # Load three different cloud textures
            cloud_texture_1 = pygame.image.load(os.path.join(script_dir, 'texture', 'Cloud1.png')).convert_alpha()
            cloud_texture_2 = pygame.image.load(os.path.join(script_dir, 'texture', 'Cloud2.png')).convert_alpha()
            cloud_texture_3 = pygame.image.load(os.path.join(script_dir, 'texture', 'Cloud3.png')).convert_alpha()

            # Resize clouds to fit the game (optional)
            cloud_width = 64
            cloud_height = 32
            cloud_texture_1 = pygame.transform.scale(cloud_texture_1, (cloud_width, cloud_height))
            cloud_texture_2 = pygame.transform.scale(cloud_texture_2, (cloud_width, cloud_height))
            cloud_texture_3 = pygame.transform.scale(cloud_texture_3, (cloud_width, cloud_height))

            # Store the cloud textures
            self.cloud_images = [cloud_texture_1, cloud_texture_2, cloud_texture_3]

            # Create cloud shadows with the same shape as the clouds
            self.cloud_shadows = []
            for cloud in self.cloud_images:
                # Create a shadow by darkening the cloud
                shadow = cloud.copy()
                shadow.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)  # Darken the cloud with transparency
                self.cloud_shadows.append(shadow)

            # Create clouds with random speeds and positions
            self.clouds = []  # Clear previous clouds before recreating
            for i in range(3):  # Create 3 clouds
                # Randomly flip the cloud image to make it look different
                cloud_image = self.cloud_images[i]
                if random.choice([True, False]):
                    cloud_image = pygame.transform.flip(cloud_image, True, False)  # Randomly flip horizontally

                # Get the corresponding shadow for this cloud
                cloud_shadow = self.cloud_shadows[i]

                cloud = Cloud(
                    cloud_image,  # Use transformed cloud image
                    random.randint(0, WINDOW_SIZE),
                    random.randint(20, 500),
                    random.randint(1, 2),  # Random speed for the cloud
                    cloud_shadow  # Set cloud shadow
                )
                self.clouds.append(cloud)

            print("Sprites loaded successfully.")
        except pygame.error as e:
            print(f"Error loading images: {e}")
            pygame.quit()
    
    @staticmethod
    def fetch_matrix(url):
        # Send GET request to retrieve the matrix text
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request was unsuccessful

        # Split the response text into rows and convert it to a 2D list of integers
        matrix = [list(map(int, row.split())) for row in response.text.strip().splitlines()]

        # Ensure the matrix is 30x30
        if len(matrix) == 30 and all(len(row) == 30 for row in matrix):
            return matrix
        else:
            raise ValueError("The matrix is not 30x30.")       



    def start_game(self, difficulty):
        self.difficulty = difficulty
        if difficulty == 'nordeus':
            try:
                matrix = self.fetch_matrix("https://jobfair.nordeus.com/jf24-fullstack-challenge/test")
                self.game = Game(difficulty=difficulty, water_sprite=self.water_sprite, land_sprite=self.land_sprite, predefined_matrix=matrix)
                self.pause_menu.is_paused = False  
            except Exception as e:
                print(f"An error occurred: {e}")
                self.game = Game(difficulty='easy', water_sprite=self.water_sprite, land_sprite=self.land_sprite)
                self.pause_menu.is_paused = False  
            
        else:
            self.game = Game(difficulty=self.difficulty, water_sprite=self.water_sprite, land_sprite=self.land_sprite)
            self.pause_menu.is_paused = False 
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.pause_menu.is_paused = not self.pause_menu.is_paused
            elif self.pause_menu.is_paused:
                self.pause_menu.handle_events(event)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()  
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and self.game.attempts > 0:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    cell_x, cell_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                    cell = self.game.map.grid[cell_x][cell_y]
                    self.game.guess_island(cell)

    def update(self):
        if self.game:
            if self.game.game_over_time and pygame.time.get_ticks() - self.game.game_over_time > RESTART_DELAY:
                if self.difficulty == 'nordeus':
                    matrix = self.fetch_matrix("https://jobfair.nordeus.com/jf24-fullstack-challenge/test")
                    self.game = Game(difficulty=self.difficulty, water_sprite=self.water_sprite, land_sprite=self.land_sprite, predefined_matrix=matrix)
                else:
                    self.game = Game(difficulty=self.difficulty, water_sprite=self.water_sprite, land_sprite=self.land_sprite)  # Restart game after delay

            # Update cloud positions
            for cloud in self.clouds:
                cloud.update()  # Ensure clouds are moving

            mouse_x, mouse_y = pygame.mouse.get_pos()
            cell_x, cell_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            cell = self.game.map.grid[cell_x][cell_y]
            self.game.update_hover_message(cell)

    def render(self):
        self.screen.fill(WHITE)
        if self.pause_menu.is_paused:
            self.pause_menu.render()
        else:
            self.game.render(self.screen, self.font)
            for cloud in self.clouds:
                cloud.render(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    app = GameApp()
    app.run()