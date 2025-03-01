import cv2
import numpy as np


class PngToGcode:
    def __init__(self, input_path="", output_path=""):
        self.input = input_path
        self.output = output_path
        self.gcode_height = 0
        self.gcode_width = 0
        self.pen_up = ""
        self.pen_down = ""

    # def convert_to_grayscale(self, image_path):
    #     """
    #     Convert the image to a grayscale bitmap.
    #     """
    #     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    #     cv2.imwrite('grayscale_image.png', image)
    #     return image

    def convert_to_grayscale(self, image_path):
        """
        Convert the image to a grayscale bitmap.
        """
        print(f"Reading image from: {image_path}")
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not load image from path: {image_path}. Ensure the file exists and is a valid image.")
        print(f"Image loaded successfully with shape: {image.shape}")
        cv2.imwrite('grayscale_image.png', image)
        return image


    def bitmap_to_paths(self, image):
        """
        Convert a bitmap to paths using OpenCV to find contours.
        """
        # Threshold the image
        _, threshold = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        paths = []
        for contour in contours:
            path = []
            for point in contour:
                path.append((point[0][0], point[0][1]))
            paths.append(path)
        return paths

    def calculate_scaling_factors(self, image, target_height_mm=100, target_width_mm=100):
        """
        Calculate the scaling factors to scale the image to the target size in millimeters.
        """
        height, width = image.shape
        height_scale = target_height_mm / height
        width_scale = target_width_mm / width
        return height_scale, width_scale

    def paths_to_gcode(self, paths, height_scale=1.0, width_scale=1.0):
        """
        Convert paths to G-code commands with scaling.
        """
        gcode_commands = []

        for path in paths:
            if len(path) > 0:
                gcode_commands.append(
                    f"G0 X{path[0][0] * width_scale} Y{path[0][1] * height_scale}")  # Move to the start of the path
                gcode_commands.append(self.pen_up + " ; Pen up")  # Raise the pen
                for point in path[1:]:
                    gcode_commands.append(
                        f"G01 X{point[0] * width_scale} Y{point[1] * height_scale}")  # Draw to the next point
                gcode_commands.append(self.pen_down + " ; Pen down")  # Lower the pen

        return gcode_commands

    def save_gcode(self, gcode, filename='output'): #output.gcode
        """
        Save G-code to a file.
        """
        with open(filename + ".gcode", 'w') as f:
            for line in gcode:
                f.write(line + '\n')

    # def gen_all(self):
    #     image_array = self.convert_to_grayscale(self.input)
    #     # Calculate the scaling factors to ensure the drawing is 100x100mm
    #     height_scale, width_scale = self.calculate_scaling_factors(image_array, target_height_mm=self.gcode_height,
    #                                                                target_width_mm=self.gcode_width)
    #     paths = self.bitmap_to_paths(image_array)
    #     gcode = self.paths_to_gcode(paths, height_scale, width_scale)
    #     self.save_gcode(gcode, self.output)

    #     print(f"G-code generation complete. Saved to '{self.output}'.")

    def gen_all(self):
        if not self.input:
            raise ValueError("Input image path is not set. Please load an image first.")
        image_array = self.convert_to_grayscale(self.input)
        # Obliczanie skalowania i generowanie G-code
        height_scale, width_scale = self.calculate_scaling_factors(image_array, target_height_mm=self.gcode_height,
                                                                target_width_mm=self.gcode_width)
        paths = self.bitmap_to_paths(image_array)
        gcode = self.paths_to_gcode(paths, height_scale, width_scale)
        self.save_gcode(gcode, self.output)
        print(f"G-code generation complete. Saved to '{self.output}'.")