# Site da Pendragon Kids — pendragonkids.com

Site estático. **Nada se edita à mão aqui**: as páginas saem de `gerar_site.py`,
porque as nove páginas de herói são a mesma página com dados diferentes — e são
elas o destino dos pins do Pinterest.

## Gerar

```
python gerar_site.py
```

Saída em `public/`. É essa pasta que o Cloudflare Pages publica.

## O que o site resolve

1. o Activity Pack ganha endereço fixo → o `[DOWNLOAD_LINK]` do e-mail de
   boas-vindas deixa de ser um buraco;
2. cada herói tem a sua página → os pins passam a ter destino específico
   (a regra é: pin nunca aponta para a home);
3. deixa de depender de Amazon e Instagram, que são terra alugada.

## Regras duras

- toda comunicação é dirigida ao **adulto**, nunca à criança;
- nenhum campo pede nome, idade, foto ou escola de menor;
- a inscrição aponta para a página do Beehiiv que já está no ar, em vez de uma
  segunda chave de API para manter;
- **as 32 páginas do livro não viram brinde**: só as 5 folhas que já são do
  pacote gratuito saem avulsas.

## Publicação (Cloudflare Pages)

- build command: *(vazio)*
- output directory: `public`
- domínio: `pendragonkids.com` e `www`
