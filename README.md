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

### 3.1 - Como script:

```bash
python dsl_html.py [elementos|variaveis|estilos|erro] [arquivo_saida.html]
```

- `elementos` — demonstra os elementos básicos da linguagem
- `variaveis` — demonstra variáveis, condicionais e repetição
- `estilos` — demonstra os modificadores de estilo CSS
- `erro` — demonstra a detecção de um erro semântico
- `arquivo_saida.html` (opcional) — salva o HTML gerado em um arquivo; se omitido, imprime no terminal

### 3.2 - Como módulo:

```python
from dsl_html import compilar

codigo = '''
pagina "Exemplo" {
    titulo 1 "Funciona!"
}
'''

html = compilar(codigo)
print(html)
```

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
