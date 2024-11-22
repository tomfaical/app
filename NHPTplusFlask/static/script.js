function iniciarTeste() {
    console.log("Botão Iniciar teste clicado!");

    // Referências aos botões
    const botaoIniciar = document.getElementById("iniciar-teste");
    const botaoPare = document.getElementById("botao-parético");
    const botaoSaudavel = document.getElementById("botao-saudavel");

    // Confirma que os elementos foram encontrados
    if (botaoIniciar) console.log("Botão Iniciar teste encontrado.");
    if (botaoPare) console.log("Botão Braço parético encontrado.");
    if (botaoSaudavel) console.log("Botão Braço saudável encontrado.");

    // Mantém o botão "Iniciar teste" pressionado
    botaoIniciar.disabled = true;
    botaoIniciar.classList.add("pressionado");
    console.log("Botão Iniciar teste pressionado.");

    // Exibe os novos botões
    botaoPare.classList.remove("escondido");
    botaoSaudavel.classList.remove("escondido");
    console.log("Novos botões exibidos.");
}
