from concurrent.futures import ThreadPoolExecutor
import math
import os
import time

import cv2
import mediapipe as mp
import numpy as np 
from gtts import gTTS
from playsound import playsound

PONTOS_OLHO_ESQUERDO = [362, 385, 387, 263, 373, 380]
PONTOS_OLHO_DIREITO = [33, 160, 158, 133, 153, 144]
PONTOS_BOCA = [78, 308, 13, 14]

limiar_olho_direito = 0.15
limiar_olho_esquerdo = 0.1
limiar_boca_aberta = 0.2

teclado_layout = [
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'],
    ['U', 'V', 'W', 'X', 'Y', 'Z', ' ', '.', ',', '?'],
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['APAGAR', 'LIMPAR', 'FALAR']
]
cursor_pos = [0, 0]
frase_atual = ''

COOLDOWN_MOVIMENTO = 0.7
ultimo_movimento_tempo = 0

CONTADOR_BOCA_ABERTA = 0
selecao_ativada = False
boca_antes_aberta = False

malha_facial = mp.solutions.face_mesh
camera = cv2.VideoCapture(0)
executor = ThreadPoolExecutor(max_workers=2)

def falar_frase(frase):
    if not frase:
        print("Nenhuma frase para falar.")
        return
    
    try:
        tts = gTTS(text=frase, lang='pt-br')
        arquivo_audio = "fala.mp3"
        tts.save(arquivo_audio)
        playsound(arquivo_audio)
        os.remove(arquivo_audio)
    except Exception as e:
        print(f"Ocorreu um erro ao tentar falar a frase: {e}")

def manipular_selecao():
    global frase_atual
    selecao = teclado_layout[cursor_pos[0]][cursor_pos[1]]
    print(selecao)
    if selecao == 'APAGAR':
        frase_atual = frase_atual[:-1]
    elif selecao == 'LIMPAR':
        frase_atual = ''
    elif selecao == 'FALAR':
        executor.submit(falar_frase, frase_atual)
    else:
        frase_atual += selecao

def desenha_teclado(ui_canvas):
    ui_canvas.fill(0)
    cv2.rectangle(ui_canvas, (20, 10), (ui_canvas.shape[1] - 20, 60), (20, 20, 20), -1)
    cv2.putText(ui_canvas, frase_atual, (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    button_height, button_width = 50, 70
    start_x, start_y = 20, 80
    gap = 8

    for i, row in enumerate(teclado_layout):
        for j, key in enumerate(row):
            x = start_x + j * (button_width + gap)
            y = start_y + i * (button_height + gap)
            cor_fundo = (0, 255, 0) if i == cursor_pos[0] and j == cursor_pos[1] else (80, 80, 80)
            if key in ['APAGAR', 'LIMPAR']:
                cor_fundo = (0, 165, 255) if cor_fundo == (0, 255, 0) else (0, 80, 180)
            elif key == 'FALAR':
                cor_fundo = (0, 255, 0) if cor_fundo == (0, 255, 0) else (0, 150, 0)
            cv2.rectangle(ui_canvas, (x, y), (x + button_width, y + button_height), cor_fundo, -1)
            font_scale = 0.8 if len(key) <= 1 else 0.6
            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
            text_x = x + (button_width - text_size[0]) // 2
            text_y = y + (button_height + text_size[1]) // 2
            cv2.putText(ui_canvas, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

def distancia_euclidiana(ponto1, ponto2):
    return math.sqrt((ponto1.x - ponto2.x)**2 + (ponto1.y - ponto2.y)**2)

def calcular_aspect_ratio_olho(landmarks, pontos_olho):
    p2_p6 = distancia_euclidiana(landmarks[pontos_olho[1]], landmarks[pontos_olho[5]])
    p3_p5 = distancia_euclidiana(landmarks[pontos_olho[2]], landmarks[pontos_olho[4]])
    p1_p4 = distancia_euclidiana(landmarks[pontos_olho[0]], landmarks[pontos_olho[3]])
    return (p2_p6 + p3_p5) / (2.0 * p1_p4) if p1_p4 != 0 else 0.0

def calcular_aspect_ratio_boca(landmarks, pontos_boca):
    dist_horizontal = distancia_euclidiana(landmarks[pontos_boca[0]], landmarks[pontos_boca[1]])
    dist_vertical = distancia_euclidiana(landmarks[pontos_boca[2]], landmarks[pontos_boca[3]])
    return dist_vertical / dist_horizontal if dist_horizontal != 0 else 0.0

largura_tela, altura_tela = 800, 480
tela_teclado = np.zeros((altura_tela, largura_tela, 3), dtype=np.uint8)

with malha_facial.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    while camera.isOpened():
        success, image = camera.read()
        if not success:
            print("Ignorando frame vazio da câmera.")
            continue

        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            estado_olho_direito = calcular_aspect_ratio_olho(landmarks, PONTOS_OLHO_ESQUERDO)
            estado_olho_esquerdo = calcular_aspect_ratio_olho(landmarks, PONTOS_OLHO_DIREITO)
            estado_boca = calcular_aspect_ratio_boca(landmarks, PONTOS_BOCA)

            boca_aberta = estado_boca > limiar_boca_aberta
            olho_e_fechado = estado_olho_direito < limiar_olho_esquerdo
            olho_d_fechado = estado_olho_esquerdo < limiar_olho_direito

            apenas_direito = olho_d_fechado and not olho_e_fechado
            apenas_esquerdo = olho_e_fechado and not olho_d_fechado
            ambos_abertos = not olho_e_fechado and not olho_d_fechado
            tempo_atual = time.time()
            if boca_aberta and not boca_antes_aberta and ambos_abertos:
                print("Boca aberta detectada.")
                CONTADOR_BOCA_ABERTA += 1
                boca_antes_aberta = True
                
                if CONTADOR_BOCA_ABERTA == 2:
                    CONTADOR_BOCA_ABERTA = 0
                    manipular_selecao()

            if not boca_aberta:
                boca_antes_aberta = False
                selecao_ativada = False
                

            if tempo_atual - ultimo_movimento_tempo > COOLDOWN_MOVIMENTO:
                if not boca_aberta:
                    if apenas_direito:
                        CONTADOR_BOCA_ABERTA = 0
                        cursor_pos[1] = (cursor_pos[1] + 1) % len(teclado_layout[cursor_pos[0]])
                        ultimo_movimento_tempo = tempo_atual
                    elif apenas_esquerdo:
                        CONTADOR_BOCA_ABERTA = 0
                        
                        
                        cursor_pos[1] = (cursor_pos[1] - 1 + len(teclado_layout[cursor_pos[0]])) % len(teclado_layout[cursor_pos[0]])
                        ultimo_movimento_tempo = tempo_atual
                else:
                    if apenas_direito:
                        CONTADOR_BOCA_ABERTA = 0
                        cursor_pos[0] = (cursor_pos[0] + 1) % len(teclado_layout)
                        cursor_pos[1] = min(cursor_pos[1], len(teclado_layout[cursor_pos[0]]) - 1)
                        ultimo_movimento_tempo = tempo_atual
                    elif apenas_esquerdo:
                        CONTADOR_BOCA_ABERTA = 0
                        cursor_pos[0] = (cursor_pos[0] - 1 + len(teclado_layout)) % len(teclado_layout)
                        cursor_pos[1] = min(cursor_pos[1], len(teclado_layout[cursor_pos[0]]) - 1)
                        ultimo_movimento_tempo = tempo_atual

        desenha_teclado(tela_teclado)
        cv2.imshow('Teclado Virtual por Gestos Faciais', tela_teclado)

        if cv2.waitKey(5) & 0xFF == 27:  # ESC
            break

camera.release()
cv2.destroyAllWindows()
