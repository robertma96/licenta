import cv2
import numpy as np


def blend(img_non_styled_path, img_styled_path, output_path):
    img1 = cv2.imread(img_non_styled_path)  # Non-styled image
    img2 = cv2.imread(img_styled_path)  # Styled image
    blank_image = np.zeros((img1.shape[0], img1.shape[1], 3), np.uint8)
    blank_image2 = np.zeros((img1.shape[0], img1.shape[1], 3), np.uint8)
    blank_image3 = np.zeros((img1.shape[0], img1.shape[1], 3), np.uint8)

    # Resize if necessary (sometimes styling adds 2-4 pixels to the original image)
    (img_height, img_width) = img1.shape[:2]
    img2 = cv2.resize(img2, (img_width, img_height))

    # Smaller border radius means smoother transition from styled image to non-styled image (Min = 1)
    border_radius = 1

    # m represents how much we want the styled image to weight in the blending process.
    # Ex: m = 2 means the styled image will have a bigger weight than the non-styled image
    m = 2

    step = 0

    if img1.shape[0] > img1.shape[1]:
        necessary_dimension = img1.shape[0]
    else:
        necessary_dimension = img1.shape[1]

    necessary_pixels = necessary_dimension / 2

    necessary_iterations = int(necessary_pixels / border_radius) + 1

    step_alpha = m * (1 / necessary_iterations)

    alpha = 1
    beta = 1 - alpha

    for i in range(necessary_iterations):
        if alpha < 0:
            alpha = 0
        elif alpha > 1:
            alpha = 1

        if i == 0:
            # Image 1
            bottom_1 = img1[-border_radius:, border_radius:-border_radius, :]
            blank_image[-border_radius:, border_radius:-border_radius, :] = bottom_1

            right_1 = img1[:, -border_radius:, :]
            blank_image[:, -border_radius:, :] = right_1

            left_1 = img1[:, 0:border_radius, :]
            blank_image[:, 0:border_radius, :] = left_1

            top_1 = img1[0:border_radius, border_radius:-border_radius, :]
            blank_image[0:border_radius, border_radius:-border_radius, :] = top_1

            # Image 2
            bottom_2 = img2[-border_radius:, border_radius:-border_radius, :]
            blank_image2[-border_radius:, border_radius:-border_radius, :] = bottom_2

            right_2 = img2[:, -border_radius:, :]
            blank_image2[:, -border_radius:, :] = right_2

            left_2 = img2[:, 0:border_radius, :]
            blank_image2[:, 0:border_radius, :] = left_2

            top_2 = img2[0:border_radius, border_radius:-border_radius, :]
            blank_image2[0:border_radius, border_radius:-border_radius, :] = top_2

            # Blending the 2 images
            blank_image3[-border_radius:, border_radius:-border_radius, :] = cv2.addWeighted(bottom_1, alpha, bottom_2,
                                                                                             beta, 0.0)  # Bottom
            blank_image3[:, -border_radius:, :] = cv2.addWeighted(right_1, alpha, right_2, beta, 0.0)  # Right
            blank_image3[:, 0:border_radius, :] = cv2.addWeighted(left_1, alpha, left_2, beta, 0.0)  # Left
            blank_image3[0:border_radius, border_radius:-border_radius, :] = cv2.addWeighted(top_1, alpha, top_2, beta,
                                                                                             0.0)  # Top

            step = border_radius
        else:
            # Image 1
            bottom_1 = img1[-step - border_radius:-step, border_radius + step:-border_radius - step]
            blank_image[-step - border_radius:-step, border_radius + step:-border_radius - step] = bottom_1

            right_1 = img1[step:-step, -step - border_radius:-step, :]
            blank_image[step:-step, -step - border_radius:-step, :] = right_1

            left_1 = img1[step:-step, step:step + border_radius, :]
            blank_image[step:-step, step:step + border_radius, :] = left_1

            top_1 = img1[step:step + border_radius, border_radius + step:-border_radius - step, :]
            blank_image[step:step + border_radius, border_radius + step:-border_radius - step, :] = top_1

            # Image 2
            bottom_2 = img2[-step - border_radius:-step, border_radius + step:-border_radius - step]
            blank_image2[-step - border_radius:-step, border_radius + step:-border_radius - step] = bottom_2

            right_2 = img2[step:-step, -step - border_radius:-step, :]
            blank_image2[step:-step, -step - border_radius:-step, :] = right_2

            left_2 = img2[step:-step, step:step + border_radius, :]
            blank_image2[step:-step, step:step + border_radius, :] = left_2

            top_2 = img2[step:step + border_radius, border_radius + step:-border_radius - step, :]
            blank_image2[step:step + border_radius, border_radius + step:-border_radius - step, :] = top_2

            # Blending the 2 images
            blank_image3[-step - border_radius:-step, border_radius + step:-border_radius - step] = cv2.addWeighted(
                bottom_1, alpha, bottom_2, beta, 0.0)  # Bottom
            blank_image3[step:-step, -step - border_radius:-step, :] = cv2.addWeighted(right_1, alpha, right_2, beta,
                                                                                       0.0)  # Right
            blank_image3[step:-step, step:step + border_radius, :] = cv2.addWeighted(left_1, alpha, left_2, beta,
                                                                                     0.0)  # Left
            blank_image3[step:step + border_radius, border_radius + step:-border_radius - step, :] = cv2.addWeighted(
                top_1,
                alpha,
                top_2,
                beta,
                0.0)  # Top

            step = step + border_radius

        alpha = alpha - step_alpha
        beta = 1 - alpha

    cv2.imwrite(output_path, blank_image3)
