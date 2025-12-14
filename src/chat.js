document.addEventListener('DOMContentLoaded', () => {
    // Function to load the navbar, only executed if the navbar-container exists
    function loadNavbar() {
        const navbarContainer = document.getElementById('navbar-container');
        if (navbarContainer) {
            fetch('/src/navbar.html')
                .then(res => res.text())
                .then(data => {
                    navbarContainer.innerHTML = data;
                    // Populate profile data in navbar
                    fetch('/profile').then(res => res.json()).then(profileData => {
                        if (profileData.username) {
                            document.getElementById('profile-username').textContent = profileData.username;
                            document.getElementById('profile-username-val').textContent = profileData.username;
                            document.getElementById('profile-role-val').textContent = profileData.role;
                            document.getElementById('profile-email-val').textContent = profileData.email;

                            // Show admin dashboard link if user is admin
                            if (profileData.role === 'admin') {
                                const adminDashboardLink = document.getElementById('admin-dashboard-link');
                                if (adminDashboardLink) {
                                    adminDashboardLink.style.display = 'block';
                                }
                            }
                        }
                    }).catch(error => console.error('Error fetching profile for navbar:', error));
                }).catch(error => console.error('Error loading navbar:', error));
        }
    }

    loadNavbar(); // Call navbar loading on DOMContentLoaded for chat.html

    // Chat functionality (can be used by chat.html or as a popup in admin.html)
    function initChat(chatContainerId = 'chat-container') {
        const chatContainer = document.getElementById(chatContainerId);
        if (!chatContainer) {
            console.warn(`Chat container with ID '${chatContainerId}' not found.`);
            return;
        }

        const chatMessages = chatContainer.querySelector('#chat-messages');
        const chatInput = chatContainer.querySelector('#chat-input');
        const sendButton = chatContainer.querySelector('#send-button');
        const closeChatButton = chatContainer.querySelector('#chat-close-btn'); // For popup

        if (sendButton) {
            // Remove any existing listeners to prevent duplicates
            const newSendButton = sendButton.cloneNode(true);
            sendButton.parentNode.replaceChild(newSendButton, sendButton);
            newSendButton.addEventListener('click', () => sendMessage(newSendButton.parentNode.querySelector('#chat-input'), chatMessages));
        }
        if (chatInput) {
            // Remove any existing listeners to prevent duplicates
            const newChatInput = chatInput.cloneNode(true);
            chatInput.parentNode.replaceChild(newChatInput, chatInput);
            newChatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage(newChatInput, chatMessages);
                }
            });
        }
        if (closeChatButton) {
            // Remove any existing listeners to prevent duplicates
            const newCloseChatButton = closeChatButton.cloneNode(true);
            closeChatButton.parentNode.replaceChild(newCloseChatButton, closeChatButton);
            newCloseChatButton.addEventListener('click', () => toggleChatPopup(false, chatContainerId));
        }

        // Initial bot message for the popup if it's new
        if (chatContainerId === 'chat-popup' && chatMessages && chatMessages.children.length === 0) {
            appendMessage('Hello! How can I assist you today?', 'bot', chatMessages);
        }

        // Fetch profile data and conditionally hide admin-only elements
        fetch('/profile')
            .then(res => res.json())
            .then(profileData => {
                if (profileData.role !== 'admin') {
                    const adminElements = [
                        'nav-user-management', 'nav-knowledge-base', 'nav-llm-settings',
                        'user-management', 'knowledge-base', 'llm-settings'
                    ];
                    adminElements.forEach(id => {
                        const element = document.getElementById(id);
                        if (element) {
                            element.style.display = 'none';
                        }
                    });
                }
            })
            .catch(error => console.error('Error fetching profile for role check:', error));
    }

    function sendMessage(chatInput, chatMessages) {
        const message = chatInput.value.trim();
        if (message === '') return;

        appendMessage(message, 'user', chatMessages);
        chatInput.value = '';

        // Simulate bot response
        setTimeout(() => {
            appendMessage('This is a simulated bot response to: "' + message + '"', 'bot', chatMessages);
        }, 1000);
    }

    function appendMessage(message, sender, chatMessages) {
        if (!chatMessages) return;
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender + '-message');
        messageElement.innerText = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to latest message
    }

    // Function to toggle the visibility of the chat popup (for admin dashboard)
    function toggleChatPopup(show, chatContainerId = 'chat-popup') {
        const chatPopup = document.getElementById(chatContainerId);
        if (chatPopup) {
            chatPopup.style.display = show ? 'flex' : 'none';
            // Only initialize chat features if showing the popup and it's the admin dashboard popup
            if (show && chatContainerId === 'chat-popup') {
                initChat(chatContainerId);
            }
        }
    }

    // Check if we are on the dedicated chat page (src/chat.html)
    // or if we are on admin.html and need to set up the popup
    const dedicatedChatContainer = document.getElementById('chat-container');
    const chatPopupContainer = document.getElementById('chat-popup');

    if (dedicatedChatContainer) {
        initChat('chat-container');
    }

    if (chatPopupContainer) {
        // This is for admin.html, where chat-popup is an element
        // Add event listener to the FAB button to toggle the chat popup
        const chatFab = document.getElementById('chat-fab');
        if (chatFab) {
            chatFab.addEventListener('click', () => {
                // Determine if we should show or hide based on current display style
                const isShowing = chatPopupContainer.style.display === 'flex';
                toggleChatPopup(!isShowing, 'chat-popup');
            });
        }
    }
});