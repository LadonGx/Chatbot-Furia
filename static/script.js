document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('message-input');
    const btn = document.getElementById('btn-submit');
    const historic = document.getElementById('historic');
    const status = document.getElementById('status');

    // Foca no input quando a página carrega
    input.focus();

    async function sendQuestion() {
        const question = input.value.trim();
        if (!question) {
            status.textContent = "Digite uma pergunta válida!";
            status.style.color = "#ff6b6b";
            setTimeout(() => status.textContent = "", 2000);
            return;
        }
        
        status.textContent = "Processando...";
        status.style.color = "#ffcc00";
        btn.disabled = true;
        input.disabled = true;
        
        // Adiciona mensagem do usuário ao histórico
        const userMsg = document.createElement('p');
        userMsg.textContent = question;
        historic.appendChild(userMsg);
        
        // Rola para a última mensagem
        historic.scrollTop = historic.scrollHeight;
        
        input.value = "";
        
        try {
            const response = await fetch("/api/pergunte", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question: question })
            });
            
            const data = await response.json();
            
            // Adiciona resposta do bot ao histórico
            const botMsg = document.createElement('p');
            botMsg.textContent = data.response;
            
            // Pequeno atraso para efeito de digitação
            setTimeout(() => {
                historic.appendChild(botMsg);
                historic.scrollTop = historic.scrollHeight;
            }, 500);
            
        } catch (error) {
            console.error("Erro:", error);
            const errorMsg = document.createElement('p');
            errorMsg.textContent = "Desculpe, ocorreu um erro. Tente novamente mais tarde.";
            errorMsg.style.color = "#ff6b6b";
            historic.appendChild(errorMsg);
        } finally {
            status.textContent = "";
            btn.disabled = false;
            input.disabled = false;
            input.focus();
        }
    }

    btn.addEventListener('click', sendQuestion);
    
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendQuestion();
    });
});