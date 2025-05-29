import { COPY_BUTTON_TEXT, COPY_BUTTON_RESET_DELAY, CODE_TEMPLATES } from './constants.js';

/**
 * Copies code content to clipboard and updates button text temporarily
 * @param {string} id - ID of the code element to copy
 * @param {HTMLButtonElement} button - The copy button element
 */
export function copyToClipboard(id, button) {
    const code = document.getElementById(id);
    navigator.clipboard.writeText(code.innerText).then(() => {
        button.textContent = COPY_BUTTON_TEXT.COPIED;
        setTimeout(() => button.textContent = COPY_BUTTON_TEXT.DEFAULT, COPY_BUTTON_RESET_DELAY);
    });
}

/**
 * Shows the selected tab and hides others
 * @param {string} tabId - ID of the tab to show
 */
export function showTab(tabId) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`.tab[data-tab="${tabId}"]`).classList.add('active');
}

/**
 * Toggles the visibility of the code examples section
 * @throws {Error} When toggle or content elements are not found
 */
export function toggleExamples() {
    try {
        console.log('Toggling examples section...');
        const toggle = document.querySelector('.examples-toggle');
        const content = document.getElementById('examples-content');
        
        if (!toggle || !content) {
            console.error('Toggle or content elements not found:', { toggle, content });
            return;
        }
        
        toggle.classList.toggle('open');
        content.classList.toggle('open');
        console.log('Examples section toggled successfully');
    } catch (error) {
        console.error('Error in toggleExamples:', error);
    }
}

/**
 * Initializes the code examples section with tabs, toggle functionality, and copy buttons
 * @throws {Error} When required DOM elements are not found
 */
export function setupCodeExamples() {
    try {
        console.log('Setting up code examples...');
        
        // Set up tab click handlers
        const tabs = document.querySelectorAll('.tab');
        if (tabs.length === 0) {
            console.error('No tab elements found');
            return;
        }
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                showTab(tabId);
            });
        });
        console.log('Tab handlers set up successfully');

        // Set up examples toggle
        const toggle = document.querySelector('.examples-toggle');
        if (!toggle) {
            console.error('Examples toggle element not found');
            return;
        }
        
        toggle.addEventListener('click', toggleExamples);
        console.log('Examples toggle handler set up successfully');

        // Set up copy buttons
        const tabContents = document.querySelectorAll('.tab-content');
        if (tabContents.length === 0) {
            console.error('No tab content elements found');
            return;
        }
        
        tabContents.forEach((tab) => {
            const pre = tab.querySelector('pre');
            const code = pre?.querySelector('code');
            if (code) {
                const btn = document.createElement('button');
                btn.textContent = COPY_BUTTON_TEXT.DEFAULT;
                btn.className = 'copy-button';

                const id = code.id || `code-${Math.random().toString(36).substr(2, 9)}`;
                code.id = id;
                btn.onclick = () => copyToClipboard(id, btn);

                const wrapper = document.createElement('div');
                wrapper.className = 'code-block-wrapper';

                wrapper.appendChild(btn);
                wrapper.appendChild(pre);
                tab.appendChild(wrapper);
            }
        });
        console.log('Copy buttons set up successfully');
    } catch (error) {
        console.error('Error in setupCodeExamples:', error);
    }
}

/**
 * Updates code examples with new coordinates
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 */
export function updateCodeExamples(latitude, longitude) {
    const lat = latitude.toFixed(4);
    const lon = longitude.toFixed(4);

    const curlCode = CODE_TEMPLATES.CURL(lat, lon);
    const pythonCode = CODE_TEMPLATES.PYTHON(lat, lon);
    const jsCode = CODE_TEMPLATES.JAVASCRIPT(lat, lon);

    const curlEl = document.getElementById("curl-code");
    const pyEl = document.getElementById("python-code");
    const jsEl = document.getElementById("js-code");

    curlEl.textContent = curlCode;
    pyEl.textContent = pythonCode;
    jsEl.textContent = jsCode;

    // Re-highlight code using Prism
    Prism.highlightElement(curlEl);
    Prism.highlightElement(pyEl);
    Prism.highlightElement(jsEl);
} 