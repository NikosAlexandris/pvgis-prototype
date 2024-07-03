"""
HTML for API
"""

html_root_page = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>PVGIS</title>
            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f4f4f4; /* Light grey background */
                }
                .header {
                    background-color: #003399; /* EC Blue */
                    color: white;
                    padding: 10px 0;
                }
                .title {
                    font-size: 70px; /* Increased Size */
                    margin-bottom: 10px; /* Space after title */
                }
                .subtitle {
                    font-size: 30px; /* Increased Size */
                    margin-bottom: 20px; /* Space after subtitle */
                }
                .poc-banner {
                    background-color: #ffcc00; /* EC Yellow */
                    color: black;
                    padding: 5px 0;
                    font-size: 20px;
                    font-weight: bold;
                }
                .content {
                    padding: 20px;
                }
                ul.links {
                    list-style-type: none;
                    padding: 0;
                }
                ul.links li {
                    margin-bottom: 10px;
                }
                ul.links a {
                    color: #003399; /* EC Blue */
                    text-decoration: none;
                    font-size: 20px;
                    font-weight: bold;
                    margin-right: 30px;
                    padding: 5px 0; /* Add padding for better spacing */
                }
                ul.links a:hover {
                    text-decoration: underline;
                }
                .explanation {
                    font-size: 14px; /* Smaller than main text */
                    color: #555; /* Subtle color */
                    font-style: italic; /* Italicize the text */
                    margin-left: 20px; /* Indent for distinction */
                    line-height: 1.6; /* Adjust line spacing */
                }
                .footer {
                    display: flex;
                    align-items: center; /* Align items vertically */
                    justify-content: center; /* Center items horizontally */
                    background-color: #f4f4f4; /* Light grey background */
                    color: #333; /* Dark text for readability */
                    font-size: 14px;
                    text-align: center;
                    padding: 20px;
                    margin-top: 30px; /* Space above the footer */
                    border-top: 1px solid #ddd; /* A subtle top border */
                }
                .footer-logo {
                    width: 100px; /* Adjust as needed */
                    height: auto; /* Maintain aspect ratio */
                    margin-right: 20px; /* Space between logo and text */
                }
                .footer-text {
                    text-align: left;
                    /* Additional styling for the text */
                }
                .footer a {
                    color: #003399; /* EC Blue */
                    text-decoration: none;
                }
                .footer a:hover {
                    text-decoration: underline;
                }
                #globeViz {
                    width: 250px;
                    height: 250px;
                    margin: auto;
                    overflow: hidden;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    position: relative;
                }
            </style>

            <script src="//unpkg.com/three"></script>
            <script src="//unpkg.com/globe.gl"></script>

        </head>
        <body>
            <div class="header">
                <div class="title">PVGIS</div>
                <div class="subtitle">Welcome to PVGIS' interactive resources</div>
            </div>
            <div class="poc-banner">Work in Progress</div>
            <div class="content">
                <ul class="links">
                    <li><a href="/docs">API</a>  <a href="https://jrc-projects.apps.ocp.jrc.ec.europa.eu/pvgis/pvis-be-prototype">Manual</a>  <a href="https://jrc-projects.apps.ocp.jrc.ec.europa.eu/pvgis/pvis-be-prototype">Forum</a></li>
                    <div class="explanation">Resources currently accessible only from inside the JRC network</div>
                </ul>
            </div>

            <div id="globeViz"></div>

            <script>
              // Initialize the globe variable outside the fetch block to ensure it's accessible throughout the script
              let world;

              fetch('/static/sample.geojson').then(res => res.json()).then(data => {
                // Define the globe inside the fetch's success callback
                world = Globe()
                  .width(300)
                  .height(300)
                  .backgroundColor('#f4f4f4')
                  .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
                  .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
                  .pointOfView({ altitude: 100 })
                  .labelsData(data.features)
                  .labelLat(d => d.geometry.coordinates[1])
                  .labelLng(d => d.geometry.coordinates[0])
                  .labelText(d => d.properties.country_name)
                  .labelColor(() => 'rgba(255, 165, 0, 0.75)')
                  .labelResolution(2)
                  (document.getElementById('globeViz'));

                // Custom globe material setup
                setupGlobeMaterial(world);
              });

              // Function to set up custom globe material
              function setupGlobeMaterial(globe) {
                const globeMaterial = globe.globeMaterial();
                globeMaterial.bumpScale = 10;

                new THREE.TextureLoader().load('https://unpkg.com/three-globe/example/img/earth-water.png', texture => {
                  globeMaterial.specularMap = texture;
                  globeMaterial.specular = new THREE.Color('grey');
                  globeMaterial.shininess = 15;
                });

                // Auto-rotate
                globe.controls().autoRotate = true;
                globe.controls().autoRotateSpeed = 0.35;

                const directionalLight = globe.lights().find(light => light.type === 'DirectionalLight');
                directionalLight && directionalLight.position.set(1, 1, 1);
              }
            </script>

            <div class="footer">
                <img class="footer-logo" src="/static/eu_logo.png" alt="European Commission Logo"/>
                <div class="footer-text">
                    Last updated on Nov 01, 2023 by the PVGIS Team<br>
                    This work is licensed under a <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">Creative Commons Attribution 4.0 International License</a>.<br>
                    All content © European Union/European Atomic Energy Community 2021 | <a href="https://ec.europa.eu/jrc/en" target="_blank">EU Science Hub</a>
                </div>
            </div>

        </body>
    </html>
    """

template_html = """<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>LV Sensors</title>
            {{ js_resources }}
            {{ css_resources }}
        </head>
        <body>
        {{ plot_div }}
        {{ plot_script }}
        </body>
    </html>
    """
