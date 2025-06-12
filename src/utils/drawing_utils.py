from PIL import Image, ImageFont
import textwrap
import math


def resize_sprite(sprite: Image.Image, scale_flearner: float) -> Image.Image:
    """
    Resizes a sprite by a given scale flearner.
    """
    width, height = sprite.size
    new_width = int(width * scale_flearner)
    new_height = int(height * scale_flearner)
    return sprite.resize((new_width, new_height), Image.Resampling.LANCZOS)


def adjust_cloud(
    cloud: Image.Image, message: str, used_font: ImageFont.FreeTypeFont
) -> tuple[Image.Image, list[str], float]:
    """
    Adjusts the cloud size to fit the message by extending the middle portion.
    Determines the target cloud size based on text content first, then wraps text accordingly.
    Maintains a 2:3 height-to-width ratio and handles text wrapping.
    Returns a new image with the adjusted cloud, the wrapped text lines, the calculated font size, and line spacing.
    """
    # Calculate base dimensions
    base_width, base_height = cloud.size
    padding = 40  # Padding inside the cloud

    # Get precise text dimensions using the font
    sample_bbox = used_font.getbbox("Aj")  # Sample with ascender and descender
    line_height = (
        sample_bbox[3] - sample_bbox[1]
    )  # Full height including ascenders/descenders
    line_spacing = line_height * 1.2  # 20% extra space between lines

    sample_bbox = used_font.getbbox(message)
    avg_char_width = (sample_bbox[2] - sample_bbox[0]) / len(message)

    # Fixed calculations for optimal text layout
    desired_aspect_ratio = 3.0 / 2.0  # width to height
    total_chars = len(message)

    # Calculate optimal dimensions based on character count and aspect ratio
    optimal_chars_per_line = math.sqrt(
        total_chars * desired_aspect_ratio * line_spacing / avg_char_width
    )
    target_line_width = int(optimal_chars_per_line)

    wrapped_lines = textwrap.wrap(
        message, width=max(target_line_width, 20)
    )  # minimum 20 chars
    actual_lines = len(wrapped_lines)

    # Calculate precise text area needed based on ACTUAL wrapped text
    if wrapped_lines:
        # Get the actual width of the widest line
        actual_text_width = max(
            used_font.getbbox(line)[2] - used_font.getbbox(line)[0]
            for line in wrapped_lines
        )
        actual_text_height = actual_lines * line_spacing
    else:
        actual_text_width = 0
        actual_text_height = 0

    # Calculate target dimensions with padding
    target_width = max(actual_text_width + (padding * 2), base_width)
    target_height = max(actual_text_height + (padding * 2), base_height)

    # Calculate how much we need to expand
    needed_width = max(0, target_width - base_width)
    needed_height = max(0, target_height - base_height)

    new_width = base_width + needed_width
    new_height = base_height + needed_height

    # Ensure both dimensions are integers
    new_width = int(new_width)
    new_height = int(new_height)

    # If we need to resize the cloud
    if new_width > base_width or new_height > base_height:
        # Create a new blank image
        new_cloud = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))

        # The rest of the code for resizing the cloud remains the same
        # Get the middle column and row for expansion
        mid_x = base_width // 2
        mid_y = base_height // 2

        # Extract the four corners
        top_left = cloud.crop((0, 0, mid_x, mid_y))
        top_right = cloud.crop((mid_x, 0, base_width, mid_y))
        bottom_left = cloud.crop((0, mid_y, mid_x, base_height))
        bottom_right = cloud.crop((mid_x, mid_y, base_width, base_height))

        # Paste the corners
        new_cloud.paste(top_left, (0, 0), top_left)
        new_cloud.paste(top_right, (new_width - (base_width - mid_x), 0), top_right)
        new_cloud.paste(
            bottom_left, (0, new_height - (base_height - mid_y)), bottom_left
        )
        new_cloud.paste(
            bottom_right,
            (new_width - (base_width - mid_x), new_height - (base_height - mid_y)),
            bottom_right,
        )

        # Sample a few pixels from the center of the cloud to use for filling
        center_pixel = cloud.getpixel((mid_x, mid_y))

        # Create horizontal and vertical "strips" from the original cloud
        top_strip = cloud.crop((mid_x, 0, mid_x + 1, mid_y))
        bottom_strip = cloud.crop((mid_x, mid_y, mid_x + 1, base_height))
        left_strip = cloud.crop((0, mid_y, mid_x, mid_y + 1))
        right_strip = cloud.crop((mid_x, mid_y, base_width, mid_y + 1))

        # Fill the horizontal middle sections (top and bottom)
        for x in range(mid_x, new_width - (base_width - mid_x)):
            # Top section
            for y in range(0, mid_y):
                pixel = top_strip.getpixel((0, y))
                new_cloud.putpixel((x, y), pixel)

            # Bottom section
            for y in range(new_height - (base_height - mid_y), new_height):
                rel_y = y - (new_height - (base_height - mid_y))
                pixel = bottom_strip.getpixel((0, rel_y))
                new_cloud.putpixel((x, y), pixel)

        # Fill the vertical middle sections (left and right)
        for y in range(mid_y, new_height - (base_height - mid_y)):
            # Left section
            for x in range(0, mid_x):
                pixel = left_strip.getpixel((x, 0))
                new_cloud.putpixel((x, y), pixel)

            # Right section
            for x in range(new_width - (base_width - mid_x), new_width):
                rel_x = x - (new_width - (base_width - mid_x))
                pixel = right_strip.getpixel((rel_x, 0))
                new_cloud.putpixel((x, y), pixel)

        # Fill the center section (expanded area)
        for y in range(mid_y, new_height - (base_height - mid_y)):
            for x in range(mid_x, new_width - (base_width - mid_x)):
                new_cloud.putpixel((x, y), center_pixel)

        return new_cloud, wrapped_lines, line_spacing

    return cloud, wrapped_lines, line_spacing
