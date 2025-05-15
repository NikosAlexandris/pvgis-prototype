import { initGlobe } from './globe.js';
import { setupCodeExamples, updateCodeExamples, showTab, toggleExamples } from './utilities.js';

// Expose necessary functions to window object
window.showTab = showTab;
window.toggleExamples = toggleExamples;

// Wait for DOM and all resources to load
window.addEventListener('load', () => {
    try {
        console.log('Initializing application...');
        const timeEl = document.getElementById('time');
        if (!timeEl) {
            console.error('Time element not found');
            return;
        }

        const globeContainer = document.getElementById('globeViz');
        if (!globeContainer) {
            console.error('Globe container not found');
            return;
        }

        // Initialize globe
        console.log('Initializing globe...');
        initGlobe('globeViz', timeEl);

        // Setup code examples
        console.log('Setting up code examples...');
        setupCodeExamples();

        // Update code examples with coordinates
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                pos => {
                    const { latitude, longitude } = pos.coords;
                    updateCodeExamples(latitude, longitude);
                },
                err => {
                    console.warn('Geolocation error:', err);
                    // Keep default coordinates in examples
                }
            );
        } else {
            console.log('Geolocation not supported');
            // Keep default coordinates in examples
        }
    } catch (error) {
        console.error('Error initializing application:', error);
    }
}); 