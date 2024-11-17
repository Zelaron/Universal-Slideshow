import os
import sys
import random
import pygame
import time
import subprocess

# User configuration - Change these values as needed

# Set IMAGE_DIRECTORY to override automatic directory detection
# Leave as None to use system's default Pictures folder
IMAGE_DIRECTORY = None

# Example paths - uncomment and modify one of these if you want to set a specific directory:
# IMAGE_DIRECTORY = r'C:\Users\Username\Pictures'    # Windows
# IMAGE_DIRECTORY = '/Users/Username/Pictures'       # macOS
# IMAGE_DIRECTORY = '/home/Username/Pictures'        # Linux

# Slideshow configuration:
# - Set to 0 to disable automatic advancement
# - Set to a positive number for seconds between auto-advance
# You can always use:
# - Left/Right arrow keys to navigate between images manually
# - ESC to quit
SHUFFLE_TIME = 5

def get_pictures_dir():
   # If user specified a custom directory, use that
   if IMAGE_DIRECTORY and os.path.exists(IMAGE_DIRECTORY):
       return IMAGE_DIRECTORY

   if os.name == 'nt':  # Windows
       try:
           import winreg
           with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
               return winreg.QueryValueEx(key, 'My Pictures')[0]
       except:
           pass

   # macOS specific path
   elif sys.platform == 'darwin':
       mac_pictures = os.path.expanduser('~/Pictures')
       if os.path.exists(mac_pictures):
           return mac_pictures

   # Linux/Unix systems
   elif sys.platform.startswith('linux'):
       try:
           # Try to get the localized Pictures directory using xdg-user-dir
           result = subprocess.run(['xdg-user-dir', 'PICTURES'], 
                                 capture_output=True, 
                                 text=True)
           pictures_dir = result.stdout.strip()
           if os.path.exists(pictures_dir):
               return pictures_dir
       except FileNotFoundError:
           pass

   # Fallback methods for all platforms
   home = os.path.expanduser('~')
   common_names = [
       'Pictures', 'Bilder', 'Images', 'Imágenes', 'Obrazy', 'Изображения',
       'My Pictures', 'Mina bilder', 'Mes images', 'Meine Bilder'
   ]
   for name in common_names:
       path = os.path.join(home, name)
       if os.path.exists(path):
           return path

   return os.path.join(home, 'Pictures')

def main():
   # Get the appropriate pictures directory
   image_directory = get_pictures_dir()
   print(f"\nImage Slideshow")
   print(f"==============")
   print(f"Using directory: {image_directory}")

   if not os.path.exists(image_directory):
       print(f"Error: Directory {image_directory} does not exist!")
       sys.exit(1)

   pygame.init()
   screen_info = pygame.display.Info()
   screen_width, screen_height = screen_info.current_w, screen_info.current_h
   screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
   pygame.display.set_caption("Image Slideshow")

   supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pcx', '.tga', '.tif', '.tiff', '.lbm', '.pbm', '.pgm', '.ppm', '.xpm')
   images = [
       os.path.join(image_directory, f)
       for f in os.listdir(image_directory)
       if f.lower().endswith(supported_extensions)
   ]

   if not images:
       print(f"No supported images found in {image_directory}")
       print(f"Supported formats: {', '.join(supported_extensions)}")
       pygame.quit()
       sys.exit(1)

   print(f"\nFound {len(images)} images")
   print(f"Auto-advance is {'disabled' if SHUFFLE_TIME == 0 else f'set to {SHUFFLE_TIME} seconds'}")
   print("\nControls:")
   print("- Right/Left arrows: Navigate between images")
   print("- ESC: Quit")
   print("\nStarting slideshow...")

   random.shuffle(images)
   index = 0
   total_images = len(images)

   running = True
   last_update = time.time()
   while running:
       try:
           image = pygame.image.load(images[index])
           image = scale_image(image, screen_width, screen_height)
           screen.fill((0, 0, 0))  # Black background
           screen.blit(image, image.get_rect(center=screen.get_rect().center))
           pygame.display.flip()
       except pygame.error as e:
           print(f"Error loading image {images[index]}: {e}")
           index = (index + 1) % total_images
           continue

       while True:
           if SHUFFLE_TIME > 0:
               current_time = time.time()
               if current_time - last_update >= SHUFFLE_TIME:
                   index = (index + 1) % total_images
                   last_update = current_time
                   break

           event = pygame.event.wait(50 if SHUFFLE_TIME > 0 else 0)
           if event is None:
               continue
           if event.type == pygame.QUIT:
               running = False
               break
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                   running = False
                   break
               elif event.key == pygame.K_RIGHT:
                   index = (index + 1) % total_images
                   last_update = time.time()
                   break
               elif event.key == pygame.K_LEFT:
                   index = (index - 1) % total_images
                   last_update = time.time()
                   break

   pygame.quit()
   sys.exit()

def scale_image(image, max_width, max_height):
   width, height = image.get_size()
   scale = min(max_width / width, max_height / height)
   new_size = (int(width * scale), int(height * scale))
   return pygame.transform.smoothscale(image, new_size)

if __name__ == "__main__":
   main()
