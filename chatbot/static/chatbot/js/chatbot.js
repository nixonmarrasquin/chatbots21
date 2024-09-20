
let isWaitingForResponse = false;
let toastTimeout;

function toggleChat() {
    const chatbotContainer = document.getElementById('chatbot-container');
    const messageInput = document.getElementById('user-message');
    const chatbotButton = document.getElementById('chatbot-button');
    
    chatbotContainer.classList.toggle('visible');

    if (chatbotContainer.classList.contains('visible')) {
        messageInput.focus();
        hideToast();
        chatbotButton.classList.add('hidden');
    } else {
        showToast();
        chatbotButton.classList.remove('hidden');
    }
}

function showToast() {
    const toast = document.getElementById('toast-message');
    toast.classList.add('show');
    
    if (toastTimeout) {
        clearTimeout(toastTimeout);
    }
    
    toastTimeout = setTimeout(() => {
        hideToast();
    }, 4000);
}

function hideToast() {
    const toast = document.getElementById('toast-message');
    toast.classList.remove('show');
    
    if (toastTimeout) {
        clearTimeout(toastTimeout);
    }
}

function focusInput() {
    document.getElementById('user-message').focus();
}

function sendMessage(event) {
    if (event) event.preventDefault(); // Evita el comportamiento predeterminado del botón

    if (isWaitingForResponse) return;

    const messageInput = document.getElementById('user-message');
    const message = messageInput.value.trim();
    const messagesContainer = document.getElementById('chatbot-messages');
    const sendButton = document.getElementById('send-button');
    
    if (message === '') return;

    messageInput.disabled = true;
    sendButton.disabled = true;
    isWaitingForResponse = true;

    addMessage('Tú', message);
    saveMessage('Tú', message);

    showTypingIndicator();

    fetch('/chatbot/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: 'message=' + message
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();

        addMessage('Chatbot', data.reply);
        saveMessage('Chatbot', data.reply);

        messageInput.disabled = false;
        sendButton.disabled = false;
        isWaitingForResponse = false;
        messageInput.value = '';
        messageInput.focus();
    });
}

function sendOption(option) {
    document.getElementById('user-message').value = option;
    sendMessage();
}

function handleKey(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function addMessage(sender, text) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageElement = document.createElement('div');

    // Añadir clase de contenedor específica según el remitente
    messageElement.classList.add(sender === 'Tú' ? 'user-message-container' : 'chatbot-message-container');

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('chat-message');

    if (sender === 'Tú') {
        messageBubble.classList.add('user-message');
        messageBubble.textContent = text;
    } else {
        messageBubble.classList.add('chatbot-message');
        messageBubble.innerHTML = text;
    }

    messageElement.appendChild(messageBubble);
    messagesContainer.appendChild(messageElement);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function saveMessage(sender, text) {
    const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
    chatHistory.push({ sender, text });
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

function loadChatHistory() {
    const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

    if (chatHistory.length === 0) {
        addMessage('Chatbot', 'Hola, te responderé todas las dudas correspondientes');
    } else {
        chatHistory.forEach(message => {
            addMessage(message.sender, message.text);
        });
    }
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    messagesContainer.appendChild(typingIndicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const messagesContainer = document.getElementById('chatbot-messages');
    const typingIndicator = messagesContainer.querySelector('.typing-indicator');
    if (typingIndicator) {
        messagesContainer.removeChild(typingIndicator);
    }
}

window.onload = function() {
    loadChatHistory();
    showToast();
};


function endChat() {
    const modal = document.getElementById('confirmation-modal');
    
    // Mostrar el modal
    modal.style.display = 'flex';

    // Acción al hacer clic en "Sí"
    document.getElementById('confirm-yes').onclick = function() {
        // Borrar el historial de chat
        document.getElementById('chatbot-messages').innerHTML = '';
        document.getElementById('user-message').value = '';
        const chatbotContainer = document.getElementById('chatbot-container');
        const chatbotButton = document.getElementById('chatbot-button');
        
        chatbotContainer.classList.remove('visible');
        chatbotButton.classList.remove('hidden');
        
        // Eliminar el historial de chat almacenado
        localStorage.removeItem('chatHistory');
        
        // Recargar el historial (en este caso, se muestra el mensaje inicial)
        loadChatHistory();

        // Cerrar el modal
        modal.style.display = 'none';
    };

    // Acción al hacer clic en "No"
    document.getElementById('confirm-no').onclick = function() {
        // Cerrar el modal sin hacer nada
        modal.style.display = 'none';
    };
}

// Llamar a esta función cuando se minimice el chat o se cargue la página para ocultar el modal.
window.onload = function() {
    loadChatHistory();
    showToast();

    // Asegurarse de que el modal esté oculto al cargar la página
    const modal = document.getElementById('confirmation-modal');
    modal.style.display = 'none';
};


