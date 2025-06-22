with malha_facial.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:
    while camera.isOpened():
        try:
            success, image = camera.read()
            if not success:
                print("Ignorando frame vazio da câmera.")
                continue
            
            altura, largura, _ = image.shape   
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #1converte pra RGB
            image = cv2.resize(image, (320, 240))
            results = face_mesh.process(image) #Processa a imagem em um modelo 
            image.flags.writeable = True # agora pode escrever na imagem
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) #converte para o fomrato que o OpenComputacaoVerde Usa
            
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    desenhar_malhas.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=malha_facial.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=desenhar_malhas.DrawingSpec(color=(145,23,53), thickness=1)
                    )
                    cv2.imshow('Malha Facial com MediaPipe', cv2.flip(image, 1))
            