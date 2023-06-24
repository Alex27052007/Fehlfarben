from PIL import Image, ImageStat
import sys
import csv

def create_image(size, mode):
    return Image.new(mode, size, "white")

def is_grayscale(path):
    image = Image.open(path).convert("RGB")
    stat = ImageStat.Stat(image)
    return sum(stat.sum) / 3 == stat.sum[0]

def save_image(image, path):
    image.save(path, 'png')

def get_minmax(image):
    min_value = 255
    max_value = 0
    pixels = image.load()
    width, height = image.size

    for i in range(width):
        for j in range(height):
            gray = pixels[i, j]
            min_value = min(min_value, gray)
            max_value = max(max_value, gray)

    return min_value, max_value

def set_contrast(image):
    min_value, max_value = get_minmax(image)

    if max_value != min_value:
        width, height = image.size
        new_image = create_image((width, height), "L")
        pixels = new_image.load()

        for i in range(width):
            for j in range(height):
                gray = image.getpixel((i, j))
                new_gray = (gray - min_value) / (max_value - min_value) * 255
                pixels[i, j] = int(new_gray)

        return new_image

def convert_pseudocolor(image, zone_values):
    width, height = image.size
    new_image = create_image((width, height), "RGB")
    pixels = new_image.load()

    for i in range(width):
        for j in range(height):
            gray = image.getpixel((i, j))
            color = zone_values[gray]
            pixels[i, j] = color

    return new_image

if len(sys.argv) != 3:
    print('Please provide the image name as the first parameter and the zone value file name as the second parameter.')
    exit()

image_file_name = sys.argv[1]
color_map_file_name = sys.argv[2]

if is_grayscale(image_file_name):
    zone_values = []

    try:
        with open(color_map_file_name) as csv_file:
            reader = csv.reader(csv_file, delimiter=' ')
            for row in reader:
                color_as_tuple = eval(row[0].split(";")[1])
                zone_values.append(color_as_tuple)

        original_image = Image.open(image_file_name)
        contrasted_image = set_contrast(original_image)
        save_image(contrasted_image, 'results/contrasted_' + image_file_name)
        converted_image = convert_pseudocolor(contrasted_image, zone_values)
        save_image(converted_image, 'results/converted_' + image_file_name)
        converted_image.show()

    except Exception as e:
        error_message = str(e)
        print("An error occurred while processing the image:", error_message)
else:
    print('The input file could not be processed. Please provide a grayscale image.')
