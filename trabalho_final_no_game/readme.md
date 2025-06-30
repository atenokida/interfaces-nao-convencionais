# Interface Facial para teclado para converter texto em voz através de movimentos faciais 

## Sobre
Projeto desenvolvido para a disciplina de Interfaces Não Convencionais (2025/1) do Bacharelado em Ciência da Computação da UTFPR-CM.  

Esta aplicação permite controlar um teclado virtual utilizando **movimentos faciais**, convertendo texto em voz. O sistema utiliza **detecção de piscadas e detecção de abertura da boca** para navegação e seleção de teclas.


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
    python main.py

## Mapeamento padrão
  * Mover para direita: olho direito
  * Mover para esquerda: olho esquerdo
  * Mover para cima: Boca aberta + olho esquerdo
  * Mover para baixo: Boca aberta + olho direito
  * Selecionar uma tecla: Abrir a boca duas vezes



# Instalar Python 3.10.14 via pyenv
```python
pyenv install 3.10.14
```
```python
pyenv shell 3.10.14
```

## Adicionar ao .zshrc

Adicione as seguintes linhas ao final do seu ~/.zshrc:
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
```
## Depois, aplique as alterações com:
```bash
source ~/.zshrc
```
