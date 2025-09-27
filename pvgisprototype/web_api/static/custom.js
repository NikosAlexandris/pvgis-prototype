// custom.js

document.addEventListener('DOMContentLoaded', (event) => {
    console.log('Custom JS loaded');

    // Example: Change the title dynamically
    document.title = 'PVGIS API Documentation';

    // Example: Add a custom button
    const topbar = document.querySelector('.topbar');
    if (topbar) {
        const customButton = document.createElement('button');
        customButton.textContent = 'Custom Button';
        customButton.style.marginLeft = '20px';
        customButton.onclick = () => alert('Custom button clicked');
        topbar.appendChild(customButton);
    }

    // Example: Add custom CSS class to body
    document.body.classList.add('custom-swagger-ui');
});
