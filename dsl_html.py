import copy
from lark import Lark

# DSL HTML-PT — linguagem em português que compila para HTML.
#
# Pipeline de três fases (igual ao compilador IMP da disciplina):
#   1. analisador.parse(codigo)   → constrói a Árvore Sintática (AST)
#   2. analiseSemantica(arvore)   → valida e decora cada nó
#   3. geraHTML(arvore)           → emite o HTML lendo os atributos


# =============================================================
# FASE 1 — GRAMÁTICA
# =============================================================
# Convenções da notação Lark:
#   MAIÚSCULAS  → token léxico (palavra, número, string entre aspas)
#   minúsculas  → regra sintática
#   "texto"     → palavra reservada (keyword)
#   ?regra      → transparente: o filho sobe direto ao pai
#   -> nome     → renomeia o nó; aparece no match/case das fases seguintes

GRAMATICA = r"""
?start : programa

# Raiz obrigatória: todo programa começa com "pagina".
# O título entre aspas é opcional (note o STRING?).
# Dentro das chaves: declarações de variáveis e elementos HTML.
programa : "pagina" STRING? "{" (var_decl | elemento)* "}" -> pagina

# '?elemento' é transparente: ao encontrar um título, a árvore
# terá diretamente um nó 'titulo', não um nó 'elemento' com filho 'titulo'.
?elemento : titulo | paragrafo | lista | link | imagem | botao | tabela
          | se_bloco | para_bloco

# NIVEL aceita apenas os dígitos 1 a 6, gerando <h1> a <h6>.
# O texto pode ser uma string literal OU o nome de uma variável.
titulo    : "titulo" NIVEL (STRING | VAR_NOME) estilo*       -> titulo
paragrafo : "paragrafo" "{" conteudo* "}" estilo*            -> paragrafo

# '?conteudo' também é transparente: os filhos do parágrafo chegam
# diretamente ao nó 'paragrafo', sem nível intermediário.
# Os nomes c_texto, c_variavel etc. distinguem o tipo de conteúdo
# no match/case da fase semântica.
?conteudo : STRING                        -> c_texto
          | VAR_NOME                      -> c_variavel
          | "negrito" (STRING | VAR_NOME) -> c_negrito
          | "italico" (STRING | VAR_NOME) -> c_italico

lista : "lista" "{" item* "}" estilo*  -> lista
item  : "item"  (STRING | VAR_NOME)    -> item

# A seta indica a direção do fluxo de informação:
#   link:   texto clicável  ->  destino (URL)
#   imagem: texto alternativo  <-  origem (arquivo)
link   : "link"   (STRING | VAR_NOME) "->" STRING estilo* -> link
imagem : "imagem" (STRING | VAR_NOME) "<-" STRING estilo* -> imagem
botao  : "botao"  (STRING | VAR_NOME) estilo*             -> botao

tabela : "tabela" "{" linha* "}" estilo* -> tabela
linha  : "linha"  "{" (STRING | VAR_NOME)* "}"            -> linha

# Declaração de variável: var nome = "valor"
# O valor é sempre uma string — resolução em tempo de compilação.
var_decl : "var" VAR_NOME "=" STRING -> var_decl

# Condicional: compara uma variável com um literal.
# O bloco "senao" é opcional — note o uso de [...] para isso.
se_bloco    : "se" VAR_NOME "==" STRING bloco_se ["senao" bloco_senao] -> se_bloco
bloco_se    : "{" elemento* "}" -> bloco_se
bloco_senao : "{" elemento* "}" -> bloco_senao

# Repetição: itera sobre uma lista de strings fornecida diretamente.
# A variável de iteração (ex: "tech") assume cada valor da lista.
para_bloco    : "para" VAR_NOME "em" lista_valores bloco_para -> para_bloco
lista_valores : "[" STRING+ "]"   -> lista_valores
bloco_para    : "{" elemento* "}" -> bloco_para

# Modificadores de estilo CSS — opcionais, vêm após o conteúdo:
#   titulo 1 "Olá" cor: "navy" alinhamento: "center"
estilo : PROP ":" STRING -> estilo

# ── Tokens léxicos ───────────────────────────────────────────
STRING   : /"[^"]*"/
NIVEL    : /[1-6]/
VAR_NOME : /[a-záéíóúãõâêîôûàèìòùç_][a-záéíóúãõâêîôûàèìòùç_0-9]*/

# PROP aceita qualquer palavra; a validação dos nomes válidos
# fica na fase semântica, onde a mensagem de erro é mais clara.
PROP     : /[a-záéíóúãõâêîôûàèìòùç]+/

%ignore /[ \n\r\t]+/
%ignore /#[^\n]*/
"""

# LALR em vez de Earley (o padrão do Lark): o Earley usa léxico
# dinâmico e pode tokenizar "negrito" como VAR_NOME. Com LALR o
# léxico é estático e as palavras-chave sempre têm prioridade.
analisador = Lark(GRAMATICA, parser="lalr")


# =============================================================
# FASE 2 — ANÁLISE SEMÂNTICA
# =============================================================
# Valida o programa e decora cada nó com atributos já calculados.
# A Fase 3 só precisa ler esses atributos, sem olhar para os filhos.
#
# Atributos decorados:
#   tree.titulo_pagina, tree.nivel, tree.texto_limpo,
#   tree.url_limpa, tree.src_limpa, tree.celulas,
#   tree.style, tree.ramo_ativo, tree.expansoes

# Tabela de tradução: nome em português → propriedade CSS real.
# Aqui fazemos a validação que o léxico não faz: se o nome não
# estiver neste dicionário, rejeitamos com mensagem explicativa.
CSS_PROPS = {
    "cor":           "color",
    "fundo":         "background-color",
    "alinhamento":   "text-align",
    "tamanho":       "font-size",
    "margem":        "margin",
    "borda":         "border",
    "preenchimento": "padding",
    "largura":       "width",
    "altura":        "height",
}

# Tabela de símbolos: nome → valor de cada variável declarada.
declaracoes = {}


def resolverTexto(token, escopo):
    # STRING → remove as aspas; VAR_NOME → busca o valor no escopo.
    s = str(token)
    return s[1:-1] if token.type == "STRING" else escopo.get(s, s)


def coletarStyle(tree):
    # Coleta os nós "estilo" e monta a string CSS para tree.style.
    partes = []
    for f in tree.children:
        if hasattr(f, "data") and f.data == "estilo":
            prop = str(f.children[0])
            if prop not in CSS_PROPS:
                raise Exception(
                    f"Propriedade CSS desconhecida: '{prop}'.\n"
                    f"Disponíveis: {', '.join(sorted(CSS_PROPS))}."
                )
            partes.append(f"{CSS_PROPS[prop]}: {str(f.children[1])[1:-1]}")
    tree.style = "; ".join(partes)


def analiseSemantica(tree, escopo=None):
    global declaracoes
    if escopo is None:
        escopo = declaracoes

    match tree.data:

        case "pagina":
            declaracoes = {}  # reinicia para cada nova compilação

            # Extrai o título da página, se fornecido.
            # O título é o primeiro filho do tipo STRING (token folha).
            tree.titulo_pagina = "Página Gerada pela DSL"
            for filho in tree.children:
                if hasattr(filho, "type") and filho.type == "STRING":
                    tree.titulo_pagina = str(filho)[1:-1]
                    break

            # Dois passes: coleta todas as variáveis primeiro e depois
            # processa os elementos. Assim uma variável pode ser usada
            # antes de ser declarada no arquivo.
            for filho in tree.children:
                if hasattr(filho, "data") and filho.data == "var_decl":
                    analiseSemantica(filho, declaracoes)
            for filho in tree.children:
                if hasattr(filho, "data") and filho.data != "var_decl":
                    analiseSemantica(filho, declaracoes)

        case "var_decl":
            # Registra a variável na tabela de símbolos.
            # children[0] = nome (VAR_NOME), children[1] = valor (STRING).
            escopo[str(tree.children[0])] = str(tree.children[1])[1:-1]

        case "titulo":
            # Converte NIVEL de token (string) para int.
            tree.nivel = int(str(tree.children[0]))
            tree.texto_limpo = resolverTexto(tree.children[1], escopo)
            coletarStyle(tree)

        case "paragrafo":
            # Decora os filhos de conteúdo recursivamente,
            # ignorando os nós 'estilo' (tratados por coletarStyle).
            for filho in tree.children:
                if hasattr(filho, "data") and filho.data != "estilo":
                    analiseSemantica(filho, escopo)
            coletarStyle(tree)

        case "c_texto":
            # Conteúdo literal: apenas remove as aspas.
            tree.texto_limpo = str(tree.children[0])[1:-1]

        case "c_variavel":
            # Conteúdo variável: resolve para o valor declarado.
            # Se a variável não foi declarada, usa o próprio nome
            # como fallback (comportamento permissivo).
            tree.texto_limpo = escopo.get(str(tree.children[0]), str(tree.children[0]))

        case "c_negrito":
            tree.texto_limpo = resolverTexto(tree.children[0], escopo)

        case "c_italico":
            tree.texto_limpo = resolverTexto(tree.children[0], escopo)

        case "lista":
            for filho in tree.children:
                if hasattr(filho, "data") and filho.data == "item":
                    analiseSemantica(filho, escopo)
            coletarStyle(tree)

        case "item":
            tree.texto_limpo = resolverTexto(tree.children[0], escopo)

        case "link":
            tree.texto_limpo = resolverTexto(tree.children[0], escopo)
            url = str(tree.children[1])[1:-1]
            # Valida se a URL começa com http:// ou https://.
            if not (url.startswith("http://") or url.startswith("https://")):
                raise Exception(
                    f"URL inválida: '{url}'.\n"
                    "A URL deve começar com 'http://' ou 'https://'."
                )
            tree.url_limpa = url
            coletarStyle(tree)

        case "imagem":
            tree.texto_limpo = resolverTexto(tree.children[0], escopo)
            tree.src_limpa = str(tree.children[1])[1:-1]
            coletarStyle(tree)

        case "botao":
            tree.texto_limpo = resolverTexto(tree.children[0], escopo)
            coletarStyle(tree)

        case "tabela":
            for filho in tree.children:
                if hasattr(filho, "data") and filho.data == "linha":
                    analiseSemantica(filho, escopo)
            coletarStyle(tree)

        case "linha":
            # Resolve todas as células de uma vez e guarda como lista.
            # A Fase 3 itera sobre tree.celulas sem tocar nos filhos.
            tree.celulas = [
                resolverTexto(c, escopo)
                for c in tree.children
                if hasattr(c, "type")
            ]

        case "se_bloco":
            nome_var = str(tree.children[0])
            valor_esperado = str(tree.children[1])[1:-1]
            bloco_v = next((c for c in tree.children if hasattr(c, "data") and c.data == "bloco_se"), None)
            bloco_f = next((c for c in tree.children if hasattr(c, "data") and c.data == "bloco_senao"), None)

            # Avalia a condição agora, em tempo de compilação.
            # Guarda o ramo correto em ramo_ativo; o outro é descartado.
            tree.ramo_ativo = bloco_v if escopo.get(nome_var, "") == valor_esperado else bloco_f
            if tree.ramo_ativo:
                for elem in tree.ramo_ativo.children:
                    if hasattr(elem, "data"):
                        analiseSemantica(elem, escopo)

        case "para_bloco":
            var_iter = str(tree.children[0])
            lista_v = next(c for c in tree.children if hasattr(c, "data") and c.data == "lista_valores")
            bloco_p = next(c for c in tree.children if hasattr(c, "data") and c.data == "bloco_para")
            valores = [str(s)[1:-1] for s in lista_v.children if hasattr(s, "type")]

            # deepcopy: sem cópia, decorar o mesmo nó em iterações
            # diferentes sobrescreveria os atributos da iteração anterior.
            # Cada cópia recebe o escopo com o valor atual da variável.
            tree.expansoes = []
            for valor in valores:
                escopo_local = {**escopo, var_iter: valor}
                expansao = []
                for elem in bloco_p.children:
                    if hasattr(elem, "data"):
                        copia = copy.deepcopy(elem)
                        analiseSemantica(copia, escopo_local)
                        expansao.append(copia)
                tree.expansoes.append(expansao)

        case "estilo":
            pass  # tratado por coletarStyle no nó pai


# =============================================================
# FASE 3 — GERAÇÃO DE HTML
# =============================================================
# Percorre a árvore lendo os atributos decorados pela Fase 2.
# 'ind' acumula espaços para indentar o HTML de saída.

def geraHTML(tree, ind=""):
    match tree.data:

        case "pagina":
            # Gera os filhos recursivamente, pulando var_decl
            # (variáveis não viram HTML — já foram resolvidas).
            corpo = "".join(
                geraHTML(f, ind + "  ")
                for f in tree.children
                if hasattr(f, "data") and f.data != "var_decl"
            )
            # Emite o esqueleto completo de um documento HTML5.
            # tree.titulo_pagina foi decorado na Fase 2.
            return (
                "<!DOCTYPE html>\n"
                '<html lang="pt-BR">\n'
                "<head>\n"
                '  <meta charset="UTF-8">\n'
                f"  <title>{tree.titulo_pagina}</title>\n"
                "</head>\n"
                "<body>\n"
                f"{corpo}"
                "</body>\n"
                "</html>\n"
            )

        case "titulo":
            # tree.nivel (int) e tree.texto_limpo (string) foram
            # calculados na Fase 2 — aqui só montamos a tag.
            s = f' style="{tree.style}"' if tree.style else ""
            return f"{ind}<h{tree.nivel}{s}>{tree.texto_limpo}</h{tree.nivel}>\n"

        case "paragrafo":
            s = f' style="{tree.style}"' if tree.style else ""
            corpo = "".join(
                geraHTML(f, ind + "  ")
                for f in tree.children
                if hasattr(f, "data") and f.data != "estilo"
            )
            return f"{ind}<p{s}>\n{corpo}{ind}</p>\n"

        case "c_texto" | "c_variavel":
            # Ambos chegam aqui com tree.texto_limpo já resolvido.
            return f"{ind}{tree.texto_limpo}\n"

        case "c_negrito":
            return f"{ind}<strong>{tree.texto_limpo}</strong>\n"

        case "c_italico":
            return f"{ind}<em>{tree.texto_limpo}</em>\n"

        case "lista":
            s = f' style="{tree.style}"' if tree.style else ""
            itens = "".join(
                geraHTML(f, ind + "  ")
                for f in tree.children
                if hasattr(f, "data") and f.data == "item"
            )
            return f"{ind}<ul{s}>\n{itens}{ind}</ul>\n"

        case "item":
            return f"{ind}<li>{tree.texto_limpo}</li>\n"

        case "link":
            s = f' style="{tree.style}"' if tree.style else ""
            return f'{ind}<a href="{tree.url_limpa}"{s}>{tree.texto_limpo}</a>\n'

        case "imagem":
            s = f' style="{tree.style}"' if tree.style else ""
            return f'{ind}<img src="{tree.src_limpa}" alt="{tree.texto_limpo}"{s}>\n'

        case "botao":
            s = f' style="{tree.style}"' if tree.style else ""
            return f"{ind}<button{s}>{tree.texto_limpo}</button>\n"

        case "tabela":
            s = f' style="{tree.style}"' if tree.style else ""
            linhas = "".join(
                geraHTML(f, ind + "  ")
                for f in tree.children
                if hasattr(f, "data") and f.data == "linha"
            )
            return f"{ind}<table{s}>\n{linhas}{ind}</table>\n"

        case "linha":
            # tree.celulas já é uma lista de strings resolvidas.
            celulas = "".join(f"{ind}  <td>{c}</td>\n" for c in tree.celulas)
            return f"{ind}<tr>\n{celulas}{ind}</tr>\n"

        case "se_bloco":
            # tree.ramo_ativo é None se a condição foi falsa e não
            # havia bloco "senao". Neste caso, não geramos nada.
            if tree.ramo_ativo is None:
                return ""
            return "".join(
                geraHTML(e, ind)
                for e in tree.ramo_ativo.children
                if hasattr(e, "data")
            )

        case "para_bloco":
            # tree.expansoes é uma lista de listas de nós decorados.
            # Cada grupo corresponde a uma iteração já resolvida.
            return "".join(
                geraHTML(elem, ind)
                for expansao in tree.expansoes
                for elem in expansao
            )

        case "var_decl" | "estilo":
            return ""  # não geram HTML diretamente

    raise Exception(f"Nó desconhecido na geração: '{tree.data}'")


def compilar(codigo):
    # Ponto de entrada para uso externo: executa as três fases
    # em sequência e retorna o HTML como string.
    arvore = analisador.parse(codigo)
    analiseSemantica(arvore)
    return geraHTML(arvore)


# =============================================================
# PROGRAMAS DE TESTE
# =============================================================
# Execute com: python dsl_html.py [elementos|variaveis|estilos|erro]

# Demonstra: todos os elementos básicos da linguagem
prog_elementos = """
pagina "Elementos Básicos" {
    titulo 1 "Bem-vindo à DSL HTML-PT"
    titulo 2 "Sobre esta linguagem"

    paragrafo {
        "Esta DSL foi feita em "
        negrito "Python"
        " com a biblioteca "
        italico "Lark"
        "."
    }

    lista {
        item "Títulos de nível 1 a 6"
        item "Parágrafos com negrito e itálico"
        item "Links, imagens e botões"
        item "Tabelas com múltiplas colunas"
    }

    link "Documentação do Lark" -> "https://lark-parser.readthedocs.io"
    botao "Começar"
}
"""

# Demonstra: variáveis, condicional e repetição
prog_variaveis = """
pagina "Portfólio de Felipe" {
    var nome       = "Felipe"
    var cargo      = "Desenvolvedor Python"
    var disponivel = "sim"

    titulo 1 nome alinhamento: "center" cor: "navy"

    paragrafo {
        "Cargo: "
        negrito cargo
    } alinhamento: "center"

    se disponivel == "sim" {
        titulo 2 "Status" cor: "darkgreen"
        paragrafo { negrito "Disponível" " para novos projetos!" }
    } senao {
        titulo 2 "Status"
        paragrafo { "Indisponível no momento." }
    }

    titulo 2 "Tecnologias"
    para tech em ["Python" "HTML" "CSS" "Lark" "Git"] {
        botao tech fundo: "steelblue" cor: "white" margem: "4px"
    }

    tabela {
        linha { "Nome" "Cargo" }
        linha { nome   cargo   }
    } borda: "1px solid #ccc"

    link "Ver projetos" -> "https://github.com" fundo: "darkblue" cor: "white"
    botao "Enviar mensagem" fundo: "green" cor: "white" margem: "8px"
}
"""

# Demonstra: modificadores de estilo CSS em todos os elementos
prog_estilos = """
pagina "Galeria de Estilos" {
    titulo 1 "Cores e Estilos" cor: "white" fundo: "navy" alinhamento: "center"
    titulo 3 "Subtítulo menor" cor: "gray" tamanho: "14px"

    paragrafo {
        "Texto normal com "
        negrito "destaque em negrito"
        " e continuação."
    } fundo: "lightyellow" margem: "16px"

    lista {
        item "Item da lista"
    } borda: "2px solid navy" preenchimento: "8px"

    botao "Ação Principal"   cor: "white" fundo: "crimson" tamanho: "18px"
    botao "Ação Secundária"  cor: "white" fundo: "gray"
}
"""

# Demonstra: erro semântico detectado com mensagem clara.
# 'destaque' é sintaticamente válido (PROP aceita qualquer palavra),
# mas a Fase 2 rejeita com a lista das propriedades disponíveis.
prog_erro = """
pagina "Teste de Erro" {
    titulo 1 "Olá" destaque: "amarelo"
}
"""

if __name__ == "__main__":
    import sys

    programas = {
        "elementos": prog_elementos,
        "variaveis": prog_variaveis,
        "estilos":   prog_estilos,
    }

    nome    = sys.argv[1] if len(sys.argv) > 1 else "variaveis"
    arquivo = sys.argv[2] if len(sys.argv) > 2 else None

    if nome == "erro":
        print("--- TESTANDO ERRO SEMÂNTICO ---")
        try:
            compilar(prog_erro)
        except Exception as e:
            print(f"Erro capturado corretamente:\n{e}")
        sys.exit(0)

    if nome not in programas:
        print(f"Programas disponíveis: {', '.join(programas)}, erro", file=sys.stderr)
        sys.exit(1)

    codigo = programas[nome]

    print("--- 1. ANÁLISE SINTÁTICA ---")
    arvore = analisador.parse(codigo)
    # Descomente a linha abaixo para ver a árvore crua gerada pelo Lark:
    # print(arvore.pretty())

    print("\n--- 2. ANÁLISE SEMÂNTICA ---")
    analiseSemantica(arvore)
    print("Árvore decorada com sucesso.")

    html = geraHTML(arvore)

    print("\n--- 3. HTML GERADO ---\n")
    if arquivo:
        import os
        pasta = os.path.dirname(arquivo)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Salvo em '{arquivo}'.")
    else:
        print(html)
