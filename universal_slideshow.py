import os
import sys
import random
import pygame
import time
import subprocess

# Set IMAGE_DIRECTORY to override automatic directory detection.
# Leave as None to use the system's default Pictures folder.
IMAGE_DIRECTORY = r'C:\Fniz'

# Example paths — uncomment and modify one if you want a specific directory:
# IMAGE_DIRECTORY = r'C:\Users\Username\Pictures'   # Windows
# IMAGE_DIRECTORY = '/Users/Username/Pictures'       # macOS
# IMAGE_DIRECTORY = '/home/Username/Pictures'        # Linux

# Shuffle the image order on startup (True) or use a deterministic sort (False).
SHUFFLE = True

# When SHUFFLE is False, choose how images are sorted:
#   'name'          – alphabetical by filename (default)
#   'date_modified' – newest files first
#   'date_created'  – newest creation time first (falls back to modified on Linux)
#   'size'          – largest files first
#   'extension'     – grouped by file extension, then alphabetical
SORT_ORDER = 'name'

# Seconds between automatic image advancement.
# Set to 0 to disable auto-advance (manual navigation only).
SLIDE_INTERVAL = 0

SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.pcx', '.tga', '.tif', '.tiff',
    '.lbm', '.pbm', '.pgm', '.ppm', '.xpm',
)

def get_pictures_dir():
    """Return the most appropriate pictures directory for the current platform."""
    if IMAGE_DIRECTORY and os.path.exists(IMAGE_DIRECTORY):
        return IMAGE_DIRECTORY

    # Windows — query the registry for the Shell Folders value
    if os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',
            ) as key:
                return winreg.QueryValueEx(key, 'My Pictures')[0]
        except Exception:
            pass

    # macOS
    elif sys.platform == 'darwin':
        mac_pictures = os.path.expanduser('~/Pictures')
        if os.path.exists(mac_pictures):
            return mac_pictures

    # Linux / Unix — try xdg-user-dir first
    elif sys.platform.startswith('linux'):
        try:
            result = subprocess.run(
                ['xdg-user-dir', 'PICTURES'],
                capture_output=True,
                text=True,
            )
            pictures_dir = result.stdout.strip()
            if pictures_dir and os.path.exists(pictures_dir):
                return pictures_dir
        except FileNotFoundError:
            pass

    # Fallback: common localised folder names
    home = os.path.expanduser('~')
    for name in (
        'Pictures', 'Bilder', 'Images', 'Imágenes', 'Obrazy',
        'Изображения', 'My Pictures', 'Mina bilder', 'Mes images',
        'Meine Bilder',
    ):
        path = os.path.join(home, name)
        if os.path.exists(path):
            return path

    return os.path.join(home, 'Pictures')

def collect_images(directory):
    """Return a list of image paths from *directory*, ordered according to config."""
    images = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

    if not images:
        return images

    if SHUFFLE:
        random.shuffle(images)
    else:
        images = _sort_images(images, SORT_ORDER)

    return images


def _sort_images(images, order):
    """Sort *images* according to *order* and return a new list."""
    order = order.lower().strip()

    if order == 'name':
        return sorted(images, key=lambda p: os.path.basename(p).lower())

    if order == 'date_modified':
        return sorted(images, key=os.path.getmtime, reverse=True)

    if order == 'date_created':
        # On Windows, st_ctime is creation time; on Unix it's metadata-change
        # time.  Python 3.12+ exposes st_birthtime on some Unix filesystems,
        # but we fall back to st_ctime for broad compatibility.
        def _creation_time(path):
            stat = os.stat(path)
            return getattr(stat, 'st_birthtime', stat.st_ctime)
        return sorted(images, key=_creation_time, reverse=True)

    if order == 'size':
        return sorted(images, key=os.path.getsize, reverse=True)

    if order == 'extension':
        return sorted(
            images,
            key=lambda p: (
                os.path.splitext(p)[1].lower(),
                os.path.basename(p).lower(),
            ),
        )

    # Unknown order — fall back to alphabetical
    print(f"Warning: unknown SORT_ORDER '{order}', falling back to 'name'.")
    return sorted(images, key=lambda p: os.path.basename(p).lower())

def scale_image(image, max_width, max_height):
    """Scale *image* to fit within *max_width* × *max_height*, preserving aspect ratio."""
    w, h = image.get_size()
    scale = min(max_width / w, max_height / h)
    return pygame.transform.smoothscale(image, (int(w * scale), int(h * scale)))

def main():
    image_directory = get_pictures_dir()

    print('\nImage Slideshow')
    print('===============')
    print(f'Directory : {image_directory}')

    if not os.path.exists(image_directory):
        print(f'Error: directory "{image_directory}" does not exist!')
        sys.exit(1)

    images = collect_images(image_directory)

    if not images:
        print(f'No supported images found in {image_directory}')
        print(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)

    order_label = 'shuffled' if SHUFFLE else SORT_ORDER
    interval_label = 'disabled' if SLIDE_INTERVAL == 0 else f'{SLIDE_INTERVAL}s'

    print(f'Images    : {len(images)}')
    print(f'Order     : {order_label}')
    print(f'Auto-adv. : {interval_label}')
    print('\nControls:')
    print('  Right / Left  — next / previous image')
    print('  S             — reshuffle images')
    print('  Escape        — quit')
    print('\nStarting slideshow…')

    pygame.init()
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
    pygame.display.set_caption('Image Slideshow')
    clock = pygame.time.Clock()

    index = 0
    total = len(images)
    last_advance = time.monotonic()  # monotonic avoids wall-clock jumps
    need_redraw = True

    running = True
    while running:
        if need_redraw:
            try:
                raw = pygame.image.load(images[index]).convert()
                scaled = scale_image(raw, screen_w, screen_h)
                screen.fill((0, 0, 0))
                screen.blit(scaled, scaled.get_rect(center=screen.get_rect().center))
                pygame.display.flip()
            except pygame.error as exc:
                print(f'Skipping {images[index]}: {exc}')
                index = (index + 1) % total
                continue
            need_redraw = False

        if SLIDE_INTERVAL > 0:
            if time.monotonic() - last_advance >= SLIDE_INTERVAL:
                index = (index + 1) % total
                last_advance = time.monotonic()
                need_redraw = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_RIGHT:
                    index = (index + 1) % total
                    last_advance = time.monotonic()
                    need_redraw = True

                elif event.key == pygame.K_LEFT:
                    index = (index - 1) % total
                    last_advance = time.monotonic()
                    need_redraw = True

                elif event.key == pygame.K_s:
                    random.shuffle(images)
                    index = 0
                    last_advance = time.monotonic()
                    need_redraw = True
                    print('Images reshuffled!')

        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
