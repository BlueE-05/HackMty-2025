import cv2 as cv
import numpy as np

bottle_detection = "Training_Images/Test2.jpg"

searching_image = "Training_Images/Test1.jpg"

template_image = cv.imread(bottle_detection, cv.IMREAD_REDUCED_COLOR_2) # Objeto que se esta buscando
searching_results = cv.imread(searching_image, cv.IMREAD_REDUCED_COLOR_2) # Imagen donde se esta buscando el objeto







# All the 6 methods for comparison in a list
methods = ['TM_CCOEFF', 'TM_CCOEFF_NORMED', 'TM_CCORR',
            'TM_CCORR_NORMED']

for meth in methods:
    method = getattr(cv, meth)
    # Comparamos las imagenes, entre mas blanco es mayor coincidencia y entre mas negro es menor coincidencia
    result = cv.matchTemplate(searching_results, template_image, method)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    print(f"Method: {meth}")
    print('Best match top left position: %s' % str(max_loc))
    print('Best match confidence: %s' % str(max_val))

    threshold = 0.28
    if max_val >= threshold:
        print("Objeto encontrado")

        ancho_imagen = template_image.shape[1]
        alto_imagen = template_image.shape[0]

        top_left = max_loc
        bottom_right = (top_left[0] + ancho_imagen, top_left[1] + alto_imagen)

        cv.rectangle(searching_results, top_left, bottom_right,
            color = (0, 255, 0), thickness = 2, lineType = cv.LINE_4)
        
        cv.imshow('Result',searching_results)
        cv.waitKey()
    else:
        print("Objeto no encontrado")