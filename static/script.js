document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    const sendBtn = document.getElementById('send-btn');
    
    // Generate a unique thread ID for the session
    const threadId = 'session_' + Math.random().toString(36).substr(2, 9);
    
    // Configure marked options
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    function createMessageElement(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
        
        let htmlContent = content;
        
        // If it's an agent message, let's format it nicer
        if (!isUser) {
            // Check if there is an INTENT block and style it uniquely
            const intentMatch = content.match(/\[INTENT: *(.*?)\]/i);
            if (intentMatch) {
                const intentStr = intentMatch[1];
                // Remove the raw intent block text from the markdown
                content = content.replace(/\[INTENT: *(.*?)\]/i, '').trim();
                // Parse markdown
                htmlContent = window.marked ? marked.parse(content) : content;
                // Prepend the intent badge
                htmlContent = `<span class="intent-badge">${intentStr}</span>` + htmlContent;
            } else {
                htmlContent = window.marked ? marked.parse(content) : content;
            }
        }
        
        messageDiv.innerHTML = `
            <div class="avatar ${isUser ? 'user-avatar' : 'agent-avatar'}">${isUser ? 'U' : 'IN'}</div>
            <div class="message-content">
                ${isUser ? `<p>${escapeHTML(content)}</p>` : htmlContent}
            </div>
        `;
        
        return messageDiv;
    }

    function createTypingIndicator() {
        const ind = document.createElement('div');
        ind.className = 'message agent-message typing-indicator';
        ind.id = 'typing-indicator';
        ind.style.display = 'flex';
        
        ind.innerHTML = `
            <div class="avatar agent-avatar">IN</div>
            <div class="typing-bubbles">
                <span></span><span></span><span></span>
            </div>
        `;
        return ind;
    }

    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    function scrollToBottom() {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;
        
        // 1. Append User Message
        chatContainer.appendChild(createMessageElement(text, true));
        userInput.value = '';
        sendBtn.disabled = true;
        scrollToBottom();
        
        // 2. Append Typing Indicator
        const typingInd = createTypingIndicator();
        chatContainer.appendChild(typingInd);
        scrollToBottom();
        
        // 3. Make API request
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: text,
                    thread_id: threadId
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingInd.remove();
            
            // Append Agent Message
            chatContainer.appendChild(createMessageElement(data.response || "No response", false));
            
        } catch (err) {
            console.error(err);
            typingInd.remove();
            chatContainer.appendChild(createMessageElement("Error: Could not connect to server.", false));
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
            scrollToBottom();
        }
    });

    // Handle enter key properly
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});
