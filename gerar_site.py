# GERADOR DO SITE pendragonkids.com
#
# Por que um gerador e não treze arquivos escritos à mão: as páginas de herói
# são a mesma página com dados diferentes. Escrever à mão garante que uma delas
# vai ficar desatualizada — e são justamente elas o destino dos pins.
#
# O que o site resolve, e é por isso que ele existe:
#   1. o Activity Pack ganha endereço fixo  -> o [DOWNLOAD_LINK] do e-mail de
#      boas-vindas deixa de ser um buraco;
#   2. cada herói ganha a SUA página        -> os 14 pins do Pinterest passam a
#      ter destino específico, que é a regra (pin nunca aponta para a home);
#   3. deixa de depender de Amazon e Instagram, que são terra alugada.
#
# REGRAS DURAS obedecidas aqui (ver BASE_DE_FAS_KIDS.md):
#   - toda a comunicação é dirigida ao ADULTO, nunca à criança;
#   - nenhum campo pede nome, idade, foto ou escola de menor;
#   - a inscrição aponta para a página do Beehiiv que já está no ar, em vez de
#     uma segunda chave de API e uma segunda Function para manter.
#
# O QUE NÃO ESTÁ AQUI, DE PROPÓSITO: as 32 páginas do livro não viram brinde.
# Só as 5 folhas que já são do pacote gratuito (Arthur, Merlin, Aine, Bors,
# Percival) são oferecidas avulsas. Dar 9 das 32 páginas seria entregar 28% do
# livro de graça — decisão comercial do autor, não minha.
import hashlib
import pathlib
import shutil
from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent
PROJETO = RAIZ.parent
FICHAS = PROJETO / "characters" / "source"
PACK = PROJETO / "LEAD_MAGNET"
SAIDA = RAIZ / "public"

SITE = "https://pendragonkids.com"
BEEHIIV = "https://pendragons-newsletter.beehiiv.com"
# Para onde o formulário de inscrição envia. É o mesmo endereço que a própria
# página do beehiiv usa. Se um dia for criado um "embed" no painel do beehiiv,
# troca-se só esta linha — e o formulário vira um <iframe> do embed.
BEEHIIV_ENVIO = f"{BEEHIIV}/create"
AMAZON = "https://a.co/d/0hpAodfu"
INSTAGRAM = "https://www.instagram.com/pendragonkids/"
TIKTOK = "https://www.tiktok.com/@pendragonkids"
YOUTUBE = "https://www.youtube.com/@PendragonKids"
GRUPO_FB = "https://www.facebook.com/groups/1809831846819777"

# Cânone fixado (ver memória pendragon-kids-operacao). NÃO inventar traço novo.
HEROIS = [
    ("percival", "Percival", 8,
     "The forest boy. He walks barefoot, carries a wooden staff, and a badger "
     "follows him everywhere.", "his badger", True),
    ("aine", "Aine", 9,
     "She comes from the sea coast. Her harp goes where she goes, and a spiral "
     "shell hangs at her throat.", "her harp", True),
    ("arthur", "Arthur", 10,
     "The boy with the wooden sword. A short red cloak, a bronze dragon brooch, "
     "and a grin that starts trouble.", "the dragon brooch", True),
    ("kay", "Kay", 11,
     "The older brother. Lean, quick, impatient — and the first one to stand in "
     "front of you when something goes wrong.", "his practice sword", False),
    ("lancelot", "Lancelot", 12,
     "He arrived from far away and already fights better than anyone. A white "
     "swan on his chest and a grin he cannot hide.", "the white swan", False),
    ("bors", "Bors", 12,
     "The strongest of them all. Calm, steady, and the one who lifts what "
     "nobody else can.", "his square shield", True),
    ("gawain", "Gawain", 13,
     "The tallest and the loudest laugh. He carries a round shield with a sun "
     "painted on it.", "the sun shield", False),
    ("bedivere", "Bedivere", 13,
     "The quiet one. He stands very straight, holds a sheathed sword he never "
     "draws, and watches the door.", "the sword he never draws", False),
    ("merlin", "Merlin", None,
     "The old wizard. Long white beard, a pointed hat that flops at the tip, "
     "and a bowl of herbs at his belt.", "his gnarled staff", True),
]

# Qual folha avulsa cada herói oferece (só as que JÁ são do pacote gratuito)
FOLHA_AVULSA = {
    "arthur": "pack_01_color_arthur.png",
    "merlin": "pack_02_color_merlin.png",
    "aine": "pack_03_color_aine.png",
    "bors": "pack_04_color_bors.png",
    "percival": "pack_05_color_percival.png",
}

# O Cloudflare serve o CSS com max-age de 4 horas. Sem carimbo, o visitante
# recebe HTML novo com folha de estilo velha — e a página chega quebrada.
# O carimbo é o resumo do próprio CSS: muda sozinho quando o CSS muda,
# e só então.
CSS = """
:root{
  --azul:#1b2f6b; --azul-claro:#60b0e2; --ouro:#ffdd55; --creme:#fffaf0;
  --tinta:#23201c; --cinza:#6b6358; --borda:#e6ddc9;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--creme);color:var(--tinta);
  font:16px/1.65 "Segoe UI",system-ui,-apple-system,sans-serif}
img{max-width:100%;display:block}
a{color:var(--azul)}
.envolta{max-width:1040px;margin:0 auto;padding:0 20px}

header.topo{background:var(--azul);color:#fff;padding:14px 0}
.topo .envolta{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.marca{font-weight:800;letter-spacing:1px;color:var(--ouro);text-decoration:none;font-size:19px}
.topo nav{display:flex;gap:18px;flex-wrap:wrap}
.topo nav a{color:#fff;text-decoration:none;font-size:14px;letter-spacing:.3px}
.topo nav a:hover{color:var(--ouro)}

.heroi-capa{background:var(--azul-claro);padding:46px 0;text-align:center}
.heroi-capa h1{font-size:clamp(28px,5vw,44px);color:#fff;line-height:1.15;
  text-shadow:0 2px 0 rgba(27,47,107,.35)}
.heroi-capa p{color:#fff;font-size:17px;margin-top:12px;max-width:52ch;margin-inline:auto}

main{padding:40px 0 60px}
h2{font-size:25px;color:var(--azul);margin-bottom:14px}
h3{font-size:19px;color:var(--azul);margin-bottom:8px}
p+p{margin-top:12px}
.leve{color:var(--cinza);font-size:14.5px}

.botao{display:inline-block;margin-top:18px;padding:15px 30px;border-radius:999px;
  background:var(--ouro);color:var(--azul);font-weight:800;text-decoration:none;
  border:3px solid var(--azul);font-size:16px}
.botao:hover{background:#fff}
.botao--calmo{background:#fff}

.grade{display:grid;gap:22px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));margin-top:24px}
.cartao{border:2px solid var(--borda);border-radius:16px;background:#fff;padding:14px;
  text-align:center;text-decoration:none;color:inherit}
.cartao:hover{border-color:var(--azul-claro)}
.cartao img{border-radius:10px;margin-bottom:10px}
.cartao b{display:block;color:var(--azul);font-size:18px}
.cartao span{font-size:13px;color:var(--cinza)}

.duas{display:grid;gap:34px;grid-template-columns:1fr;align-items:start}
@media(min-width:760px){.duas{grid-template-columns:1fr 1fr}}
.moldura{border:2px solid var(--borda);border-radius:16px;background:#fff;padding:12px}

.aviso{margin-top:34px;border-left:4px solid var(--azul-claro);background:#fff;
  padding:14px 18px;border-radius:0 12px 12px 0;font-size:14.5px;color:var(--cinza)}

.inscricao{margin-top:20px;border:2px solid var(--borda);border-radius:16px;
  background:#fff;padding:20px}
.inscricao label{display:block;font-weight:700;color:var(--azul);margin-bottom:8px}
.inscricao-linha{display:flex;gap:12px;flex-wrap:wrap}
.inscricao input[type=email]{flex:1 1 240px;min-width:0;padding:14px 16px;
  border:2px solid var(--borda);border-radius:999px;font:inherit;color:var(--tinta);
  background:var(--creme)}
.inscricao input[type=email]:focus{outline:none;border-color:var(--azul-claro)}
.inscricao button{margin-top:0;cursor:pointer;flex:0 0 auto}
.inscricao .leve{margin-top:12px}
.inscricao-recado{margin-top:12px;font-weight:700;color:var(--azul)}
.inscricao--feita .inscricao-linha{display:none}
.inscricao--feita .inscricao-recado{font-size:17px}

.tres{display:grid;gap:20px;grid-template-columns:1fr;margin-top:24px}
@media(min-width:720px){.tres{grid-template-columns:repeat(3,1fr)}}
.tres article{border:2px solid var(--borda);border-radius:16px;background:#fff;padding:20px}
.icone{display:inline-grid;place-items:center;width:46px;height:46px;border-radius:12px;
  font-size:22px;margin-bottom:10px}
.icone.azul{background:#dceeff}.icone.ouro{background:#fff1b8}.icone.rosa{background:#ffe3ec}

.episodio{border:2px solid var(--borda);border-radius:16px;background:#fff;padding:18px 20px;margin-top:16px}
.episodio b{color:var(--azul);font-size:18px;display:block}
.episodio span{font-size:13.5px;color:var(--cinza)}

footer{background:var(--azul);color:#cfd8ef;padding:30px 0;font-size:14px;margin-top:40px}
footer a{color:var(--ouro);text-decoration:none}
footer .envolta{display:flex;gap:20px;justify-content:space-between;flex-wrap:wrap}
footer nav{display:flex;gap:16px;flex-wrap:wrap}
"""

CARIMBO = hashlib.md5(CSS.encode("utf-8")).hexdigest()[:8]

# O formulário funciona SEM este roteiro: nesse caso ele envia direto para a
# página do beehiiv (o `action` do <form>). Com o roteiro, a inscrição acontece
# sem sair do site: ele fala com a Function em /subscribe, que guarda a chave.
JS = """// Inscrição sem sair da página. Se algo falhar, o formulário segue
// o caminho normal do <form> e a pessoa termina na página do beehiiv.
(function () {
  var f = document.querySelector("form.inscricao");
  if (!f || !window.fetch) return;

  var campo = f.querySelector('input[type=email]');
  var botao = f.querySelector("button");
  var recado = document.createElement("p");
  recado.className = "leve inscricao-recado";
  recado.setAttribute("role", "status");
  f.appendChild(recado);

  var textoOriginal = botao.textContent;

  f.addEventListener("submit", function (e) {
    e.preventDefault();
    var email = campo.value.trim();
    if (!email) return;

    botao.disabled = true;
    botao.textContent = "Sending…";
    recado.textContent = "";

    fetch("/subscribe", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email: email })
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (d) {
        if (d && d.ok) {
          f.classList.add("inscricao--feita");
          recado.textContent =
            "Thank you! Check your inbox — your pages are on the way.";
          campo.value = "";
        } else {
          falhar();
        }
      })
      .catch(falhar);
  });

  function falhar() {
    // Nada de beco sem saída: devolvemos a pessoa ao caminho que funciona.
    botao.disabled = false;
    botao.textContent = textoOriginal;
    recado.textContent = "";
    HTMLFormElement.prototype.submit.call(f);
  }
})();
"""

CARIMBO_JS = hashlib.md5(JS.encode("utf-8")).hexdigest()[:8]



def pagina(titulo, descricao, corpo, caminho_raiz=".", capa=None, roteiro=False):
    nav = f"""<nav>
      <a href="{caminho_raiz}/heroes/">The Heroes</a>
      <a href="{caminho_raiz}/watch/">Stories &amp; Songs</a>
      <a href="{caminho_raiz}/free/">Free Pack</a>
      <a href="{caminho_raiz}/book/">The Book</a>
      <a href="{caminho_raiz}/parents/">For Parents</a>
    </nav>"""
    bloco_capa = ""
    if capa:
        bloco_capa = f"""<section class="heroi-capa"><div class="envolta">
      <h1>{capa[0]}</h1><p>{capa[1]}</p></div></section>"""
    bloco_roteiro = (
        f'<script src="{caminho_raiz}/js/subscribe.js?v={CARIMBO_JS}"></script>'
        if roteiro else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descricao}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Pendragon Kids">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<link rel="stylesheet" href="{caminho_raiz}/style.css?v={CARIMBO}">
</head>
<body>
<header class="topo"><div class="envolta">
  <a class="marca" href="{caminho_raiz}/">PENDRAGON KIDS</a>
  {nav}
</div></header>
{bloco_capa}
<main><div class="envolta">
{corpo}
</div></main>
<footer><div class="envolta">
  <div>
    <b style="color:#fff">Pendragon Kids</b><br>
    Coloring pages and little heroes, by Pete Michael.<br>
    <span style="font-size:12.5px">Everything here is made for a grown-up and a child to enjoy together.</span>
  </div>
  <nav>
    <a href="{caminho_raiz}/parents/">For Parents</a>
    <a href="{INSTAGRAM}">Instagram</a>
    <a href="{TIKTOK}">TikTok</a>
    <a href="{YOUTUBE}">YouTube</a>
    <a href="{GRUPO_FB}">Facebook Group</a>
  </nav>
</div></footer>
{bloco_roteiro}
</body>
</html>
"""


def escrever(caminho_relativo, html):
    destino = SAIDA / caminho_relativo
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")


def miniatura(origem, destino, largura=520):
    im = Image.open(origem).convert("RGB")
    if im.width > largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, quality=88)


def construir():
    # A pasta vive dentro do OneDrive, que trava arquivos enquanto sincroniza:
    # apagar a árvore inteira falha com "Acesso negado" no meio da operação e
    # deixa o site pela metade. Em vez de brigar, sobrescreve-se — o conjunto
    # de arquivos é determinístico, então nada fica para trás de uma versão
    # para outra. Só se limpa o que o gerador cria.
    SAIDA.mkdir(parents=True, exist_ok=True)
    for antigo in list(SAIDA.rglob("*.html")) + list(SAIDA.rglob("*.jpg")):
        try:
            antigo.unlink()
        except PermissionError:
            pass
    (SAIDA / "style.css").write_text(CSS, encoding="utf-8")
    (SAIDA / "js").mkdir(exist_ok=True)
    (SAIDA / "js" / "subscribe.js").write_text(JS, encoding="utf-8")

    # --- downloads: o pacote e as folhas avulsas que já são gratuitas --------
    (SAIDA / "downloads").mkdir(exist_ok=True)
    shutil.copy(PACK / "PendragonKids_Activity_Pack.pdf",
                SAIDA / "downloads" / "pendragon-kids-activity-pack.pdf")
    for chave, arquivo in FOLHA_AVULSA.items():
        shutil.copy(PACK / "paginas_png" / arquivo,
                    SAIDA / "downloads" / f"color-{chave}.png")

    # --- imagens leves para a web -------------------------------------------
    for chave, *_ in HEROIS:
        ficha = FICHAS / f"{chave}-ficha-v1.png"
        im = Image.open(ficha).convert("RGB")
        # a ficha tem 3 vistas em cima e 4 expressões embaixo: recorta a vista
        # de frente, que é o retrato que serve de cartão
        recorte = im.crop((0, 0, im.width // 3, int(im.height * 0.62)))
        miniatura_destino = SAIDA / "img" / f"{chave}.jpg"
        recorte.thumbnail((520, 520), Image.LANCZOS)
        miniatura_destino.parent.mkdir(parents=True, exist_ok=True)
        recorte.save(miniatura_destino, quality=88)
        if chave in FOLHA_AVULSA:
            miniatura(PACK / "paginas_png" / FOLHA_AVULSA[chave],
                      SAIDA / "img" / f"color-{chave}.jpg", 520)
    miniatura(PACK / "paginas_png" / "pack_00_cover.png", SAIDA / "img" / "pack.jpg", 560)

    # --- home ----------------------------------------------------------------
    cartoes = "\n".join(
        f'<a class="cartao" href="/heroes/{c}/"><img src="/img/{c}.jpg" alt="{n}">'
        f'<b>{n}</b><span>{"age " + str(i) if i else "the old wizard"}</span></a>'
        for c, n, i, *_ in HEROIS)
    escrever("index.html", pagina(
        "Pendragon Kids — free coloring pages and little heroes",
        "Nine little heroes of Camelot, free coloring pages, and a printable "
        "activity pack for parents and educators.",
        f"""<div class="duas">
  <div>
    <h2>Start with the free pack</h2>
    <p>Ten printable pages: five heroes to colour, a maze, a dot-to-dot, a
    drawing page and a cover. Made for a grown-up and a child to sit down with
    together.</p>
    <p class="leve">No cost. Just print and colour.</p>
    <a class="botao" href="/free/">Get the free activity pack</a>
  </div>
  <div class="moldura"><img src="/img/pack.jpg" alt="The free Camelot Heroes activity pack"></div>
</div>

<h2 style="margin-top:50px">Stories made for wonder, kindness and creativity</h2>
<div class="tres">
  <article><span class="icone azul">&#9876;</span><h3>Little adventures</h3>
    <p>Short, joyful stories with clear beginnings, surprises and happy endings.</p></article>
  <article><span class="icone ouro">&#9998;</span><h3>Make and imagine</h3>
    <p>Colouring pages and simple activities that turn watching into creating.</p></article>
  <article><span class="icone rosa">&#9825;</span><h3>Big feelings</h3>
    <p>Gentle moments about friendship, courage, patience and helping one another.</p></article>
</div>
<p style="margin-top:18px"><a href="/watch/">Watch the stories and sing along &#8594;</a></p>

<h2 style="margin-top:50px">Meet the nine</h2>
<p>Every one of them has a page of their own — and most have a free colouring
sheet you can print right now.</p>
<div class="grade">{cartoes}</div>

<div class="aviso">
  <b>For grown-ups.</b> Pendragon Kids is written and drawn for parents,
  carers and teachers to share with children aged about 4 to 8. We never ask
  children for anything — see <a href="/parents/">For Parents</a>.
</div>
""",
        capa=("Nine little heroes of Camelot",
              "Free colouring pages, printable activities, and a coloring book "
              "for children aged 4 to 8.")))

    # --- página de cada herói -------------------------------------------------
    for chave, nome, idade, descricao, marca, _ in HEROIS:
        tem_folha = chave in FOLHA_AVULSA
        if tem_folha:
            oferta = f"""<div class="duas">
  <div class="moldura"><img src="/img/color-{chave}.jpg" alt="Free {nome} colouring page"></div>
  <div>
    <h2>Free {nome} colouring page</h2>
    <p>One page, ready to print at home. Thick lines and wide open spaces, drawn
    for small hands that are still learning to stay inside them.</p>
    <a class="botao" href="/downloads/color-{chave}.png" download>Print the {nome} page</a>
    <p class="leve" style="margin-top:16px">Want nine more pages? The
    <a href="/free/">free activity pack</a> has colouring, a maze and a
    dot-to-dot.</p>
  </div>
</div>"""
        else:
            oferta = f"""<h2>Colour {nome}</h2>
<p>{nome} is in the <a href="/free/">free activity pack</a> and in the colouring
book — ten printable pages to start with, thirty-two in the book.</p>
<a class="botao" href="/free/">Get the free activity pack</a>"""

        escrever(f"heroes/{chave}/index.html", pagina(
            f"{nome} — Pendragon Kids",
            f"{descricao} Free colouring pages for children aged 4 to 8.",
            f"""<div class="duas">
  <div class="moldura"><img src="/img/{chave}.jpg" alt="{nome}"></div>
  <div>
    <h2>Who {nome} is</h2>
    <p>{descricao}</p>
    <p class="leve">Look for <b>{marca}</b> — it is in every picture of {nome}.</p>
    <p class="leve">{"Age " + str(idade) if idade else "The oldest of them all"}.</p>
  </div>
</div>

<div style="margin-top:44px">{oferta}</div>

<p style="margin-top:40px"><a href="/heroes/">← all nine heroes</a></p>
""",
            caminho_raiz="../..",
            capa=(nome, descricao)))

    # --- índice dos heróis -----------------------------------------------------
    escrever("heroes/index.html", pagina(
        "The nine heroes — Pendragon Kids",
        "Arthur, Kay, Aine, Percival, Lancelot, Bors, Gawain, Bedivere and "
        "Merlin — with free colouring pages.",
        f"""<h2>Nine heroes, nine pages</h2>
<p>Each one has a page of their own, and most have a colouring sheet you can
print right now.</p>
<div class="grade">{cartoes}</div>""",
        caminho_raiz="..",
        capa=("The nine heroes of Camelot",
              "Click a hero to meet them — and to print their colouring page.")))

    # --- a página que destrava tudo: o pacote ----------------------------------
    escrever("free/index.html", pagina(
        "Free Camelot activity pack — Pendragon Kids",
        "Ten printable pages: five heroes to colour, a maze, a dot-to-dot and "
        "a drawing page. Free for parents and educators.",
        f"""<div class="duas">
  <div class="moldura"><img src="/img/pack.jpg" alt="The free activity pack"></div>
  <div>
    <h2>Ten pages, free</h2>
    <p>Colour Arthur, Merlin, Aine, Bors and Percival. Then a maze, a
    dot-to-dot, a page to draw your own hero, and a cover to colour.</p>
    <p>Thick lines, wide spaces, nothing fussy — made for children aged about
    four to eight, with a grown-up nearby.</p>
    <a class="botao" href="/downloads/pendragon-kids-activity-pack.pdf" download>Download the pack (PDF)</a>
    <p class="leve" style="margin-top:18px">A4 · 10 pages · print at home or at school.</p>
  </div>
</div>

<h2 style="margin-top:50px">Get the next ones by email</h2>
<p>New colouring pages, little stories and activities — sent to grown-ups, not
to children. One email at a time, and you can leave whenever you like.</p>

<form class="inscricao" action="{BEEHIIV_ENVIO}" method="post">
  <input type="hidden" name="sent_from_orchid" value="true">
  <label for="email">Your email address</label>
  <div class="inscricao-linha">
    <input id="email" name="email" type="email" required autocomplete="email"
           placeholder="you@example.com" aria-label="Your email address">
    <button class="botao" type="submit">Send me the next pages</button>
  </div>
  <p class="leve">For grown-ups only. No cost, and you can unsubscribe from any
  email. We never write to children.</p>
</form>

<p class="leve" style="margin-top:14px">Prefer to see the list first?
<a href="{BEEHIIV}">Read it here</a>.</p>

<div class="aviso">
  <b>A note for grown-ups.</b> The mailing list is for adults. We never ask a
  child for their name, age, photo or school. See <a href="/parents/">For Parents</a>.
</div>
""",
        caminho_raiz="..",
        roteiro=True,
        capa=("The free Camelot activity pack",
              "Ten printable pages for parents and educators to enjoy with a child.")))

    # --- o livro ----------------------------------------------------------------
    escrever("book/index.html", pagina(
        "The colouring book — Pendragon Kids",
        "Pendragon Kids: Camelot Heroes — 32 big pictures to colour, for "
        "children aged 4 to 8.",
        f"""<h2>Pendragon Kids: Camelot Heroes</h2>
<p><b>32 big pictures to colour.</b> The castle and a map of the kingdom, every
one of the nine heroes on a page of their own, the round table, the flag
tournament, the snowball fight, the garden animals — and the sword in the stone.</p>
<p>Thick, clean lines and wide open spaces. A blank page behind every drawing,
so crayons and markers never bleed through and any page can be torn out and put
on the wall.</p>
<p class="leve">Paperback · 8.5 × 11 in · for children aged 4 to 8.</p>
<a class="botao" href="{AMAZON}">See the book on Amazon</a>
<p style="margin-top:34px"><a href="/free/">Not sure yet? Start with the ten free pages →</a></p>""",
        caminho_raiz="..",
        capa=("The colouring book",
              "Thirty-two big pictures to colour, from the castle to the sword in the stone.")))

    # --- para os responsáveis -----------------------------------------------------
    escrever("parents/index.html", pagina(
        "For parents and educators — Pendragon Kids",
        "How Pendragon Kids works, who it is for, and our rules about children "
        "and personal data.",
        f"""<h2>Who this is for</h2>
<p>Pendragon Kids is made for <b>grown-ups to share with children</b> aged about
four to eight — parents, carers, teachers, librarians and homeschooling
families. Everything on this site is meant to be printed and coloured together.</p>

<h2 style="margin-top:38px">What we never do</h2>
<p>We do not speak to children directly, and we never ask a child for a name,
an age, a photograph, a video, a school or any other personal detail. We run no
contests or giveaways that collect information about a child.</p>
<p>Our mailing list is for adults. If you sign up, you are telling us you are a
grown-up who would like colouring pages and activities by email. You can leave
with one click, from any email we send.</p>

<h2 style="margin-top:38px">Using the pages</h2>
<p>The free pages are yours to print at home, in a classroom or in a library,
as many times as you like. Please don't sell them or pass them off as your own.</p>

<h2 style="margin-top:38px">Who makes it</h2>
<p>Pendragon Kids is written and drawn by <b>Pete Michael</b>. The nine heroes —
Arthur, Kay, Aine, Percival, Lancelot, Bors, Gawain, Bedivere and Merlin — are
our own take on the old stories of Camelot, made small and friendly.</p>

<p style="margin-top:34px"><a href="mailto:">Questions? Write to us.</a></p>

<div class="aviso">
  <b>Nothing here is a game or an app.</b> There is no login for children, no
  chat, no account and no tracking of children. Just pages to print.
</div>
""",
        caminho_raiz="..",
        capa=("For parents and educators",
              "What Pendragon Kids is, and the rules we keep about children.")))

    # --- historias e musicas (fusao com o rascunho de 29/10) ------------------
    escrever("watch/index.html", pagina(
        "Stories and songs — Pendragon Kids",
        "Little Camelot stories and sing-along songs with Arthur and the "
        "Camelot Heroes, for children aged 4 to 8.",
        f"""<h2>Watch and sing along</h2>
<p>Short stories and songs with Arthur and the Camelot Heroes — made to be
watched with a grown-up, then turned into something to draw.</p>

<div class="episodio">
  <b>S01E01 &middot; Arthur Discovers Camelot</b>
  <span>The first story &mdash; with a sing-along version.</span>
</div>
<div class="episodio">
  <b>S01E02 &middot; Come Meet the Camelot Heroes</b>
  <span>All nine heroes, one by one &mdash; with a sing-along version.</span>
</div>

<p style="margin-top:22px">
  <a class="botao" href="{YOUTUBE}">Watch on YouTube</a>
</p>
<p class="leve" style="margin-top:14px">Shorter versions on
  <a href="{INSTAGRAM}">Instagram</a> and <a href="{TIKTOK}">TikTok</a>.</p>

<h2 style="margin-top:50px">Then colour what you watched</h2>
<p>Every hero in the stories has a page here, and most have a colouring sheet
you can print right now.</p>
<a class="botao botao--calmo" href="/heroes/">Meet the nine heroes</a>

<div class="aviso">
  <b>For grown-ups.</b> Our videos are marked as made for children, which means
  no comments and no notifications &mdash; so the conversation happens in our
  <a href="{GRUPO_FB}">Facebook group</a> and by email, with adults.
</div>
""",
        caminho_raiz="..",
        capa=("Stories and songs",
              "Little adventures from Camelot, made to watch together and then draw.")))

    # --- contagem final -----------------------------------------------------------
    paginas = sorted(p.relative_to(SAIDA).as_posix() for p in SAIDA.rglob("index.html"))
    return paginas


if __name__ == "__main__":
    paginas = construir()
    print(f"site gerado em {SAIDA}")
    for p in paginas:
        print("  ", p)
    tamanho = sum(f.stat().st_size for f in SAIDA.rglob("*") if f.is_file())
    print(f"\n{len(list(SAIDA.rglob('*')))} arquivos · {tamanho/1024/1024:.1f} MB")
