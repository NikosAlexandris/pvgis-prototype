const { Vector2 } = THREE;

/** @constant {string} Base URL for the PVGIS API broadband performance endpoint */
export const PVGIS_API_ENDPOINT = 'https://pvgis6.jrc.it/performance/broadband';

/** @constant {string} Default start time for the API queries in ISO format */
export const DEFAULT_START_TIME = '2005-01-01 00:00:00';

/** @constant {string} Default end time for the API queries in ISO format */
export const DEFAULT_END_TIME = '2020-12-31 23:59:59';

/** 
 * @constant {Object} Text content for the copy button states
 * @property {string} DEFAULT - Default button text
 * @property {string} COPIED - Button text after successful copy
 */
export const COPY_BUTTON_TEXT = {
    DEFAULT: 'Copy',
    COPIED: 'Copied!'
};

/** @constant {number} Delay in milliseconds before resetting copy button text */
export const COPY_BUTTON_RESET_DELAY = 2000;

/** 
 * @constant {Object} Code example templates for different programming languages
 * @property {Function} CURL - Generates a cURL command example
 * @property {Function} PYTHON - Generates a Python code example
 * @property {Function} JAVASCRIPT - Generates a JavaScript code example
 */
export const CODE_TEMPLATES = {
    /** 
     * @param {number} lat - Latitude coordinate
     * @param {number} lon - Longitude coordinate
     * @returns {string} Formatted cURL command with proper line breaks
     */
    CURL: (lat, lon) => {
        const url = new URL(PVGIS_API_ENDPOINT);
        url.searchParams.set('latitude', lat);
        url.searchParams.set('longitude', lon);
        url.searchParams.set('start_time', DEFAULT_START_TIME);
        url.searchParams.set('end_time', DEFAULT_END_TIME);
        
        const baseUrl = url.origin + url.pathname;
        const startTime = encodeURIComponent(DEFAULT_START_TIME);
        const endTime = encodeURIComponent(DEFAULT_END_TIME);
        
        return `curl "${baseUrl}\\
?latitude=${lat}\\
&longitude=${lon}\\
&start_time=${startTime}\\
&end_time=${endTime}"`;
    },
    
    /** 
     * @param {number} lat - Latitude coordinate
     * @param {number} lon - Longitude coordinate
     * @returns {string} Formatted Python code
     */
    PYTHON: (lat, lon) => 
        `import requests\n\nlatitude = ${lat}\nlongitude = ${lon}\n\nresponse = requests.get("${PVGIS_API_ENDPOINT}", params={\n    "latitude": latitude,\n    "longitude": longitude,\n    "start_time": "${DEFAULT_START_TIME}",\n    "end_time": "${DEFAULT_END_TIME}"\n})\n\nprint(response.json())`,
    
    /** 
     * @param {number} lat - Latitude coordinate
     * @param {number} lon - Longitude coordinate
     * @returns {string} Formatted JavaScript code
     */
    JAVASCRIPT: (lat, lon) => {
        const code = `const url = new URL('${PVGIS_API_ENDPOINT}');
url.searchParams.set('latitude', '${lat}');
url.searchParams.set('longitude', '${lon}');
url.searchParams.set('start_time', '${DEFAULT_START_TIME}');
url.searchParams.set('end_time', '${DEFAULT_END_TIME}');

fetch(url)
  .then(res => res.json())
  .then(data => console.log(data));`;
        return code;
    }
};

// Globe constants
/**
 * @constant {Object} Default view configuration for the globe
 */
export const GLOBE_VIEW = {
    DEFAULT: {
        lat: 45.812,
        lng: 8.628,
        altitude: 5
    },
    ZOOMED: {
        lat: 45.812,
        lng: 8.628,
        altitude: 2
    }
};

/**
 * @constant {Object} Globe texture URLs
 */
export const GLOBE_TEXTURES = {
    DAY: 'https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-day.jpg',
    NIGHT: 'https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg',
    TOPOLOGY: 'https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png'
};

/**
 * @constant {Object} Globe marker configuration
 */
export const GLOBE_MARKER = {
    SIZE: {
        DEFAULT: 14,
        LARGE: 24
    },
    COLOR: '#d72638',
    SVG: `<svg viewBox="-4 0 36 36">
        <path fill="currentColor" d="M14,0 C21.732,0 28,5.641 28,12.6 C28,23.963 14,36 14,36 C14,36 0,24.064 0,12.6 C0,5.641 6.268,0 14,0 Z"></path>
        <circle fill="black" cx="14" cy="14" r="7"></circle>
    </svg>`
};

/**
 * @constant {Object} Globe animation timings
 */
export const GLOBE_ANIMATION = {
    ZOOM_DURATION: 4000,
    INITIAL_DURATION: 0
};

/**
 * @constant {Object} Globe visual configuration
 */
export const GLOBE_CONFIG = {
    BACKGROUND: 'rgba(0,0,0,0)'
};

/**
 * @constant {Object} Globe shader configuration for day/night effect
 */
export const GLOBE_SHADER = {
    vertex: `
    varying vec3 vNormal;
    varying vec2 vUv;
    void main() {
        vNormal = normalize(normalMatrix * normal);
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
    fragment: `
    #define PI 3.141592653589793
    uniform sampler2D dayTexture;
    uniform sampler2D nightTexture;
    uniform vec2 sunPosition;
    uniform vec2 globeRotation;
    varying vec3 vNormal;
    varying vec2 vUv;

    float toRad(in float a) {
        return a * PI / 180.0;
    }

    vec3 Polar2Cartesian(in vec2 c) {
        float theta = toRad(90.0 - c.x);
        float phi = toRad(90.0 - c.y);
        return vec3(
            sin(phi) * cos(theta),
            cos(phi),
            sin(phi) * sin(theta)
        );
    }

    void main() {
        float invLon = toRad(globeRotation.x);
        float invLat = -toRad(globeRotation.y);
        mat3 rotX = mat3(
            1, 0, 0,
            0, cos(invLat), -sin(invLat),
            0, sin(invLat), cos(invLat)
        );
        mat3 rotY = mat3(
            cos(invLon), 0, sin(invLon),
            0, 1, 0,
            -sin(invLon), 0, cos(invLon)
        );
        vec3 rotatedSunDirection = rotX * rotY * Polar2Cartesian(sunPosition);
        float intensity = dot(normalize(vNormal), normalize(rotatedSunDirection));
        vec4 dayColor = texture2D(dayTexture, vUv);
        vec4 nightColor = texture2D(nightTexture, vUv);
        float blendFactor = smoothstep(-0.1, 0.1, intensity);
        gl_FragColor = mix(nightColor, dayColor, blendFactor);
    }`
}; 