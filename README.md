# DSL-HTML-PT 🇧🇷

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

### 1. Instale a dependência

O projeto usa apenas a biblioteca `lark` para fazer a análise sintática:

```bash
pip install lark
```

### 2. Salve o arquivo

Coloque o arquivo `dsl_html.py` em uma pasta qualquer no seu computador.

### 3. Escreva seu programa na DSL

Você pode editar um dos programas de teste que já existem no arquivo (`prog_elementos`, `prog_variaveis`, `prog_estilos`) ou escrever o seu próprio código, seguindo a sintaxe da linguagem. Exemplo simples:

```
pagina "Minha Página" {
    titulo 1 "Olá, mundo!" cor: "navy"
    paragrafo {
        "Este texto foi gerado pela minha "
        negrito "DSL"
        "!"
    }
}
```

### 4. Rode pelo terminal

Abra o terminal na pasta onde está o `dsl_html.py` e execute:

```bash
python dsl_html.py [elementos|variaveis|estilos|erro] [arquivo_saida.html]
```

- `elementos` — demonstra os elementos básicos da linguagem
- `variaveis` — demonstra variáveis, condicionais e repetição
- `estilos` — demonstra os modificadores de estilo CSS
- `erro` — demonstra a detecção de um erro semântico
- `arquivo_saida.html` (opcional) — salva o HTML gerado em um arquivo; se omitido, o resultado é apenas impresso no terminal

Exemplos:

```bash
python dsl_html.py variaveis
python dsl_html.py elementos
python dsl_html.py estilos
python dsl_html.py erro
```

Para gerar um arquivo `.html` de verdade, que você pode abrir direto no navegador:

```bash
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

with open("meu_site.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML gerado com sucesso!")
```

Basta rodar esse novo script (`python meu_script.py`) na mesma pasta onde está o `dsl_html.py`, e o arquivo `meu_site.html` será criado.

### Dica sobre erros

Se você cometer algum erro semântico — por exemplo, usar uma propriedade CSS que não existe (`destaque:` em vez de `cor:`) ou uma URL sem `http://`/`https://` — o compilador vai parar e mostrar uma mensagem explicando exatamente o que está errado, como no exemplo `erro` do próprio arquivo.

## 4 - Requisitos:

- Python 3.10+ (usa `match`/`case`)
- [`lark`](https://pypi.org/project/lark/)

```bash
pip install lark
```

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
