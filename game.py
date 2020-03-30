# Basic arcade shooter

# Imports
import arcade
import random
import timeit

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Space Shooter"
SCALING = 1.0


class FlyingSprite(arcade.Sprite):
    pass


class FriendlyMissile(FlyingSprite):
    pass


class SpaceShooter(arcade.Window):
    """Space Shooter side scroller game.

    Player starts on the left, enemies appear on the right
    Player can move anywhere, but not off screen
    Player can shoot missiles at enemies
    Enemies fly to the left at variable speed
    Collisions end the game
    """

    def __init__(self, width, height, title):
        """Initialize the game."""
        super().__init__(width, height, title)

        self.background = None

    def setup(self):
        """Get the game ready to play."""
        # Set the background color
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Set up the empty sprite lists
        self.missile_list = arcade.SpriteList()
        self.enemies_list = arcade.SpriteList()
        self.clouds_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        # Set up the player
        self.player = arcade.Sprite('images/jet.png', SCALING)
        self.player.center_y = self.height / 2
        self.player.left = 10
        self.all_sprites.append(self.player)

        # Spawn a new enemy every 0.25 seconds
        arcade.schedule(self.add_enemy, 0.25)

        # Spawn a new cload every second
        arcade.schedule(self.add_cloud, 1.0)

        # Load sounds
        # Sound sources: Jon Fincher
        self.collision_sound = arcade.load_sound('sounds/Collision.wav')
        self.move_up_sound = arcade.load_sound('sounds/Rising_putter.wav')
        self.move_down_sound = arcade.load_sound('sounds/Falling_putter.wav')

        # Start the background music
        self.play_background_music()
        arcade.schedule(self.play_background_music, 15.0)

        # Initialize variables
        self.started = False
        self.paused = False
        self.game_over = False
        self.diagnostics = False

        self.kill_count = 0
        self.processing_time = 0
        self.draw_time = 0
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None

    def play_background_music(self, delta_time: float = 0.0):
        if self.background:
            self.background.stop()

        # Load background music
        # Sound source: http://ccmixter.org/files/Apoxode/59262
        # License: https://creativecommons.org/licenses/by/3.0/
        self.background = arcade.Sound("sounds/Apoxode_-_Electric_1.wav",
                                       streaming=True)
        self.background.play(0.5)

    def add_enemy(self, delta_time: float):
        """Add a new enemy to the screen.

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """
        # Don't add enemies if paused, not started or gameover
        if self.paused or not self.started or self.game_over:
            return

        # First, create the new enemy sprite
        enemy = FlyingSprite("images/missile.png", SCALING)

        # Set its position to a random height and off screen right
        enemy.left = random.randint(self.width, self.width + 80)
        enemy.top = random.randint(10, self.height - 10)

        # Set its speed to a random speed heading left
        enemy.velocity = (random.randint(-250, -90), 0)

        # Add it to the enemies list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

    def add_cloud(self, delta_time: float):
        """Add a new cloud to the screen.

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """
        # Don't add clouds if paused, not started or gameover
        if self.paused or not self.started or self.game_over:
            return

        # First, create the new cloud sprite
        cloud = FlyingSprite("images/cloud.png", SCALING)

        # Set its position to a random height and off screen right
        cloud.left = random.randint(self.width, self.width + 80)
        cloud.top = random.randint(10, self.height - 10)

        # Set its speed to a random speed heading left
        cloud.velocity = (random.randint(-75, -20), 0)

        # Add it to the clouds list
        self.clouds_list.append(cloud)
        self.all_sprites.append(cloud)

    def add_missile(self):
        """Add a new enemy to the screen.

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """
        # Don't add missiles if paused, not started or gameover
        if self.paused or not self.started or self.game_over:
            return

        # First, create the new missile sprite
        missile = FriendlyMissile("images/missile_friendly.png", SCALING)

        # Set its position to center right of player
        missile.right = self.player.right
        missile.center_y = self.player.center_y

        # Set its speed to a random speed heading left
        missile.velocity = (200, 0)

        # Add it to the missile list
        self.missile_list.append(missile)
        self.all_sprites.append(missile)

    def on_key_press(self, symbol, modifiers):
        """Handle user keyboard input.

        Q: Quit the game
        P: Pause/Unpause the game
        D: Show diagnostics
        ENTER: Start or Restart game
        I/J/K/L: Move up, Left, Down, Right
        Arrows: Move up, Left, Down, Right
        Space: Shoot missiles

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if symbol == arcade.key.ENTER:
            self.started = True
            # Call setup() when restarting game
            if self.game_over:
                self.game_over = False
                self.setup()

        if symbol == arcade.key.Q:
            # Quit immediately
            arcade.close_window()

        if symbol == arcade.key.P:
            self.paused = not self.paused

        if symbol == arcade.key.D:
            self.diagnostics = not self.diagnostics

        if symbol == arcade.key.SPACE:
            self.add_missile()

        if symbol == arcade.key.I or symbol == arcade.key.UP:
            self.player.change_y = 250
            arcade.play_sound(self.move_up_sound)

        if symbol == arcade.key.K or symbol == arcade.key.DOWN:
            self.player.change_y = -250
            arcade.play_sound(self.move_down_sound)

        if symbol == arcade.key.J or symbol == arcade.key.LEFT:
            self.player.change_x = -250

        if symbol == arcade.key.L or symbol == arcade.key.RIGHT:
            self.player.change_x = 250

    def on_key_release(self, symbol: int, modifiers: int):
        """Undo movement vectors when movement keys are released.

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if (
            symbol == arcade.key.I
            or symbol == arcade.key.K
            or symbol == arcade.key.UP
            or symbol == arcade.key.DOWN
        ):
            self.player.change_y = 0

        if (
            symbol == arcade.key.J
            or symbol == arcade.key.L
            or symbol == arcade.key.LEFT
            or symbol == arcade.key.RIGHT
        ):
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        """Update the positions and statuses of all game objects.

        If paused, do nothing

        Arguments:
            delta_time {float} -- Time since the last update
        """
        # If paused, game not started or game over, don't update anything
        if self.paused or not self.started or self.game_over:
            return

        # Did you hit anything? If so, end the game
        if self.player.collides_with_list(self.enemies_list):
            arcade.play_sound(self.collision_sound)
            self.game_over = True

        # Update all sprite positions
        for sprite in self.all_sprites:
            sprite.center_x = sprite.center_x + sprite.change_x * delta_time
            sprite.center_y = sprite.center_y + sprite.change_y * delta_time
            # Remove cloud or enemy sprite once it leaves screen on left
            if sprite.right < 0:
                sprite.remove_from_sprite_lists()

            if isinstance(sprite, FriendlyMissile):
                if sprite.left > self.width:
                    sprite.remove_from_sprite_lists()

        # Remove missile and enemy on collision
        for missile in self.missile_list:
            collisions = missile.collides_with_list(self.enemies_list)
            if collisions:
                self.kill_count = self.kill_count + 1
                missile.remove_from_sprite_lists()
            for enemy in collisions:
                enemy.remove_from_sprite_lists()

        # Keep the player on the screen
        if self.player.top > self.height:
            self.player.top = self.height
        if self.player.right > self.width:
            self.player.right = self.width
        if self.player.bottom < 0:
            self.player.bottom = 0
        if self.player.left < 0:
            self.player.left = 0

    def on_draw(self):
        """Draw all game objects."""
        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        if self.frame_count % 60 == 0:
            if self.fps_start_timer is not None:
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = 60 / total_time
            self.fps_start_timer = timeit.default_timer()
        self.frame_count += 1

        # Needs to be called before drawing
        arcade.start_render()

        # Draw all sprites
        self.clouds_list.draw()
        self.enemies_list.draw()
        self.missile_list.draw()
        self.player.draw()

        # Display number of enemies destroyed
        output = f'Enemies Destroyed: {self.kill_count}'
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 30, arcade.color.BLACK, 16)

        if not self.started:
            output = f'Press ENTER to start'
            arcade.draw_text(output,
                             SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2,
                             arcade.color.BLACK,
                             40,
                             anchor_x='center')

        if self.paused:
            output = f'PAUSED'
            arcade.draw_text(output,
                             SCREEN_WIDTH / 2,
                             (SCREEN_HEIGHT / 2),
                             arcade.color.BLACK,
                             40,
                             anchor_x='center')

        if self.game_over:
            output = f'GAME OVER'
            arcade.draw_text(output,
                             SCREEN_WIDTH / 2,
                             (SCREEN_HEIGHT / 2) + 45,
                             arcade.color.BLACK,
                             40,
                             anchor_x='center')
            output = f'Press ENTER to restart'
            arcade.draw_text(output,
                             SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2,
                             arcade.color.BLACK,
                             40,
                             anchor_x='center')

        # Show diagnostics (Processing Time, Draw Time, FPS, and Sprite Counts)
        # Press 'D' during play to show
        if self.diagnostics:
            output = f"Processing time: {self.processing_time:.3f}"
            arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.BLACK, 16)

            output = f"Drawing time: {self.draw_time:.3f}"
            arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.BLACK, 16)

            if self.fps is not None:
                output = f"FPS: {self.fps:.0f}"
                arcade.draw_text(output, 20, SCREEN_HEIGHT - 80, arcade.color.BLACK, 16)

            output = f'Enemy Count: {len(self.enemies_list)}'
            arcade.draw_text(output, 20, SCREEN_HEIGHT - 100, arcade.color.BLACK, 16)

            output = f'Cloud Count: {len(self.clouds_list)}'
            arcade.draw_text(output, 20, SCREEN_HEIGHT - 120, arcade.color.BLACK, 16)

            output = f'Missile Count: {len(self.missile_list)}'
            arcade.draw_text(output, 20, SCREEN_HEIGHT - 140, arcade.color.BLACK, 16)

        self.draw_time = timeit.default_timer() - draw_start_time


if __name__ == "__main__":
    space_game = SpaceShooter(
        int(SCREEN_WIDTH * SCALING), int(SCREEN_HEIGHT * SCALING), SCREEN_TITLE
    )
    space_game.setup()
    arcade.run()
