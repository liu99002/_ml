class ChatApp {
    constructor() {
        this.currentSessionId = null;
        this.websocket = null;
        this.isConnected = false;
        
        this.initElements();
        this.bindEvents();
        this.loadSessions();
    }
    
    initElements() {
        // DOM 元素
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.chatSessions = document.getElementById('chat-sessions');
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.currentSessionTitle = document.getElementById('current-session-title');
        this.deleteSessionBtn = document.getElementById('delete-session-btn');
        this.chatInputContainer = document.getElementById('chat-input-container');
        this.typingIndicator = document.getElementById('typing-indicator');
    }
    
    bindEvents() {
        // 新對話按鈕
        this.newChatBtn.addEventListener('click', () => this.createNewSession());
        
        // 發送消息
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // 輸入框事件
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 自動調整輸入框高度
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
        
        // 刪除會話
        this.deleteSessionBtn.addEventListener('click', () => this.deleteCurrentSession());
    }
    
    async loadSessions() {
        try {
            const response = await fetch('/api/sessions');
            const data = await response.json();
            this.renderSessions(data.sessions);
        } catch (error) {
            console.error('載入會話失敗:', error);
        }
    }
    
    renderSessions(sessions) {
        this.chatSessions.innerHTML = '';
        
        sessions.forEach(session => {
            const sessionElement = document.createElement('div');
            sessionElement.className = 'session-item';
            sessionElement.dataset.sessionId = session.session_id;
            
            sessionElement.innerHTML = `
                <div class="session-title">${session.title}</div>
                <div class="session-preview">${session.last_message || '沒有消息'}</div>
            `;
            
            sessionElement.addEventListener('click', () => {
                this.selectSession(session.session_id, session.title);
            });
            
            this.chatSessions.appendChild(sessionElement);
        });
    }
    
    async createNewSession() {
        try {
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            await this.loadSessions();
            this.selectSession(data.session.session_id, data.session.title);
        } catch (error) {
            console.error('創建會話失敗:', error);
        }
    }
    
    async selectSession(sessionId, title) {
        // 更新當前會話
        this.currentSessionId = sessionId;
        this.currentSessionTitle.textContent = title;
        
        // 更新UI狀態
        document.querySelectorAll('.session-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const currentItem = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (currentItem) {
            currentItem.classList.add('active');
        }
        
        // 顯示輸入區域和刪除按鈕
        this.chatInputContainer.style.display = 'block';
        this.deleteSessionBtn.style.display = 'block';
        
        // 連接WebSocket
        this.connectWebSocket(sessionId);
        
        // 載入聊天歷史
        await this.loadChatHistory(sessionId);
    }
    
    async loadChatHistory(sessionId) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/history`);
            const data = await response.json();
            
            this.chatMessages.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    this.displayMessage(msg.role, msg.content, new Date(msg.timestamp));
                });
            } else {
                this.showWelcomeMessage();
            }
            
            this.scrollToBottom();
        } catch (error) {
            console.error('載入聊天歷史失敗:', error);
        }
    }
    
    showWelcomeMessage() {
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>開始新對話 💬</h2>
                <p>我是您的智能助手，有什麼可以幫助您的嗎？</p>
            </div>
        `;
    }
    
    connectWebSocket(sessionId) {
        // 關閉現有連接
        if (this.websocket) {
            this.websocket.close();
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            this.isConnected = true;
            console.log('WebSocket 連接成功');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            this.isConnected = false;
            console.log('WebSocket 連接關閉');
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket 錯誤:', error);
            this.isConnected = false;
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'user_message':
                // 用戶消息已經在發送時顯示了
                break;
            case 'ai_message':
                this.hideTypingIndicator();
                this.displayMessage('assistant', data.content, new Date(data.timestamp));
                this.enableInput();
                break;
            case 'typing':
                this.showTypingIndicator();
                break;
            case 'error':
                this.hideTypingIndicator();
                this.displayMessage('assistant', `❌ 錯誤: ${data.content}`, new Date());
                this.enableInput();
                break;
        }
    }
    
    displayMessage(role, content, timestamp) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = role === 'user' ? '您' : '🤖';
        const avatarBg = role === 'user' ? '#10a37f' : '#7c3aed';
        
        messageDiv.innerHTML = `
            <div class="message-avatar" style="background-color: ${avatarBg}">
                ${avatar}
            </div>
            <div class="message-content">${this.formatMessage(content)}</div>
        `;
        
        // 移除歡迎消息
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // 簡單的 Markdown 渲染
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    disableInput() {
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
    }
    
    enableInput() {
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.messageInput.focus();
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || !this.currentSessionId || !this.isConnected) {
            return;
        }
        
        // 顯示用戶消息
        this.displayMessage('user', message, new Date());
        
        // 發送消息到WebSocket
        this.websocket.send(JSON.stringify({
            message: message
        }));
        
        // 清空輸入框並禁用
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.disableInput();
        
        // 重新載入會話列表以更新最後消息
        setTimeout(() => this.loadSessions(), 1000);
    }
    
    async deleteCurrentSession() {
        if (!this.currentSessionId) return;
        
        if (confirm('確定要刪除這個對話嗎？此操作無法撤銷。')) {
            try {
                await fetch(`/api/sessions/${this.currentSessionId}`, {
                    method: 'DELETE'
                });
                
                // 重置UI
                this.currentSessionId = null;
                this.currentSessionTitle.textContent = '選擇或創建一個對話';
                this.chatInputContainer.style.display = 'none';
                this.deleteSessionBtn.style.display = 'none';
                this.chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <h2>歡迎使用聊天助手 🤖</h2>
                        <p>我是基於大語言模型和 MCP 工具的智能助手，可以幫助您處理各種問題。</p>
                        <p>請選擇現有對話或創建新對話開始聊天。</p>
                    </div>
                `;
                
                // 關閉WebSocket
                if (this.websocket) {
                    this.websocket.close();
                }
                
                // 重新載入會話列表
                await this.loadSessions();
                
            } catch (error) {
                console.error('刪除會話失敗:', error);
                alert('刪除對話失敗，請稍後重試。');
            }
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// 初始化應用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
