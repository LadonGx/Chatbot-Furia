document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('message-input');
    const btn = document.getElementById('btn-submit');
    const historic = document.getElementById('historic');
    const status = document.getElementById('status');
    const usernameDisplay = document.getElementById('username-display');

    // Conecta ao WebSocket
    const socket = io();
    
    // Foca no input quando a página carrega
    input.focus();

    // Função para adicionar mensagens ao histórico
    function addMessage(content, type, sender = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);

        switch(type) {
            case 'sent':
                messageElement.innerHTML = `
                    <div class="message-bubble sent-bubble">
                        ${content}
                    </div>
                `;
                break;

            case 'received':
                messageElement.innerHTML = `
                    <div class="message-bubble received-bubble">
                        ${content}
                    </div>
                `;
                break;

            case 'bot':
                messageElement.innerHTML = `
                    <div class="message-header">
                        <img src="https://upload.wikimedia.org/wikipedia/pt/f/f9/Furia_Esports_logo.png" 
                             class="bot-avatar">
                        <span>FURIA_BOT</span>
                    </div>
                    <div class="message-bubble bot-bubble">
                        ${content}
                    </div>
                `;
                break;

            case 'notification':
                messageElement.innerHTML = `
                    <div class="notification-message">
                        ${content}
                    </div>
                `;
                break;

            case 'system':
                messageElement.innerHTML = `
                    <div class="system-message">
                        ${content}
                    </div>
                `;
                break;
        }

        historic.appendChild(messageElement);
        historic.scrollTop = historic.scrollHeight;
    }

    // Função para enviar mensagem
    function sendMessage() {
        const message = input.value.trim();
        if (!message) {
            status.textContent = "Digite uma mensagem válida!";
            status.style.color = "#ff6b6b";
            setTimeout(() => status.textContent = "", 2000);
            return;
        }
        
        // Adiciona mensagem do usuário ao histórico
        addMessage(message, 'sent');
        
        // Envia mensagem via WebSocket
        socket.emit('message', { message: message });
        
        // Mostra status de processamento se for para o bot
        if (message.startsWith('@FuriaBot')) {
            status.textContent = "Processando...";
            status.style.color = "#ffcc00";
        }

        input.value = "";
    }

    //Função para limpar o historico
    function clearChatHistory() {
        historic.innerHTML = '';
        // Mensagem de boas-vindas inicial
        addMessage('Bem-vindo ao chat da FURIA! Digite @FuriaBot para interagir com nosso assistente.', 'system');
    }

    // Event listeners do WebSocket
    socket.on('connect', () => {
        addMessage('Conectado ao chat!', 'system');
    });

    socket.on('user_message', (data) => {
        // Mensagens de outros usuários
        if (data.sender_id !== socket.id) {
            addMessage(data.message, 'received');
        }
    });

    socket.on('bot_message', (data) => {
        status.textContent = "";
        addMessage(data.response, 'bot');
    });

    socket.on('system_message', (data) => {
        if (data.type === 'notification') {
            addMessage(data.message, 'notification');
        } else {
            addMessage(data.message, 'system');
        }
    });

    socket.on('disconnect', () => {
        addMessage('Desconectado do servidor', 'system');
    });

    // Event listeners da UI
    btn.addEventListener('click', sendMessage);
    
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    // Mensagem de boas-vindas inicial
    addMessage('Bem-vindo ao chat da FURIA! Digite @FuriaBot para interagir com nosso assistente.', 'system');
});