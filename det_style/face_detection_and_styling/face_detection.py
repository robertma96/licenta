import dlib
import cv2
import os
import subprocess
from . import blending


# take a bounding predicted by dlib and convert it
# to the format (x, y, w, h) as we would normally do
# with OpenCV
def rectangle_to_boundrybox(rect):
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    return x, y, w, h


# Resize Image
def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def face_detection(full_image_name, image_path, results_path, model_path, reverse):
    if reverse == 'True':
        reverse = True
    elif reverse == 'False':
        reverse = False
    dirpath = os.path.dirname(os.path.realpath(__file__))
    evaluate_path = os.path.join(dirpath, 'evaluate.py')
    # Citire imagine
    img = cv2.imread(image_path)
    if img is None:
        print("Nicio imagine nu exista in locatia specificata")
        return 0

    (img_name, img_extension) = os.path.splitext(full_image_name)

    # Folderul de baza
    base_dir = os.path.realpath(os.path.join(results_path, 'results'))

    # Calea catre folder-ul nou creat pentru imagine
    directory = os.path.realpath(os.path.join(base_dir, img_name))

    # Se creeaza un folder cu denumirea imaginii. In acest folder se creeaza si foldere pentru imaginile stilizate
    # si cele stilizate cu blending
    if not os.path.isdir(directory):
        os.makedirs(os.path.join(base_dir, img_name))
        os.makedirs(os.path.join(base_dir, img_name) + '/styled')
        os.makedirs(os.path.join(base_dir, img_name) + '/blended')
        os.makedirs(os.path.join(base_dir, img_name) + '/unstyled')
    path = directory

    img_width = img.shape[1]
    img_height = img.shape[0]

    # Redimensionam imaginea pentru a se putea face stilizarea (nu stiu care este dim maxima pe care se poate face
    # stilizarea pe placa video)
    if (img_width * img_height) > 2073600:
        while (img_width * img_height) > 2073600:
            img = image_resize(img, height=int(img_height - img_height * 0.05))
            img_width = img.shape[1]
            img_height = img.shape[0]
    resized_image_name = img_name + '_RESIZED' + img_extension
    cv2.imwrite(os.path.join(directory, resized_image_name), img)
    resized_image_path = os.path.join(directory, resized_image_name)

    detector = dlib.get_frontal_face_detector()

    # Acel 1 va face imaginea mai mare, putand detecta mai multe fete
    dets = detector(img, 1)

    i = -1

    # Se pregateste comanda pentru stilizare
    styled_image_name = img_name + '_STYLED' + img_extension
    cmd = [os.path.realpath(evaluate_path),
           '--checkpoint', model_path,
           '--in-path', resized_image_path,
           '--out-path', os.path.join(path, styled_image_name)]

    # Se apeleaza evaluate.py pentru stilizare
    command = subprocess.call(cmd, shell=True)

    if command != 0:
        print("Nu s-a putut stiliza imaginea, cel mai probabil dimensiunea imaginii este prea mare")
        return 0

    styled_image_final = cv2.imread(os.path.join(directory, styled_image_name))

    # Doar imaginea stilizata
    if reverse == 'only_style':
        return os.path.join(directory, styled_image_name)

    # Verificam daca dorim ca doar fetele sa fie stilizate, sau fundalul
    if reverse is True:
        divizor = 2
    else:
        divizor = 1

    for det in dets:
        x, y, w, h = rectangle_to_boundrybox(det)
        i = i + 1
        if w > 30 and h > 30:
            # image_name_styled = image_name.split('.')[0] + "_" + str(i) + "_blended" + "." + image_name.split('.')[1]

            region_of_interest = img[y:y + h, x:x + w]
            roi_height = region_of_interest.shape[0]
            roi_width = region_of_interest.shape[1]

            # Numarul de pixeli cu care vom mari dreptunghiul care va incadra fata (pentru blending)
            offset_height = int(roi_height / divizor)
            offset_width = int(roi_width / divizor)

            if y - offset_height < 0:
                offset_height_up = y
            else:
                offset_height_up = offset_height

            if y + h + offset_height > img_height:
                offset_height_down = img_height - y + h
            else:
                offset_height_down = offset_height

            if x - offset_width < 0:
                offset_width_left = x
            else:
                offset_width_left = offset_width

            if x + w + offset_width > img_width:
                offset_width_right = img_width - x + w
            else:
                offset_width_right = offset_width

            # Dreptunghiul fetei impreuna cu offset. Aceasta imagine urmeaza a fi stilizata.
            styled_image_with_offset = styled_image_final[y - offset_height_up:y + h + offset_height_down,
                                       x - offset_width_left:x + w + offset_width_right]
            normal_image_with_offset = img[y - offset_height_up:y + h + offset_height_down,
                                       x - offset_width_left:x + w + offset_width_right]

            # Cum se va numi imaginea pentru fiecare fata detectata. Ex: Pentru o imagine denumita 'test', in care sunt
            # detectate 3 fete, vom avea 3 imagini denumite test_0, test_1, test_2.
            image_name_output = img_name + "_" + str(i) + "." + img_extension
            # Calea unde se afla imaginea care urmeaza sa fie stilizata
            image_output_path_styled = os.path.join(path, 'styled', image_name_output)
            # Calea catre unde se vor salva imaginile nestilizate.
            image_output_path_normal = os.path.join(path, 'unstyled', image_name_output)

            # Se vor salva aceste imagini in folder-ul 'results'
            cv2.imwrite(image_output_path_styled, styled_image_with_offset)
            cv2.imwrite(image_output_path_normal, normal_image_with_offset)

            # Calea unde se vor salva imaginile blenduite
            output_path_blended = os.path.join(path, 'blended', image_name_output)

            # Functia pentru blending primeste 3 argumente. Primul este imaginea nestilizata, al
            # doilea este imaginea stilizata, iar al 3 lea reprezinta locatia unde sa salveze rezultatul
            # Schimbam ordinea in functie de cum vrem sa se faca blending-ul; reverse = False => Fata stilizata
            # reverse = True => Fundal stilizata, fata nestilizata
            if reverse is True:
                blending.blend(image_output_path_styled, image_output_path_normal, output_path_blended)
            elif reverse is False:
                blending.blend(image_output_path_normal, image_output_path_styled, output_path_blended)

            # Adaugam imaginea stilizata care a trecut si prin procesul de blending inapoi in imaginea originala de la
            # care am plecat
            img_blended = cv2.imread(output_path_blended)
            if reverse is True:
                styled_image_final[y - offset_height_up:y + h + offset_height_down,
                x - offset_width_left:x + w + offset_width_right] = img_blended
            elif reverse is False:
                img[y - offset_height_up:y + h + offset_height_down,
                x - offset_width_left:x + w + offset_width_right] = img_blended
    final_image = img_name + "_FINAL" + img_extension
    restored_image_with_style_path = os.path.join(path, final_image)
    if reverse is True:
        cv2.imwrite(restored_image_with_style_path, styled_image_final)
    else:
        cv2.imwrite(restored_image_with_style_path, img)
    return restored_image_with_style_path
