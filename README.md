# Universal Slideshow

A lightweight, cross-platform image slideshow application that works seamlessly on Windows (7+), macOS (10.9+), and Linux. Browse your image collection in fullscreen with arrow key navigation, randomized order, and automatic advancement.

Navigate manually using left/right arrow keys, or let the slideshow auto-advance every 5 seconds. Press ESC to exit.

## Features

- Fullscreen display with automatic image scaling
- Works across Windows, macOS, and Linux
- Manual navigation with arrow keys
- Random image order
- Configurable auto-advance timer
- Smart detection of system Pictures folder
- Black background for optimal viewing

## Installation

1. Ensure you have Python 3.6 or newer installed
2. Install the required package:
```bash
pip install pygame
```
3. Download and run the script:
```bash
python universal_slideshow.py
```

## Configuration

### Image Directory

By default, the slideshow uses your system's Pictures folder. To use a custom directory:

1. Open `universal_slideshow.py`
2. Find the `IMAGE_DIRECTORY` variable at the top
3. Uncomment and modify one of these examples:
```python
# IMAGE_DIRECTORY = r'C:\Users\Username\Pictures'    # Windows
# IMAGE_DIRECTORY = '/Users/Username/Pictures'       # macOS
# IMAGE_DIRECTORY = '/home/Username/Pictures'        # Linux
```

### Auto-Advance Timer

To change how long each image is displayed:

1. Find the `SHUFFLE_TIME` variable
2. Set to desired seconds (e.g., `SHUFFLE_TIME = 10`)
3. Set to `0` to disable auto-advance

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- PCX (.pcx)
- TGA (.tga)
- TIFF (.tif, .tiff)
- LBM (.lbm)
- PBM (.pbm)
- PGM (.pgm)
- PPM (.ppm)
- XPM (.xpm)

## Controls

- **Right Arrow**: Next image
- **Left Arrow**: Previous image
- **ESC**: Exit slideshow

## Requirements

- Python 3.6+
- pygame

## License

[MIT License](LICENSE)

---

All suggestions for improvements are welcome! Feel free to open an issue or submit a pull request.
