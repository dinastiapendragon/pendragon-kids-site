// Inscrição sem sair da página. Se algo falhar, o formulário segue
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
