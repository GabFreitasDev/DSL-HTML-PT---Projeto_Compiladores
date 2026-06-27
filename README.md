# DSL-HTML-PT BR

Uma **linguagem de domínio específico (DSL)** em português que compila para HTML, construída em Python com [Lark](https://github.com/lark-parser/lark).

Inspirada no pipeline clássico de compiladores (análise sintática → análise semântica → geração de código), o projeto permite escrever páginas web usando uma sintaxe declarativa e legível em português, sem precisar tocar em uma única tag HTML.

```
pagina "Meu Site" {
    titulo 1 "Olá, mundo!" cor: "navy" alinhamento: "center"

    paragrafo {
        "Escrito em "
        negrito "português"
        " e compilado para HTML."
    }

    link "Veja no GitHub" -> "https://github.com"
}
```

## 1 - Funcionalidades:

- **Elementos HTML completos**: títulos (`h1`–`h6`), parágrafos, listas, links, imagens, botões e tabelas
- **Variáveis**: declare valores com `var nome = "valor"` e reutilize em qualquer lugar do código
- **Condicionais**: blocos `se` / `senao` avaliados em tempo de compilação
- **Repetição**: blocos `para ... em [...]` para gerar elementos repetidos a partir de uma lista
- **Estilização CSS**: modificadores como `cor:`, `fundo:`, `alinhamento:`, `tamanho:`, `margem:`, `borda:`, entre outros
- **Validação semântica**: mensagens de erro claras para propriedades CSS inválidas, URLs malformadas e variáveis desconhecidas

## 2 - Como funciona:

O compilador segue três fases bem definidas:

1. **Análise Sintática** — a gramática (definida com Lark, parser LALR) transforma o código-fonte em uma Árvore Sintática Abstrata (AST)
2. **Análise Semântica** — percorre a árvore validando regras (propriedades CSS, URLs, variáveis) e decorando cada nó com os atributos que a próxima fase vai precisar
3. **Geração de HTML** — percorre a árvore já decorada e emite o HTML final, pronto para uso

## 3 - Como usar:

### 1. Clone o repositório

```bash
git clone https://github.com/GabFreitasDev/DSL-HTML-PT---Projeto_Compiladores.git
cd DSL-HTML-PT---Projeto_Compiladores
```

### 2. Crie o ambiente virtual e instale a dependência

O projeto usa apenas a biblioteca `lark` para fazer a análise sintática. Como muitos sistemas não permitem instalar pacotes Python globalmente via `pip`, recomenda-se usar um ambiente virtual:

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install lark
```

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install lark
```

> **Erro no PowerShell?** Se aparecer "running scripts is disabled on this system", o Windows está bloqueando a execução de scripts `.ps1` por padrão. Roda esse comando uma vez no PowerShell e resolve:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Outra opção é usar o **cmd.exe** no lugar do PowerShell — lá não tem essa restrição.

Nas próximas vezes que abrir o terminal, basta ativar o ambiente antes de rodar o projeto.

### 3. Escreva seu programa na DSL

Crie um novo arquivo `.py` na mesma pasta do `dsl_html.py` e use a função `compilar` para escrever seu próprio código na DSL — o passo **"5. Usar com seu próprio código"** logo abaixo tem um exemplo completo. A referência de sintaxe está na seção **"5 - Sintaxe da linguagem"** do documento.

### 4. Rode pelo terminal

Antes de qualquer coisa, lembra de ativar o ambiente virtual (se ainda não fez):

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

Aí é só rodar um dos quatro programas de exemplo:

```
python dsl_html.py elementos   # elementos básicos da linguagem
python dsl_html.py variaveis   # variáveis, condicionais e repetição
python dsl_html.py estilos     # modificadores de estilo CSS
python dsl_html.py erro        # erro semântico detectado pelo compilador
```

Para gerar um arquivo `.html` de verdade, que você pode abrir direto no navegador:

```
python dsl_html.py variaveis saida.html
```

### 5. Usar com seu próprio código (forma mais útil)

Para compilar **o seu próprio texto na DSL**, em vez de usar os exemplos prontos, importe a função `compilar` em outro script Python:

```python
from dsl_html import compilar

meu_codigo = """
pagina "Meu Site" {
    titulo 1 "Bem-vindo!"
    paragrafo {
        "Compilado com minha própria DSL."
    }
}
"""

html = compilar(meu_codigo)

with open("saida.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML gerado com sucesso!")
```

Salve esse código em um arquivo chamado `meu_script.py` na mesma pasta do `dsl_html.py` e rode:

```
python meu_script.py
```

O arquivo `saida.html` será criado na mesma pasta.

### Dica sobre erros

Se você cometer algum erro semântico — por exemplo, usar uma propriedade CSS que não existe (`destaque:` em vez de `cor:`) ou uma URL sem `http://`/`https://` — o compilador vai parar e mostrar uma mensagem explicando exatamente o que está errado, como no exemplo `erro` do próprio arquivo.

## 4 - Requisitos:

- Python 3.10+ (usa `match`/`case`)
- [`lark`](https://pypi.org/project/lark/) — instale dentro de um ambiente virtual (veja seção 3.2)

## 5 - Sintaxe da linguagem:

| Construção | Exemplo |
|---|---|
| Página | `pagina "Título" { ... }` |
| Variável | `var nome = "Felipe"` |
| Título | `titulo 1 "Texto"` ou `titulo 2 nome` |
| Parágrafo | `paragrafo { "texto" negrito "forte" italico "itálico" }` |
| Lista | `lista { item "A" item "B" }` |
| Link | `link "Texto" -> "https://..."` |
| Imagem | `imagem "Alt" <- "caminho.png"` |
| Botão | `botao "Texto"` |
| Tabela | `tabela { linha { "A" "B" } }` |
| Condicional | `se var == "valor" { ... } senao { ... }` |
| Repetição | `para item em ["A" "B" "C"] { ... }` |
| Estilo | `cor: "navy"`, `fundo: "white"`, `alinhamento: "center"`, etc. |

## 6 - Contexto:

Projeto desenvolvido como exercício de construção de compiladores, aplicando os conceitos de análise léxica, sintática e semântica em uma linguagem com propósito prático e didático. O projeto foi desenvolvido pelos alunos Bruno Alberto, Felipe Stéffano, Gabriel de Freitas e Lucas Leite como projeto prático da disciplina de Compiladores do professor Luis Carlos.

## 7 - Licença:

Este projeto está disponível sob a licença MIT.
