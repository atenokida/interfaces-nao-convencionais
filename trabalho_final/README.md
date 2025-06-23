# Interface Facial para Jogos de Plataforma

## Sobre
Projeto desenvolvido para a disciplina de Interfaces Não Convencionais (2025/1) do Bacharelado em Ciência da Computação da UTFPR-CM.  

Permite controlar jogos de plataforma simples (e.g. Super Mario) usando expressões faciais. Piscar com os olhos ou abrir a boca aciona teclas específicas, substituindo o uso convencional do clique de botões.

## Como Executar
### Pré-requisitos
 * Python v3.10.14+
 * Webcam funcional
 * Utilitários para simular cliques:
   - (LINUX) `wtype`.

### 1. Crie e ative um ambiente virtual
    # Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate

### 2. Instale as dependências
    pip install -r requirements.txt

### 3. Execute o script
    python mascara.py

## Mapeamento padrão
  * Olho esquerdo fechado &rarr; Tecla `a`
  * Olho direito fechado &rarr; Tecla `d`
  * Boca aberta &rarr; Tecla `w`