document.addEventListener('DOMContentLoaded', () => {
    const menu = document.querySelector('.fa-bars');
    const linksDiv = document.querySelector('.links-div');
    if (menu && linksDiv) {
            menu.addEventListener('click', () => {
                linksDiv.classList.toggle('active');
            });

            document.addEventListener('click', (e) => {
                if (!linksDiv.contains(e.target) && !menu.contains(e.target)) {
                    linksDiv.classList.remove('active');
                }
            });

            window.addEventListener('resize', () => {
                if (window.innerWidth > 580) {
                    linksDiv.classList.remove('active');
                }
            });
        }

    //cargar imagenes 
    const uploadImageBtn = document.getElementById('uploadImageBtn');
    const imageInput = document.getElementById('imageInput');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const cancelImageBtn = document.getElementById('cancelImageBtn');
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const chatContainer = document.getElementById('chatContainer');
    const logo = document.getElementById('logo');
    const welcomeTitle = document.getElementById('welcome-title');
    if (!chatForm || !imageInput || !uploadImageBtn) {
        console.warn('Algunos elementos del chat/imagen no se encontraron en el DOM');
        return;
    }
    let selectedFile = null;
        // Reiniciar vista previa al cargar la página
    if (imagePreviewContainer) {
        imagePreviewContainer.style.display = 'none';
        imagePreview.src = '';
        const fileName = document.getElementById('fileName');
        if (fileName) fileName.textContent = '';
        imageInput.value = ''; // por si quedó algo cargado
    }


    // VISTA PREVIA 
    uploadImageBtn.addEventListener('click', () => {
        imageInput.value = ''; // 👈 limpia antes de abrir el selector
        imageInput.click();
    });
    //  Reiniciar vista previa al cargar la página 


    imageInput.addEventListener('change', (e) => {

        const file = e.target.files[0];
        if (!file) return;
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = function(event) {
            imagePreview.src = event.target.result;
            document.getElementById('fileName').textContent = file.name;
            imagePreviewContainer.style.display = 'flex';
        };

        reader.readAsDataURL(file);
    });
    //eliminar la imagen cargada
    cancelImageBtn.addEventListener('click', () => {
        selectedFile = null;
        imageInput.value = ''; // limpia el input
        imagePreviewContainer.style.display = 'none';
        imagePreview.src = '';
        document.getElementById('fileName').textContent = '';
    });
    // === ENVÍO ===
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Si hay imagen seleccionada
        if (selectedFile) {
            addMessage(`📷 Imagen seleccionada: ${selectedFile.name}`, 'user');
            showTypingIndicator();
            const formData = new FormData();
            formData.append('image', selectedFile);

            try {
                const response = await fetch("/api/analyze_image/", {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': getCSRFToken() }
                });

                hideTypingIndicator();
                if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

                const html = await response.text();
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                const description = tempDiv.querySelector('p, .description, #description')?.textContent
                    || "No se pudo interpretar la imagen.";
                addMessage(description, 'bot');
            } catch (error) {
                hideTypingIndicator();
                addMessage('Ocurrió un error al analizar la imagen.', 'bot');
            } finally {
                selectedFile = null;
                imageInput.value = '';
                imagePreviewContainer.style.display = 'none';
                imagePreview.src = '';
            }
            return;
        }

        // Si no hay imagen, enviar mensaje normal (Voiceflow u otro)
        const message = messageInput.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        messageInput.value = '';
        logo.style.display = 'none';
        welcomeTitle.style.display = 'none';
        chatContainer.style.display = 'block';
        showTypingIndicator();

        try {
            const response = await fetch('https://general-runtime.voiceflow.com/state/user/temp/interact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'TU_API_KEY_VOICEFLOW'
                },
                body: JSON.stringify({
                    request: { type: 'text', payload: message }
                })
            });
            hideTypingIndicator();
            const data = await response.json();
            data.forEach(item => {
                if (item.type === 'text' && item.payload?.message) {
                    addMessage(item.payload.message, 'bot');
                }
            });
        } catch (error) {
            hideTypingIndicator();
            addMessage('Lo siento, hubo un error al procesar tu mensaje.', 'bot');
        }
    });

    // === FUNCIONES AUXILIARES ===
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typing = document.createElement('div');
        typing.className = 'message bot typing';
        typing.textContent = 'Escribiendo...';
        typing.id = 'typing-indicator';
        chatMessages.appendChild(typing);
    }

    function hideTypingIndicator() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        return csrfToken || '';
    }
});
