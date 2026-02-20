// Interactive Tour Configuration
const tourSteps = [
    {
        element: '.page-title',
        title: '👋 Welcome to Klodev Apex!',
        description: 'This is your dashboard where you can monitor all your campaigns and agent activities in real-time.',
        position: 'bottom',
        scrollOffset: 100
    },
    {
        element: '.stats-grid',
        title: '📊 Real-time Metrics',
        description: 'Track your key performance indicators here. See emails sent, calls made, and engagement rates at a glance.',
        position: 'top',
        scrollOffset: 100
    },
    {
        element: '.agent-pipeline',
        title: '🤖 Multi-Agent Pipeline',
        description: 'Watch your 4 AI agents work in sequence: Classification → ICP → Platform Decision → Content Generation.',
        position: 'bottom',
        scrollOffset: 100
    },
    {
        element: '.global-execute-btn',
        title: '🚀 Execute All Agents',
        description: 'Click here to run all agents at once. They will process your input and take real actions like sending emails and making calls!',
        position: 'left',
        scrollOffset: 50
    },
    {
        element: '.nav-item[href="/agents/classification"]',
        title: '🎯 Agent 1 - Classification',
        description: 'Visit each agent page to see detailed results and fine-tune parameters for your specific needs.',
        position: 'right',
        scrollOffset: 50
    },
    {
        element: '.ai-insights-panel',
        title: '💡 AI Assistant',
        description: 'Get real-time insights and suggestions from your AI assistant to optimize your campaigns and improve performance.',
        position: 'left',
        scrollOffset: 20
    }
];

let currentStep = 0;
let tourActive = false;

// Wait for elements to be ready
function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        const checkElement = () => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
            } else if (Date.now() - startTime > timeout) {
                reject(new Error(`Element ${selector} not found`));
            } else {
                setTimeout(checkElement, 100);
            }
        };
        checkElement();
    });
}

async function startTour() {
    // Check if tour has been completed before
    if (localStorage.getItem('tourCompleted') === 'true') {
        showToast('Tour already completed! You can restart from settings.', 'info');
        return;
    }

    // Don't start tour on landing page
    if (window.location.pathname === '/landing') {
        return;
    }

    tourActive = true;
    currentStep = 0;
    
    try {
        // Create tour overlay
        const overlay = document.createElement('div');
        overlay.id = 'tourOverlay';
        overlay.className = 'tour-overlay';
        document.body.appendChild(overlay);
        
        // Create tour popup
        const popup = document.createElement('div');
        popup.id = 'tourPopup';
        popup.className = 'tour-popup';
        document.body.appendChild(popup);
        
        // Add escape key handler
        document.addEventListener('keydown', handleEscapeKey);
        
        await showStep(currentStep);
    } catch (error) {
        console.error('Tour error:', error);
        endTour();
    }
}

function handleEscapeKey(e) {
    if (e.key === 'Escape' && tourActive) {
        endTour();
    }
}

async function showStep(stepIndex) {
    const step = tourSteps[stepIndex];
    
    try {
        const element = await waitForElement(step.element);
        
        // Scroll element into view with offset
        const rect = element.getBoundingClientRect();
        const absoluteTop = window.scrollY + rect.top;
        window.scrollTo({
            top: absoluteTop - step.scrollOffset,
            behavior: 'smooth'
        });
        
        // Wait for scroll to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Remove previous highlights
        document.querySelectorAll('.tour-highlight').forEach(el => el.classList.remove('tour-highlight'));
        
        // Highlight current element
        element.classList.add('tour-highlight');
        
        // Position popup
        positionPopup(step, element);
        
    } catch (error) {
        console.warn(`Element ${step.element} not found, skipping step`);
        // Skip to next step if element not found
        if (stepIndex < tourSteps.length - 1) {
            currentStep++;
            showStep(currentStep);
        } else {
            completeTour();
        }
    }
}

function positionPopup(step, element) {
    const popup = document.getElementById('tourPopup');
    if (!popup) return;
    
    const rect = element.getBoundingClientRect();
    const popupRect = popup.getBoundingClientRect();
    
    let top, left;
    
    // Calculate position based on step configuration
    switch(step.position) {
        case 'top':
            top = rect.top - popupRect.height - 20;
            left = rect.left + (rect.width / 2) - (popupRect.width / 2);
            break;
        case 'bottom':
            top = rect.bottom + 20;
            left = rect.left + (rect.width / 2) - (popupRect.width / 2);
            break;
        case 'left':
            top = rect.top + (rect.height / 2) - (popupRect.height / 2);
            left = rect.left - popupRect.width - 20;
            break;
        case 'right':
            top = rect.top + (rect.height / 2) - (popupRect.height / 2);
            left = rect.right + 20;
            break;
        default:
            top = rect.bottom + 20;
            left = rect.left + (rect.width / 2) - (popupRect.width / 2);
    }
    
    // Ensure popup stays within viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    top = Math.max(10, Math.min(top, viewportHeight - popupRect.height - 10));
    left = Math.max(10, Math.min(left, viewportWidth - popupRect.width - 10));
    
    popup.style.top = top + 'px';
    popup.style.left = left + 'px';
    
    // Add arrow pointing to the element
    addPopupArrow(step.position, element, popup);
    
    // Update popup content
    popup.innerHTML = `
        <div class="tour-popup-header">
            <h3>${step.title}</h3>
            <button class="tour-close" onclick="endTour()">✕</button>
        </div>
        <div class="tour-popup-body">
            <p>${step.description}</p>
        </div>
        <div class="tour-popup-footer">
            <div class="tour-progress">
                <span>${currentStep + 1}/${tourSteps.length}</span>
                <div class="tour-progress-bar">
                    <div class="tour-progress-fill" style="width: ${((currentStep + 1) / tourSteps.length) * 100}%"></div>
                </div>
            </div>
            <div class="tour-buttons">
                ${currentStep > 0 ? '<button class="tour-prev" onclick="prevStep()">Previous</button>' : ''}
                ${currentStep < tourSteps.length - 1 ? 
                    '<button class="tour-next" onclick="nextStep()">Next</button>' : 
                    '<button class="tour-complete" onclick="completeTour()">Finish Tour</button>'
                }
            </div>
        </div>
    `;
}

function addPopupArrow(position, element, popup) {
    // Remove any existing arrow
    const existingArrow = popup.querySelector('.tour-popup-arrow');
    if (existingArrow) {
        existingArrow.remove();
    }
    
    // Create arrow element
    const arrow = document.createElement('div');
    arrow.className = `tour-popup-arrow tour-popup-arrow-${position}`;
    
    // Position arrow based on popup position relative to element
    const elementRect = element.getBoundingClientRect();
    const popupRect = popup.getBoundingClientRect();
    
    let arrowLeft, arrowTop;
    
    switch(position) {
        case 'top':
            arrowLeft = elementRect.left + (elementRect.width / 2) - popupRect.left;
            arrowTop = popupRect.height;
            break;
        case 'bottom':
            arrowLeft = elementRect.left + (elementRect.width / 2) - popupRect.left;
            arrowTop = -8;
            break;
        case 'left':
            arrowLeft = popupRect.width;
            arrowTop = elementRect.top + (elementRect.height / 2) - popupRect.top;
            break;
        case 'right':
            arrowLeft = -8;
            arrowTop = elementRect.top + (elementRect.height / 2) - popupRect.top;
            break;
    }
    
    arrow.style.left = arrowLeft + 'px';
    arrow.style.top = arrowTop + 'px';
    
    popup.appendChild(arrow);
}

function nextStep() {
    if (currentStep < tourSteps.length - 1) {
        currentStep++;
        showStep(currentStep);
    }
}

function prevStep() {
    if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
    }
}

function completeTour() {
    localStorage.setItem('tourCompleted', 'true');
    endTour();
    showToast('🎉 Tour completed! You\'re ready to boost your sales!', 'success');
}

function endTour() {
    tourActive = false;
    document.getElementById('tourOverlay')?.remove();
    document.getElementById('tourPopup')?.remove();
    document.querySelectorAll('.tour-highlight').forEach(el => el.classList.remove('tour-highlight'));
    document.removeEventListener('keydown', handleEscapeKey);
}

// Check if first time user and show tour
document.addEventListener('DOMContentLoaded', () => {
    // Only show tour if on dashboard and not completed
    if (!localStorage.getItem('tourCompleted') && 
        window.location.pathname === '/dashboard') {
        
        // Small delay to let page fully load
        setTimeout(() => {
            showTourPrompt();
        }, 1500);
    }
});

function showTourPrompt() {
    // Create a beautiful prompt instead of confirm
    const promptDiv = document.createElement('div');
    promptDiv.className = 'tour-prompt';
    promptDiv.innerHTML = `
        <div class="tour-prompt-content">
            <div class="tour-prompt-icon">👋</div>
            <h3>Welcome to Klodev Apex!</h3>
            <p>Would you like a quick tour to see how everything works?</p>
            <div class="tour-prompt-buttons">
                <button class="tour-prompt-btn tour-prompt-yes" onclick="startTour(); this.closest('.tour-prompt').remove()">Yes, show me around</button>
                <button class="tour-prompt-btn tour-prompt-no" onclick="localStorage.setItem('tourCompleted', 'true'); this.closest('.tour-prompt').remove()">No, thanks</button>
            </div>
        </div>
    `;
    document.body.appendChild(promptDiv);
}

// Add tour styles WITH FALLBACKS to prevent CSS breakage
const tourStyles = document.createElement('style');
tourStyles.textContent = `
    .tour-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(4px);
        z-index: 9998;
        animation: fadeIn 0.3s ease;
    }

    .tour-highlight {
        position: relative !important;
        z-index: 9999 !important;
        box-shadow: 0 0 0 4px var(--primary, #2563eb), 0 0 30px var(--primary-glow, rgba(37, 99, 235, 0.5)) !important;
        border-radius: 12px !important;
        animation: pulse 2s infinite !important;
        background: var(--bg-card, #ffffff) !important;
        transition: all 0.3s ease !important;
    }

    .tour-popup {
        position: fixed;
        background: var(--bg-card, #ffffff);
        color: var(--text-primary, #0f172a);
        border-radius: 16px;
        padding: 1.5rem;
        width: 340px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        border: 1px solid var(--border-light, #e2e8f0);
        animation: scaleIn 0.3s ease;
    }

    .tour-popup-arrow {
        position: absolute;
        width: 16px;
        height: 16px;
        background: var(--bg-card, #ffffff);
        transform: rotate(45deg);
        border: 1px solid var(--border-light, #e2e8f0);
        z-index: 9999;
    }

    .tour-popup-arrow-top { border-bottom: none; border-right: none; }
    .tour-popup-arrow-bottom { border-top: none; border-left: none; }
    .tour-popup-arrow-left { border-right: none; border-top: none; }
    .tour-popup-arrow-right { border-left: none; border-bottom: none; }

    .tour-popup-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }

    .tour-popup-header h3 {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
        color: var(--text-primary, #0f172a);
    }

    .tour-close {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 1px solid var(--border-light, #e2e8f0);
        background: var(--bg-tertiary, #f8fafc);
        color: var(--text-tertiary, #64748b);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }

    .tour-close:hover {
        background: var(--error, #ef4444);
        color: white;
        transform: rotate(90deg);
        border-color: var(--error, #ef4444);
    }

    .tour-popup-body {
        margin-bottom: 1.5rem;
        line-height: 1.6;
        color: var(--text-secondary, #475569);
        font-size: 0.95rem;
    }

    .tour-popup-footer {
        border-top: 1px solid var(--border-light, #e2e8f0);
        padding-top: 1rem;
    }

    .tour-progress { margin-bottom: 1rem; }

    .tour-progress span {
        font-size: 0.8rem;
        color: var(--text-tertiary, #64748b);
        display: block;
        margin-bottom: 0.5rem;
    }

    .tour-progress-bar {
        height: 4px;
        background: var(--bg-tertiary, #e2e8f0);
        border-radius: 2px;
        overflow: hidden;
    }

    .tour-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary, #2563eb), var(--secondary, #06b6d4));
        transition: width 0.3s ease;
    }

    .tour-buttons {
        display: flex;
        gap: 0.5rem;
        justify-content: flex-end;
    }

    .tour-prev,
    .tour-next,
    .tour-complete {
        padding: 0.6rem 1.2rem;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }

    .tour-prev {
        background: var(--bg-tertiary, #f8fafc);
        color: var(--text-secondary, #475569);
    }

    .tour-next {
        background: var(--primary, #2563eb);
        color: white;
    }

    .tour-complete {
        background: var(--success, #10b981);
        color: white;
    }

    .tour-prev:hover,
    .tour-next:hover,
    .tour-complete:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Tour Prompt Modal */
    .tour-prompt {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
        background: rgba(0,0,0,0.4);
        backdrop-filter: blur(4px);
        animation: fadeIn 0.3s ease;
    }

    .tour-prompt-content {
        background: var(--bg-card, #ffffff);
        color: var(--text-primary, #0f172a);
        border-radius: 24px;
        padding: 2.5rem;
        max-width: 400px;
        text-align: center;
        box-shadow: 0 30px 60px rgba(0,0,0,0.3);
        border: 1px solid var(--border-light, #e2e8f0);
        animation: scaleIn 0.3s ease;
    }

    .tour-prompt-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: wave 2s infinite;
    }

    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(15deg); }
        75% { transform: rotate(-15deg); }
    }

    .tour-prompt-content h3 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: var(--text-primary, #0f172a);
    }

    .tour-prompt-content p {
        color: var(--text-secondary, #475569);
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    .tour-prompt-buttons {
        display: flex;
        gap: 1rem;
    }

    .tour-prompt-btn {
        flex: 1;
        padding: 0.8rem 1.5rem;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .tour-prompt-yes {
        background: linear-gradient(135deg, var(--primary, #2563eb), var(--secondary, #06b6d4));
        color: white;
    }

    .tour-prompt-yes:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px var(--primary, #2563eb);
    }

    .tour-prompt-no {
        background: var(--bg-tertiary, #f8fafc);
        color: var(--text-secondary, #475569);
        border: 1px solid var(--border-light, #e2e8f0);
    }

    .tour-prompt-no:hover {
        background: var(--error, #ef4444);
        color: white;
        border-color: var(--error, #ef4444);
    }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes scaleIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 4px var(--primary, #2563eb), 0 0 20px var(--primary-glow, rgba(37, 99, 235, 0.3)); }
        50% { box-shadow: 0 0 0 8px var(--primary, #2563eb), 0 0 30px var(--primary-glow, rgba(37, 99, 235, 0.5)); }
    }
`;
document.head.appendChild(tourStyles);

// Show toast function (if not already defined)
if (typeof showToast !== 'function') {
    window.showToast = function(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Define inline styles just in case dashboard doesn't have toast styles
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.padding = '12px 24px';
        toast.style.background = type === 'success' ? '#10b981' : '#3b82f6';
        toast.style.color = 'white';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
        toast.style.zIndex = '99999';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.gap = '10px';
        toast.style.animation = 'scaleIn 0.3s ease';

        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span style="font-weight: 500;">${message}</span>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    };
}