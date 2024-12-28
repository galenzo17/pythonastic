import pygame
import sys
import random

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

BIRD_WIDTH = 34
BIRD_HEIGHT = 24
BIRD_FRAMES = 3    # Number of animation frames for the bird

PIPE_WIDTH = 52
PIPE_HEIGHT = 320
PIPE_GAP = 150

# Particle effect configuration
PARTICLE_COUNT = 15
PARTICLE_SIZE = 5
PARTICLE_SPEED = 1

# Initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()

# Load images (placeholder surfaces if you don't have real images)
# Replace these with your own images
bird_frames = []
for i in range(BIRD_FRAMES):
    # Here we create a colored surface for the bird's frame
    surface = pygame.Surface((BIRD_WIDTH, BIRD_HEIGHT), pygame.SRCALPHA)
    surface.fill((255 - i*50, 200 - i*30, 0))  # Change color slightly
    bird_frames.append(surface)

pipe_top_image = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT))
pipe_top_image.fill((0, 200, 0))
pipe_bottom_image = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT))
pipe_bottom_image.fill((0, 180, 0))

# Load a background image or just create a surface
bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_surface.fill((135, 206, 235))  # Sky color

# Bird class
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame_index = 0
        self.frame_counter = 0
        self.velocity = 0
        self.gravity = 0.4
        self.jump_strength = -7
        self.rect = bird_frames[0].get_rect(center=(x, y))
        
        # Particle attributes
        self.particles = []

    def update(self):
        # Animate bird
        self.frame_counter += 1
        if self.frame_counter >= 5:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % BIRD_FRAMES

        # Apply gravity
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

        # Generate particles
        self.generate_particles()

        # Update particle positions
        self.update_particles()

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, surface):
        # Draw bird
        current_frame = bird_frames[self.frame_index]
        surface.blit(current_frame, self.rect)

        # Draw bird's particles
        for px, py, vx, vy, size in self.particles:
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), size)

    def generate_particles(self):
        # Add new particle behind the bird
        if len(self.particles) < PARTICLE_COUNT:
            px = self.x - 10
            py = self.y
            vx = random.uniform(-1, -0.5) * PARTICLE_SPEED
            vy = random.uniform(-0.5, 0.5) * PARTICLE_SPEED
            size = random.randint(2, PARTICLE_SIZE)
            self.particles.append([px, py, vx, vy, size])

    def update_particles(self):
        # Move and reduce size of particles
        for i in range(len(self.particles) - 1, -1, -1):
            self.particles[i][0] += self.particles[i][2]
            self.particles[i][1] += self.particles[i][3]
            self.particles[i][4] -= 0.03  # Slowly shrink the particle

            # Remove particles that are too small or offscreen
            if self.particles[i][4] <= 0 or self.particles[i][0] < 0:
                self.particles.pop(i)

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(100, 400)  # Vertical position of the gap
        self.top_rect = pipe_top_image.get_rect(midbottom=(x, self.gap_y - PIPE_GAP // 2))
        self.bottom_rect = pipe_bottom_image.get_rect(midtop=(x, self.gap_y + PIPE_GAP // 2))
        self.speed = 3

    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        surface.blit(pipe_top_image, self.top_rect)
        surface.blit(pipe_bottom_image, self.bottom_rect)

    def off_screen(self):
        return self.x < -PIPE_WIDTH

    def collision(self, bird_rect):
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bottom_rect)

# Main function
def main():
    try:
        bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        pipes = []
        spawn_timer = 0
        score = 0
        font = pygame.font.SysFont("Arial", 30, bold=True)

        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    # This helps for touchscreen if it registers as MOUSEBUTTONDOWN
                    bird.jump()

            # Update bird
            bird.update()

            # Spawn pipes
            spawn_timer += 1
            if spawn_timer >= 90:  # Adjust pipe spawn frequency
                spawn_timer = 0
                pipes.append(Pipe(SCREEN_WIDTH))

            # Update pipes
            for pipe in pipes:
                pipe.update()

            # Check collisions or pass
            for pipe in pipes:
                # Bird collision
                if pipe.collision(bird.rect):
                    # Reset game or break
                    running = False
                # Check if the bird passed the pipe (scoring)
                if pipe.x + PIPE_WIDTH < bird.x and not getattr(pipe, 'passed', False):
                    pipe.passed = True
                    score += 1

            # Remove off-screen pipes
            pipes = [pipe for pipe in pipes if not pipe.off_screen()]

            # Check ground or ceiling collision
            if bird.rect.top <= 0 or bird.rect.bottom >= SCREEN_HEIGHT:
                running = False

            # Draw everything
            screen.blit(bg_surface, (0, 0))
            for pipe in pipes:
                pipe.draw(screen)
            bird.draw(screen)

            # Show score
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            pygame.display.update()

        pygame.quit()
        sys.exit()
    except Exception as e:
        print("An error occurred:", e)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()