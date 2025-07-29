import pygame
import os
import sys
import math
from pathlib import Path

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60  # Increased for smoother animation

class EasingFunctions:
    """Utility class for easing functions to create smooth animations."""
    
    @staticmethod
    def ease_in_out(t):
        """Smooth ease-in-out function."""
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def ease_out(t):
        """Ease-out function for natural deceleration."""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in(t):
        """Ease-in function for natural acceleration."""
        return t * t

class AssetLoader:
    """Enhanced asset loader with better error handling and caching."""
    
    def __init__(self):
        self.assets_path = Path("assets")
        self.images_path = self.assets_path / "images"
        self.sounds_path = self.assets_path / "sounds"
        self.loaded_images = {}
        self.loaded_sounds = {}
        
    def load_image(self, filename):
        """Load an image file with enhanced error handling."""
        if filename in self.loaded_images:
            return self.loaded_images[filename]
            
        try:
            image_path = self.images_path / filename
            if image_path.exists():
                image = pygame.image.load(str(image_path))
                self.loaded_images[filename] = image
                return image
            else:
                print(f"Warning: Image file {filename} not found")
                return self.create_placeholder_image(50, 50, (255, 0, 0))
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            return self.create_placeholder_image(50, 50, (255, 0, 0))
            
    def load_sound(self, filename):
        """Load a sound file with enhanced error handling."""
        if filename in self.loaded_sounds:
            return self.loaded_sounds[filename]
            
        try:
            sound_path = self.sounds_path / filename
            if sound_path.exists():
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(0.3)
                self.loaded_sounds[filename] = sound
                return sound
            else:
                print(f"Warning: Sound file {filename} not found")
                return None
        except Exception as e:
            print(f"Error loading sound {filename}: {e}")
            return None
            
    def create_placeholder_image(self, width, height, color):
        """Create a placeholder image when asset is not found."""
        surface = pygame.Surface((width, height))
        surface.fill(color)
        return surface

class FadeEffect:
    """Handles fade-in and fade-out effects."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fade_surface = pygame.Surface((screen_width, screen_height))
        self.fade_surface.fill((0, 0, 0))
        self.fade_alpha = 255
        self.fade_in_duration = 60  # frames
        self.fade_out_duration = 60  # frames
        self.fade_in_complete = False
        self.fade_out_started = False
        
    def update_fade_in(self, frame_count):
        """Update fade-in effect."""
        if not self.fade_in_complete and frame_count < self.fade_in_duration:
            progress = frame_count / self.fade_in_duration
            self.fade_alpha = int(255 * (1 - EasingFunctions.ease_in_out(progress)))
            if frame_count >= self.fade_in_duration - 1:
                self.fade_in_complete = True
                
    def update_fade_out(self, frame_count, total_frames):
        """Update fade-out effect."""
        if not self.fade_out_started and frame_count >= total_frames - self.fade_out_duration:
            self.fade_out_started = True
            
        if self.fade_out_started:
            fade_out_progress = (frame_count - (total_frames - self.fade_out_duration)) / self.fade_out_duration
            fade_out_progress = max(0, min(1, fade_out_progress))
            self.fade_alpha = int(255 * EasingFunctions.ease_in_out(fade_out_progress))
            
    def draw(self, screen):
        """Draw the fade effect."""
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))

class SceneManager:
    """Enhanced scene manager with better background handling and parallax effects."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Animated Scene Demo - SIT771 Task 1.4")
        self.clock = pygame.time.Clock()
        self.fps = FPS
        self.running = True
        self.asset_loader = AssetLoader()
        self.fade_effect = FadeEffect(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setup_background()
        
    def setup_background(self):
        """Setup the background with parallax layers."""
        try:
            # Load background images
            sky_bg = self.asset_loader.load_image("sky_background.png")
            mountain_bg = self.asset_loader.load_image("mountain.png")
            
            # Scale images to fit screen
            sky_bg = pygame.transform.scale(sky_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            mountain_bg = pygame.transform.scale(mountain_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Create composite background
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.blit(sky_bg, (0, 0))
            self.background.blit(mountain_bg, (0, 0))
            
        except Exception as e:
            print(f"Error loading background: {e}")
            # Fallback to simple background
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((135, 206, 235))  # Sky blue
            
            # Add mountain silhouette
            mountain_points = [(0, SCREEN_HEIGHT), (200, 400), (400, 500), 
                              (600, 350), (800, 450), (1000, 300), 
                              (1200, 400), (SCREEN_WIDTH, 500), (SCREEN_WIDTH, SCREEN_HEIGHT)]
            pygame.draw.polygon(self.background, (139, 69, 19), mountain_points)

class Character:
    """Enhanced character class with smooth movement and better animation."""
    
    def __init__(self, x, y, asset_loader):
        self.start_x = x
        self.target_x = SCREEN_WIDTH + 100  # Walk off-screen
        self.x = x
        self.y = y
        self.base_y = y  # Store base Y for jump calculations
        self.asset_loader = asset_loader
        self.rect = pygame.Rect(x, y, 60, 96)
        self.animation_frames = []
        self.current_frame = 0
        self.frame_delay = 8
        self.frame_counter = 0
        self.visible = False
        self.walking = False
        self.jumping = False
        self.movement_started = False
        self.movement_duration = 300  # Extended for longer walk
        self.movement_progress = 0
        self.jump_started = False
        self.jump_progress = 0
        self.jump_duration = 60  # Jump duration in frames
        self.jump_height = 50  # Maximum jump height
        self.jump_trigger_x = SCREEN_WIDTH * 0.6  # Trigger jump at 60% of screen
        self.load_animations()
        
    def load_animations(self):
        """Load character animation frames from assets."""
        # Load walking animation frames
        walk_frames = [
            "dani_walk01.png",
            "dani_walk02.png", 
            "dani_walk03.png",
            "dani_walk04.png",
            "dani_walk05.png"
        ]
        
        for frame_file in walk_frames:
            frame = self.asset_loader.load_image(frame_file)
            # Scale frame to reasonable size
            frame = pygame.transform.scale(frame, (60, 96))
            self.animation_frames.append(frame)
            
        # Load jump frame
        self.jump_frame = self.asset_loader.load_image("dani_jump01.png")
        self.jump_frame = pygame.transform.scale(self.jump_frame, (60, 96))
        
    def update(self, frame_count):
        """Update character animation and movement."""
        if self.visible:
            # Update animation
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.frame_counter = 0
                if self.walking:
                    self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                elif self.jumping:
                    self.current_frame = 0  # Stay on jump frame
                    
            # Update movement
            if self.walking and not self.movement_started:
                self.movement_started = True
                self.movement_progress = 0
                
            if self.movement_started and self.movement_progress < 1.0:
                self.movement_progress += 1.0 / self.movement_duration
                self.movement_progress = min(1.0, self.movement_progress)
                
                # Use easing function for smooth movement
                eased_progress = EasingFunctions.ease_in_out(self.movement_progress)
                self.x = self.start_x + (self.target_x - self.start_x) * eased_progress
                
                # Check if we should trigger jump
                if not self.jump_started and self.x >= self.jump_trigger_x:
                    self.jump_started = True
                    self.jumping = True
                    self.jump_progress = 0
                    # Play jump sound when jump starts
                    if hasattr(self, 'sound_effects'):
                        self.sound_effects.play('jump', frame_count)
                
                # Handle jump animation
                if self.jump_started and self.jump_progress < 1.0:
                    self.jump_progress += 1.0 / self.jump_duration
                    self.jump_progress = min(1.0, self.jump_progress)
                    
                    # Create a parabolic jump motion
                    jump_ease = EasingFunctions.ease_out(self.jump_progress)
                    jump_height = self.jump_height * (4 * jump_ease * (1 - jump_ease))  # Parabolic curve
                    self.y = self.base_y - jump_height
                
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                    
    def draw(self, screen):
        """Draw the character."""
        if self.visible:
            if self.jumping:
                screen.blit(self.jump_frame, self.rect)
            else:
                screen.blit(self.animation_frames[self.current_frame], self.rect)

class AnimatedSprite:
    """Enhanced animated sprite with better timing and effects."""
    
    def __init__(self, x, y, frame_files, asset_loader, scale=(40, 40)):
        self.x = x
        self.y = y
        self.asset_loader = asset_loader
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 4
        self.frame_counter = 0
        self.visible = False
        self.animation_complete = False
        self.scale = scale
        self.alpha = 255
        self.fade_in_duration = 30
        self.fade_in_progress = 0
        self.load_frames(frame_files)
        self.rect = self.frames[0].get_rect() if self.frames else pygame.Rect(x, y, scale[0], scale[1])
        self.rect.x = x
        self.rect.y = y
        
    def load_frames(self, frame_files):
        """Load animation frames from file list."""
        for frame_file in frame_files:
            frame = self.asset_loader.load_image(frame_file)
            frame = pygame.transform.scale(frame, self.scale)
            self.frames.append(frame)
            
    def update(self):
        """Update animation with fade-in effect."""
        if self.visible:
            # Handle fade-in effect
            if self.fade_in_progress < 1.0:
                self.fade_in_progress += 1.0 / self.fade_in_duration
                self.alpha = int(255 * EasingFunctions.ease_in_out(self.fade_in_progress))
            
            if not self.animation_complete:
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.frame_counter = 0
                    self.current_frame += 1
                    if self.current_frame >= len(self.frames):
                        self.animation_complete = True
                        self.current_frame = len(self.frames) - 1
                    
    def draw(self, screen):
        """Draw the sprite with alpha blending."""
        if self.visible and self.frames:
            frame = self.frames[self.current_frame].copy()
            if self.alpha < 255:
                frame.set_alpha(self.alpha)
            screen.blit(frame, self.rect)

class Cloud:
    """Enhanced cloud class with parallax movement."""
    
    def __init__(self, x, y, asset_loader, speed=0.5, layer=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.layer = layer  # Different layers for parallax effect
        self.asset_loader = asset_loader
        self.cloud_frames = []
        self.current_frame = 0
        self.frame_delay = 15
        self.frame_counter = 0
        self.load_cloud_frames()
        self.rect = pygame.Rect(x, y, 120, 72)
        self.visible = True
        
    def load_cloud_frames(self):
        """Load cloud animation frames."""
        for i in range(1, 21):  # cloud01_idle.png to cloud20_idle.png
            filename = f"cloud{i:02d}_idle.png"
            frame = self.asset_loader.load_image(filename)
            frame = pygame.transform.scale(frame, (120, 72))
            self.cloud_frames.append(frame)
            
    def update(self):
        """Update cloud position and animation with parallax effect."""
        # Parallax movement based on layer
        parallax_speed = self.speed * (1 + self.layer * 0.3)
        self.x += parallax_speed
        self.rect.x = self.x
        if self.x > SCREEN_WIDTH:
            self.x = -120
            
        # Update animation
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.cloud_frames)
            
    def draw(self, screen):
        """Draw the cloud."""
        if self.visible and self.cloud_frames:
            screen.blit(self.cloud_frames[self.current_frame], self.rect)

class SoundEffect:
    """Enhanced sound effect manager with better timing."""
    
    def __init__(self, asset_loader):
        self.asset_loader = asset_loader
        self.sounds = {}
        self.sound_timings = {}
        self.load_sounds()
        
    def load_sounds(self):
        """Load sound effects from assets."""
        sound_files = {
            'jump': 'player_jump_groan01.ogg',
            'start': 'game_start.ogg'
        }
        
        for sound_name, filename in sound_files.items():
            sound = self.asset_loader.load_sound(filename)
            if sound:
                self.sounds[sound_name] = sound
                
    def play(self, sound_name, frame_count):
        """Play a sound effect with timing control."""
        if sound_name in self.sounds and sound_name not in self.sound_timings:
            self.sounds[sound_name].play()
            self.sound_timings[sound_name] = frame_count

class AnimatedScene:
    """Enhanced main scene class with better timing and effects."""
    
    def __init__(self):
        self.scene_manager = SceneManager()
        self.sound_effects = SoundEffect(self.scene_manager.asset_loader)
        self.setup_scene_objects()
        
    def setup_scene_objects(self):
        """Setup all scene objects with enhanced positioning."""
        # Create character with smooth movement
        self.character = Character(-100, 500, self.scene_manager.asset_loader)
        self.character.sound_effects = self.sound_effects  # Pass sound effects to character
        
        # Create mushroom with growth animation
        mushroom_growth_frames = [f"mushroom_growing{i:02d}.png" for i in range(1, 9)]
        self.mushroom = AnimatedSprite(600, 450, mushroom_growth_frames, 
                                     self.scene_manager.asset_loader, (80, 80))
        
        # Create explosion animation
        explosion_frames = [f"mushroom_bursting{i:02d}.png" for i in range(1, 14)]
        self.explosion = AnimatedSprite(600, 450, explosion_frames, 
                                      self.scene_manager.asset_loader, (100, 100))
        
        # Create satellite activation
        satellite_frames = [f"satellite_dish_signal_activating{i:02d}.png" for i in range(1, 4)]
        self.satellite = AnimatedSprite(1000, 200, satellite_frames, 
                                      self.scene_manager.asset_loader, (120, 120))
        
        # Create clouds with different layers for parallax effect
        self.clouds = [
            Cloud(100, 100, self.scene_manager.asset_loader, 0.3, 1),
            Cloud(400, 150, self.scene_manager.asset_loader, 0.5, 2),
            Cloud(700, 80, self.scene_manager.asset_loader, 0.7, 3)
        ]
        
        # Scene timing
        self.frame_count = 0
        self.total_frames = 900  # Extended for smoother experience
        
    def update_scene(self):
        """Update scene based on frame count with enhanced timing."""
        frame = self.frame_count
        
        # Scene initialization with fade-in (0-60 frames)
        if 0 <= frame < 60:
            self.scene_manager.fade_effect.update_fade_in(frame)
            
        # Character entry (60-360 frames) - Extended for continuous walk
        elif 60 <= frame < 360:
            if frame == 60:
                self.character.visible = True
                self.character.walking = True
                
        # Mushroom growth (360-480 frames)
        elif 360 <= frame < 480:
            if frame == 360:
                self.mushroom.visible = True
                
        # Mushroom explosion (480-600 frames)
        elif 480 <= frame < 600:
            if frame == 480:
                self.mushroom.visible = False
                self.explosion.visible = True
                self.sound_effects.play('jump', frame)
                
        # Satellite activation (600-720 frames)
        elif 600 <= frame < 720:
            if frame == 600:
                self.satellite.visible = True
                
        # Scene conclusion (720-840 frames)
        elif 720 <= frame < 840:
            if frame == 720:
                self.sound_effects.play('start', frame)
                
        # Fade out (840-900 frames)
        elif 840 <= frame < 900:
            self.scene_manager.fade_effect.update_fade_out(frame, self.total_frames)
            
        # End scene
        elif frame >= 900:
            self.scene_manager.running = False
            
    def run(self):
        """Enhanced main game loop with better timing."""
        while self.scene_manager.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.scene_manager.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.scene_manager.running = False
                        
            # Update scene
            self.update_scene()
            
            # Update objects
            self.character.update(self.frame_count)
            self.mushroom.update()
            self.satellite.update()
            self.explosion.update()
            for cloud in self.clouds:
                cloud.update()
                
            # Draw everything
            self.scene_manager.screen.blit(self.scene_manager.background, (0, 0))
            
            # Draw clouds (background layer)
            for cloud in self.clouds:
                cloud.draw(self.scene_manager.screen)
                
            # Draw scene objects (foreground layer)
            self.character.draw(self.scene_manager.screen)
            self.mushroom.draw(self.scene_manager.screen)
            self.satellite.draw(self.scene_manager.screen)
            self.explosion.draw(self.scene_manager.screen)
            
            # Draw fade effect
            self.scene_manager.fade_effect.draw(self.scene_manager.screen)
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.scene_manager.clock.tick(self.scene_manager.fps)
            self.frame_count += 1
            
        pygame.quit()

if __name__ == "__main__":
    scene = AnimatedScene()
    scene.run() 