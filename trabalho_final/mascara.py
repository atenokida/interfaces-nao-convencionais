from concurrent.futures import ThreadPoolExecutor 
import math
import subprocess
import sys
import time
import traceback

import cv2
import mediapipe as mp
import pyautogui

import face_mesh_module

PONTOS_OLHO_ESQUERDO = [362, 385, 387, 263, 373, 380]
PONTOS_OLHO_DIREITO = [33, 160, 158, 133, 153, 144]
PONTOS_BOCA = [78, 308, 13, 14]

LIMIAR_PISCADA = 0.15
LIMIAR_BOCA_ABERTA = 0.3

TECLA_OLHO_ESQUERDO_FECHADO = 'a'
TECLA_OLHO_DIREITO_FECHADO = 'd'
TECLA_BOCA_ABERTA = 'w'

malha_facial = mp.solutions.face_mesh
camera = cv2.VideoCapture(0)
desenhar_malhas = mp.solutions.drawing_utils
desenhar_especificacao = desenhar_malhas.DrawingSpec(thickness=1, circle_radius=1)

_estado_olho_esquerdo = 'aberto'
_estado_olho_direito = 'aberto'
_estado_boca = 'fechada'

_executor = ThreadPoolExecutor(max_workers=3)


def aperta_tecla(tecla):
    print(f"Pressionando tecla: {tecla}")

    try:
        if sys.platform == 'win32':
            pyautogui.press(tecla)
            print(f"Tecla '{tecla}' pressionada.")
            
        elif sys.platform.startswith('linux'):
            subprocess.Popen(['wtype', tecla])
            print(f"Tecla '{tecla}' pressionada.")
            
        else:
            print("Sistema operacional não suportado.")
            return
    except FileNotFoundError:
        print("ERRO: O comando 'wtype' não foi encontrado. Instale com: sudo pacman -S wtype")
    except Exception as e:
        print("ERRO ao pressionar a tecla:", tecla)
        traceback.print_exc()


def pressionar_tecla(tecla):
    print(f'Segurando tecla: {tecla}')
    
    try:
        if sys.platform == 'win32':
            pyautogui.keyDown(tecla)
        elif sys.platform.startswith('linux'):
            subprocess.Popen(['wtype', '-k', tecla])
        else:
            print('Sistema operacional não suportado para pressionar tecla.')
            
    except FileNotFoundError:
        print('ERRO: Comando \'wtype\' não foi encontrado.')
        
    except Exception:
        print(f'ERRO ao pressionar a tecla: {tecla}')
        traceback.print_exc()


def soltar_tecla(tecla):
    print(f'Soltando tecla: {tecla}')
    
    try:
        if sys.platform == 'win32':
            pyautogui.keyUp(tecla)
        elif sys.platform.startswith('linux'):
            subprocess.Popen(['wtype', '-K', tecla])
        else:
            print('Sistema operacional não suportado para soltar tecla.')
    
    except FileNotFoundError:
        print('ERRO: Comando \'wtype\' não foi encontrado.')
    
    except Exception:
        print(f'ERRO ao soltar a tecla: {tecla}')
        traceback.print_exc()


def distancia_euclidiana(ponto1, ponto2):
    return math.sqrt((ponto1.x - ponto2.x)**2 + (ponto1.y - ponto2.y)**2)


def calcular_olho(landmarks, pontos_olho):
    p2_p6 = distancia_euclidiana(landmarks[pontos_olho[1]], landmarks[pontos_olho[5]])
    p3_p5 = distancia_euclidiana(landmarks[pontos_olho[2]], landmarks[pontos_olho[4]])
    p1_p4 = distancia_euclidiana(landmarks[pontos_olho[0]], landmarks[pontos_olho[3]])
    if p1_p4 == 0: return 0.0
    ear = (p2_p6 + p3_p5) / (2.0 * p1_p4)
    return ear


def calcular_boca(landmarks, pontos_boca):
    dist_horizontal = distancia_euclidiana(landmarks[pontos_boca[0]], landmarks[pontos_boca[1]])
    dist_vertical = distancia_euclidiana(landmarks[pontos_boca[2]], landmarks[pontos_boca[3]])
    if dist_horizontal == 0: return 0.0
    mar = dist_vertical / dist_horizontal
    return mar
      

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
                time.sleep(0.2)
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
                olho_esquerdo = calcular_olho(results.multi_face_landmarks[0].landmark, PONTOS_OLHO_ESQUERDO)
                olho_direito = calcular_olho(results.multi_face_landmarks[0].landmark, PONTOS_OLHO_DIREITO)
                boca = calcular_boca(results.multi_face_landmarks[0].landmark, PONTOS_BOCA)
                
                if olho_esquerdo < LIMIAR_PISCADA:
                    if _estado_olho_esquerdo == 'aberto':
                        _estado_olho_esquerdo = 'fechado'
                        _executor.submit(pressionar_tecla, TECLA_OLHO_ESQUERDO_FECHADO)
                        cv2.putText(image, "Olho Esquerdo Fechado", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    if _estado_olho_esquerdo == 'fechado':
                        _estado_olho_esquerdo = 'aberto'
                        _executor.submit(soltar_tecla, TECLA_OLHO_ESQUERDO_FECHADO)
                
                if olho_direito < LIMIAR_PISCADA:
                    if _estado_olho_direito == 'aberto':
                        _estado_olho_direito = 'fechado'
                        _executor.submit(pressionar_tecla, TECLA_OLHO_DIREITO_FECHADO)
                        cv2.putText(image, "Olho Direito Fechado", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    if _estado_olho_direito == 'fechado':
                        _estado_olho_direito = 'aberto'
                        _executor.submit(soltar_tecla, TECLA_OLHO_DIREITO_FECHADO)
                        
                if boca > LIMIAR_BOCA_ABERTA:
                    if _estado_boca == 'fechada':
                        _estado_boca = 'aberta'
                        _executor.submit(pressionar_tecla, TECLA_BOCA_ABERTA)
                        cv2.putText(image, "Boca Aberta", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    if _estado_boca == 'aberta':
                        _estado_boca = 'fechada'
                        _executor.submit(soltar_tecla, TECLA_BOCA_ABERTA)
            
            time.sleep(0.05)
        except Exception as e:
            print(f"Ocorreu um erro ao processar a imagem: {e}")
            continue        
            
        detector = face_mesh_module.FaceMeshDetector(maxFaces=1)
        img, _ =  detector.findFaceMesh(image)
            
        cv2.imshow('Malha Facial com MediaPipe', img)
        cv2.waitKey(1)
        #if cv2.waitKey(5) & 0xFF == 27:
        #    print("Saindo do loop.")
        #    break # sai com esc
        # por algum motivo o código executa isso quando tem interação