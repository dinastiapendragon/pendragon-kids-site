// Cloudflare Pages Function — POST /subscribe
// -----------------------------------------------------------------------------
// Recebe { email } do formulário de /free/ e inscreve na lista do beehiiv da
// Pendragon Kids. A chave do beehiiv fica numa variável SECRETA do Cloudflare e
// NUNCA chega ao navegador: o visitante só fala com esta função.
//
// >>> VARIÁVEIS A CONFIGURAR NO PAINEL <<<
//   Cloudflare → Workers & Pages → pendragon-kids-site → Settings →
//   Variables and Secrets → Add:
//
//   BEEHIIV_API_KEY         = a chave do beehiiv. Marcar como SECRET (cifrada).
//                             (beehiiv → Settings → API → Create New API Key)
//   BEEHIIV_PUBLICATION_ID  = o id da publicação, começa com "pub_".
//                             Pode ser texto simples; não é segredo.
//
//   ⚠ É a publicação da PENDRAGON KIDS — conta separada da Dinastia.
//
// Não há campo "Language": esta lista é só em inglês. Não inventar campo
// personalizado que talvez não exista na conta — a API recusa.
// -----------------------------------------------------------------------------

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;

  if (!env.BEEHIIV_API_KEY || !env.BEEHIIV_PUBLICATION_ID) {
    return json({ ok: false, error: 'config' }, 500);
  }

  // .trim() defende contra espaço ou quebra de linha colados junto no painel —
  // causa clássica de 404, porque o id ia encodado na URL e a rota não casava.
  const apiKey = env.BEEHIIV_API_KEY.trim();
  const pubId = env.BEEHIIV_PUBLICATION_ID.trim();

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: 'invalid' }, 400);
  }

  const email = typeof body.email === 'string' ? body.email.trim() : '';
  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'email' }, 400);
  }

  let upstream;
  try {
    upstream = await fetch(
      `https://api.beehiiv.com/v2/publications/${pubId}/subscriptions`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${apiKey}`,
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          email,
          reactivate_existing: true,  // quem saiu e volta, volta
          send_welcome_email: true,   // é o e-mail que ENTREGA o Activity Pack
          utm_source: 'pendragonkids-site',
          utm_medium: 'free-page',
        }),
      },
    );
  } catch {
    return json({ ok: false, error: 'network' }, 502);
  }

  if (!upstream.ok) {
    // O detalhe não volta ao visitante; fica no log do Cloudflare para
    // diagnóstico. A chave nunca é registrada — vai só no cabeçalho.
    let detalhe = '';
    try { detalhe = await upstream.text(); } catch { /* ignore */ }
    console.error('beehiiv subscribe failed', upstream.status, detalhe);
    return json({ ok: false, error: 'upstream' }, 502);
  }

  return json({ ok: true });
}
// Métodos que não sejam POST recebem 405 do próprio Pages, já que só
// exportamos onRequestPost.
