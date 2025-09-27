const { TextureLoader, ShaderMaterial, Vector2 } = THREE;
import { GLOBE_VIEW, GLOBE_TEXTURES, GLOBE_MARKER, GLOBE_ANIMATION, GLOBE_CONFIG, GLOBE_SHADER } from './constants.js';

const dayNightShader = {
    vertexShader: `
    varying vec3 vNormal;
    varying vec2 vUv;
    void main() {
        vNormal = normalize(normalMatrix * normal);
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
    fragmentShader: `
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

const sunPosAt = dt => {
    const day = new Date(+dt).setUTCHours(0, 0, 0, 0);
    const t = solar.century(dt);
    const longitude = (day - dt) / 864e5 * 360 - 180;
    return [longitude - solar.equationOfTime(t) / 4, solar.declination(t)];
};

export function initGlobe(containerId, timeEl) {
    try {
        console.log('Creating globe with container:', containerId);
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container ${containerId} not found`);
        }

        const globe = Globe()
            .backgroundColor(GLOBE_CONFIG.BACKGROUND)
            .globeImageUrl(GLOBE_TEXTURES.DAY)
            .bumpImageUrl(GLOBE_TEXTURES.TOPOLOGY)
            .width(container.clientWidth)
            .height(container.clientHeight)
            (container);

        if (!globe) {
            throw new Error('Failed to create globe instance');
        }
        console.log('Globe instance created successfully');

        globe.controls().enableZoom = false;

        console.log('Loading globe textures...');
        Promise.all([
            new TextureLoader().loadAsync(GLOBE_TEXTURES.DAY)
                .catch(err => {
                    console.error('Failed to load day texture:', err);
                    throw err;
                }),
            new TextureLoader().loadAsync(GLOBE_TEXTURES.NIGHT)
                .catch(err => {
                    console.error('Failed to load night texture:', err);
                    throw err;
                })
        ]).then(([dayTexture, nightTexture]) => {
            console.log('Textures loaded successfully');

            // Set texture properties
            dayTexture.minFilter = THREE.LinearFilter;
            nightTexture.minFilter = THREE.LinearFilter;

            const material = new ShaderMaterial({
                uniforms: {
                    dayTexture: { value: dayTexture },
                    nightTexture: { value: nightTexture },
                    sunPosition: { value: new Vector2() },
                    globeRotation: { value: new Vector2() }
                },
                vertexShader: GLOBE_SHADER.vertex,
                fragmentShader: GLOBE_SHADER.fragment
            });

            globe
                .globeMaterial(material)
                .onZoom(({ lng, lat }) => material.uniforms.globeRotation.value.set(lng, lat));

            globe.pointOfView(GLOBE_VIEW.DEFAULT, GLOBE_ANIMATION.INITIAL_DURATION);

            if ('geolocation' in navigator) {
                navigator.geolocation.getCurrentPosition(
                    pos => {
                        const { latitude, longitude } = pos.coords;
                        console.log('Moving to:', { lat: latitude, lng: longitude, altitude: GLOBE_VIEW.ZOOMED.altitude });
                        globe.pointOfView({ lat: latitude, lng: longitude, altitude: GLOBE_VIEW.ZOOMED.altitude }, GLOBE_ANIMATION.ZOOM_DURATION);

                        // Add location marker
                        globe
                            .htmlElementsData([{
                                lat: latitude,
                                lng: longitude,
                                size: GLOBE_MARKER.SIZE.DEFAULT,
                                color: GLOBE_MARKER.COLOR
                            }])
                            .htmlElement(d => {
                                const el = document.createElement('div');
                                el.innerHTML = GLOBE_MARKER.SVG;
                                el.style.color = d.color;
                                el.style.width = `${d.size}px`;
                                el.style.height = `${d.size}px`;
                                el.style.cursor = 'pointer';
                                return el;
                            });
                    },
                    err => {
                        console.warn('Geolocation unavailable:', err.message);
                        globe.pointOfView(GLOBE_VIEW.ZOOMED, GLOBE_ANIMATION.ZOOM_DURATION);

                        // Add default location marker
                        globe
                            .htmlElementsData([{
                                lat: GLOBE_VIEW.DEFAULT.lat,
                                lng: GLOBE_VIEW.DEFAULT.lng,
                                size: GLOBE_MARKER.SIZE.DEFAULT,
                                color: GLOBE_MARKER.COLOR
                            }])
                            .htmlElement(d => {
                                const el = document.createElement('div');
                                el.innerHTML = GLOBE_MARKER.SVG;
                                el.style.color = d.color;
                                el.style.width = `${d.size}px`;
                                el.style.height = `${d.size}px`;
                                el.style.cursor = 'pointer';
                                return el;
                            });
                    }
                );
            } else {
                globe.pointOfView(GLOBE_VIEW.ZOOMED, GLOBE_ANIMATION.ZOOM_DURATION);

                // Add default location marker
                globe
                    .htmlElementsData([{
                        lat: GLOBE_VIEW.DEFAULT.lat,
                        lng: GLOBE_VIEW.DEFAULT.lng,
                        size: GLOBE_MARKER.SIZE.LARGE,
                        color: GLOBE_MARKER.COLOR
                    }])
                    .htmlElement(d => {
                        const el = document.createElement('div');
                        el.innerHTML = GLOBE_MARKER.SVG;
                        el.style.color = d.color;
                        el.style.width = `${d.size}px`;
                        el.style.height = `${d.size}px`;
                        el.style.cursor = 'pointer';
                        return el;
                    });
            }

            requestAnimationFrame(function animate() {
                const now = Date.now();
                timeEl.textContent = new Date(now).toUTCString();
                material.uniforms.sunPosition.value.set(...sunPosAt(now));
                requestAnimationFrame(animate);
            });

        }).catch(error => {
            console.error('Error in globe initialization:', error);
        });
    } catch (error) {
        console.error('Critical error in initGlobe:', error);
    }
} 