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
    python main.py

## Mapeamento padrão
  * Olho esquerdo fechado &rarr; Tecla `a`
  * Olho direito fechado &rarr; Tecla `d`
  * Boca aberta &rarr; Tecla `w`



pyenv install 3.10.14
Instalar a versão do python que roda as dependências do projeto
pyenv shell 3.10.14


adicionar esse código ao /.zshrc
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
```
source ~/.zshrc