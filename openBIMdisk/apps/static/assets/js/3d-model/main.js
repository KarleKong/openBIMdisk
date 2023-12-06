import * as THREE from '../threejs/Three.js';
import {PLYLoader} from './PLYLoader.js';
import {OrbitControls} from './OrbitControls.js';
import * as DB from '../installation-data.js';

let installationData;
let camera, scene, renderer, light, orbitControls;
let canvasContainer = document.getElementById('canvas-container');
let width = canvasContainer.clientWidth,
    height = canvasContainer.clientHeight;
const DEFAULT_CAMERA_ZOOM = 1.5;
const loader = new PLYLoader();

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

const meshes = {};
const lines = {};

let geometryProcessComplete = false;
let selectedMode = false; // indicate whether a module is selected (clicked)
let selectedModuleName, hoveredModuleName;

const MESH_OPACITY_FOCUS = 0.8,
    LINE_OPACITY_FOCUS = 1;
const MESH_OPACITY_FADE = 0.1,
    LINE_OPACITY_FADE = 0.1;
const MESH_OPACITY_HOVER = 0.5,
    LINE_OPACITY_HOVER = 0.5;

const MESH_COLOR_GREY = '#C4C4C4',
    MESH_COLOR_YELLOW = '#F7CD45',
    MESH_COLOR_BLUE = '#3AA0DD',
    MESH_COLOR_GREEN = '#30A14E',
    MESH_COLOR_DISABLED = '#777';

const LINE_COLOR_GREY = '#919191',
    LINE_COLOR_YELLOW = '#E78C10',
    LINE_COLOR_BLUE = '#246B8C',
    LINE_COLOR_GREEN = '#10722F',
    LINE_COLOR_DISABLED = '#444';

const meshColorMap = {
    0: MESH_COLOR_GREY,
    1: MESH_COLOR_YELLOW,
    2: MESH_COLOR_BLUE,
    3: MESH_COLOR_GREEN,
    'disabled': MESH_COLOR_DISABLED
};

const lineColorMap = {
    0: LINE_COLOR_GREY,
    1: LINE_COLOR_YELLOW,
    2: LINE_COLOR_BLUE,
    3: LINE_COLOR_GREEN,
    'disabled': LINE_COLOR_DISABLED
};

const moduleStatusMap = {
    0: 'Not in production yet',
    1: 'Production in progress',
    2: 'Production completed',
    3: 'Installed'
};

// set color for meshes and lines
const setColor = function (colorMap, moduleName) {
    if (['ground'].includes(moduleName)) {
        return colorMap['disabled'];
    } else {
        return getMapValue(colorMap, moduleName);
    }
}

const getMapValue = function (map, moduleName) {
    return installationData.hasOwnProperty(moduleName)
        ? map[installationData[moduleName]]
        : map[0];
};

function init() {
    camera = new THREE.PerspectiveCamera(60, width / height, 1, 10000);
    camera.position.set(300, 240, 300);
    camera.zoom = DEFAULT_CAMERA_ZOOM;
    scene = new THREE.Scene();

    let x = -123.04345166015625,
        z = -46.603991455078145;
    let y = -184.4871513671875;
    let y_ground = y + 10;
    let y_roof = y + 17.4871513671875;

    const PLY_TOTAL = 60; // total number of .ply files to be loaded
    let plySuccess = 0, plyError = 0; // number of successful and failed loads
    let geometryProcessedTotal; // total number of geometries to be processed
    let geometryProcessed = 0; // number of geometries processed

    // store all geometry objects on load
    let groundGeometry;
    let standardGeometry = {}; // map (key: .ply file name; value: geometry object)
    let roofGeometry;

    $('#three-model > .hint').click(function () {
        $('.loading').removeClass('hide');
        $('#three-model > .hint').addClass('hide');

        const model_url="../../static/assets/newmodel/"

        // load ground
        loadPLY(model_url + 'ground.ply', 'ground');
        // load standard
        loadPLY(model_url + `standard/A-TR.ply`, 'standard', `A-TR`);
        loadPLY(model_url + `standard/B-TR.ply`, 'standard', `B-TR`);
        for (let i = 1; i <= 14; ++i) {
            // Tower A
            loadPLY(model_url + `standard/A-N-${i}.ply`, 'standard', `A-N-${i}`);
            loadPLY(model_url + `standard/A-S-${i}.ply`, 'standard', `A-S-${i}`);
            // Tower B
            loadPLY(model_url + `standard/B-N-${i}.ply`, 'standard', `B-N-${i}`);
            loadPLY(model_url + `standard/B-S-${i}.ply`, 'standard', `B-S-${i}`);
        }
        // load roof
        loadPLY(model_url + '/roof.ply', 'roof');

        // load installation data
        setTimeout(function () {
            installationData = DB.installationData;
            checkLoadComplete();
        }, 100);
    });

    // load a .ply file and obtain the corresponding geometry object
    function loadPLY(url, type, key) { // key: key for the standardGeometry map
        loader.load(url, function (geometry) {
            switch (type) {
                case 'ground':
                    groundGeometry = geometry;
                    break;
                case 'standard':
                    standardGeometry[key] = geometry;
                    break;
                case 'roof':
                    roofGeometry = geometry;
                    break;
            }

            plySuccess++;
            checkLoadComplete();

        }, undefined, function () {
            plyError++;
            checkLoadComplete();
        });
    }

    function checkLoadComplete() {
        // check whether both .ply files and
        // installation data are completely loaded
        if (plySuccess + plyError === PLY_TOTAL
            && installationData !== undefined)
            onPLYLoadComplete();
    }

    function onPLYLoadComplete() {
        // calculate total number of PLY to be rendered
        geometryProcessedTotal = ( (groundGeometry !== undefined) ? 1 : 0 )
            + Object.keys(standardGeometry).length * 17
            + ( (roofGeometry !== undefined) ? 1 : 0 );

        // ground
        processGeometry(groundGeometry, 'ground', 'ground');

        // standard
        for (let floor = 3; floor <= 19; ++floor) {
            // Tower A, TR
            processGeometry(standardGeometry[`A-TR`], 'standard', `A-${floor}-TR`, floor);
            // Tower A, Wing N
            for (let i = 1; i <= 14; ++i) {
                processGeometry(standardGeometry[`A-N-${i}`], 'standard', `A-${floor}-N-${i}`, floor);
            }
            // Tower A, Wing S
            for (let i = 1; i <= 14; ++i) {
                processGeometry(standardGeometry[`A-S-${i}`], 'standard', `A-${floor}-S-${i}`, floor);
            }
            // Tower B, TR
            processGeometry(standardGeometry[`B-TR`], 'standard', `B-${floor}-TR`, floor);
            // Tower B, Wing N
            for (let i = 1; i <= 14; ++i) {
                processGeometry(standardGeometry[`B-N-${i}`], 'standard', `B-${floor}-N-${i}`, floor);
            }
            // Tower B, Wing S
            for (let i = 1; i <= 14; ++i) {
                processGeometry(standardGeometry[`B-S-${i}`], 'standard', `B-${floor}-S-${i}`, floor);
            }
        }

        // roof
        processGeometry(roofGeometry, 'roof', 'roof');
    }

    // process a geometry (create meshes and lines)
    function processGeometry(geometry, type, moduleName, floor) { // floor: 3-19
        // make processing each geometry asynchronous
        setTimeout(function () {
            if (geometry === undefined) {
                // handle undefined geometry caused by load error
                return;
            }

            geometry.computeVertexNormals();
            // TODO: improve performance
            const material = new THREE.MeshLambertMaterial({
                color: setColor(meshColorMap, moduleName), // mesh color
                // specular: '#111',
                // shininess: 200,
                transparent: true,
                opacity: selectedMode ? MESH_OPACITY_FADE : MESH_OPACITY_FOCUS
            });

            const mesh = new THREE.Mesh(geometry, material);

            let scalar = 3;
            let calcY = y;
            switch (type) {
                case 'ground':
                    scalar *= 0.001;
                    calcY = y_ground;
                    break;
                case 'standard':
                    calcY = y + 10 * (floor - 3);
                    break;
                case 'roof':
                    calcY = y_roof;
                    break;
            }

            mesh.name = moduleName;
            mesh.position.set(x, calcY, z);
            mesh.rotation.x = -Math.PI / 2;
            mesh.scale.multiplyScalar(scalar);
            // TODO: improve performance
            // mesh.castShadow = true;
            // mesh.receiveShadow = true;

            //为mesh添加轮廓线
            const edges = new THREE.EdgesGeometry(geometry);
            const edgesMaterial = new THREE.LineBasicMaterial({
                color: setColor(lineColorMap, moduleName), // line color
                transparent: true,
                opacity: selectedMode ? LINE_OPACITY_FADE : LINE_OPACITY_FOCUS
            });

            const line = new THREE.LineSegments(edges, edgesMaterial);
            line.name = moduleName;
            line.scale.multiplyScalar(scalar);
            line.position.set(x, calcY, z);
            line.rotateX(-Math.PI / 2);

            // add click event for each mesh
            mesh.onClick = function () {
                if (selectedMode) {
                    setFade(selectedModuleName);
                    setFocus(moduleName);

                } else {
                    for (let key in meshes) {
                        if (key === moduleName) {
                            setFocus(key);
                            continue;
                        }

                        setFade(key);
                    }
                }

                selectedModuleName = moduleName;

                $('#three-model > .module-info .module-id').text(moduleName);
                $('#three-model > .module-info .module-status').text(
                    getMapValue(moduleStatusMap, moduleName)
                );
                
                $('#three-model > .module-info .status-label').css({
                    'background': setColor(meshColorMap, moduleName)
                });
                $.ajax({
                    url:'/query',
                    method:'POST',
                    data:{selectedModuleName:selectedModuleName},
                    success: function(response){
                        console.log(response);
                        $('#refreshedTable tbody').html(response);
                        // if (response.redirect){
                        //     window.location.href = response.redirect;
                        // }
                    },
                    error:function(error){
                        console.error(error);
                    }
                });
            };

            mesh.onHover = function () {
                if (selectedMode) {
                    if (hoveredModuleName !== selectedModuleName) {
                        // recover the last hovered mesh
                        setFade(hoveredModuleName);
                    }

                    if (moduleName !== selectedModuleName) {
                        // highlight the newly hovered mesh
                        setHover(moduleName);
                    }

                } else {
                    if (hoveredModuleName !== undefined) {
                        // recover the last hovered mesh
                        setFocus(hoveredModuleName);
                    }

                    // highlight the newly hovered mesh
                    setHover(moduleName);
                }

                hoveredModuleName = moduleName;
            }

            const group = new THREE.Group();
            group.add(mesh);
            group.add(line);
            scene.add(group);

            meshes[moduleName] = mesh;
            lines[moduleName] = line;

            if ((++geometryProcessed) === geometryProcessedTotal) {
                onGeometryProcessComplete();
            }
        });
    }

    function onGeometryProcessComplete() {
        $('.loading').addClass('hide');
        setTimeout(function () {
            geometryProcessComplete = true;
        }, 100);
    }

    function getOS() {
        let userAgent = navigator.userAgent;
        if (/iPad|iPhone|iPod/.test(userAgent)
            || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 0)) {
            return 'iOS';
        } else {
            return 'other';
        }
    }

    // light
    // light = new THREE.AmbientLight('#404040');
    light = new THREE.AmbientLight('#FFF');
    scene.add(light);

    //canvas
    //renderer
    renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById('canvas'),
        antialias: true,
        alpha: true
    });

    // TODO: improve performance
    // renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setPixelRatio(2);
    renderer.setSize(width, height);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.setClearColor('#FFF', 0);
    renderer.shadowMap.enabled = false;

    // controls
    orbitControls = new OrbitControls(camera, renderer.domElement);
    //上下旋转范围
    orbitControls.minPolarAngle = 0;
    orbitControls.maxPolarAngle = Math.PI / 2;

    // cursor: grab
    let canvas = document.getElementById('canvas');
    canvas.addEventListener('mousedown', function () {
        canvas.classList.add('grabbing');
    });
    canvas.addEventListener('mouseup', function () {
        canvas.classList.remove('grabbing');
    });

    // resize
    new ResizeObserver(function () {
        let newWidth = canvasContainer.clientWidth;
        let newHeight = canvasContainer.clientHeight;

        camera.aspect = newWidth / newHeight;
        camera.zoom = (window.innerWidth <= 576) ? 1.25 : DEFAULT_CAMERA_ZOOM;
        camera.updateProjectionMatrix();

        renderer.setSize(newWidth, newHeight);
        renderer.render(scene, camera);

    }).observe(canvasContainer);

    // mouse click event
    let drag = false;

    renderer.domElement.addEventListener('mousedown', function () {
        drag = false;
    });

    renderer.domElement.addEventListener('mousemove', function (event) {
        drag = true;
        intersect(event, function (intersects) {
            canvas.classList.add('select');
            intersects[0].object.onHover();
        }, function () {
            canvas.classList.remove('select');
            // remove the highlight when the mouse is not hovered above meshes
            if (selectedMode) {
                if (hoveredModuleName !== selectedModuleName)
                    setFade(hoveredModuleName);
            } else {
                if (hoveredModuleName !== undefined)
                    setFocus(hoveredModuleName);
            }
        });
    });

    renderer.domElement.addEventListener('mouseup', function (event) {
        if (!drag) {
            intersect(event, function (intersects) {
                intersects[0].object.onClick();
                $('#three-model > .module-info').removeClass('hide');
                selectedMode = true;
            }, function (intersects) {
                if (intersects.length > 0
                    && ['ground', 'roof'].includes(intersects[0].object.name)) {
                    // do nothing if ground or roof is clicked
                    // specifically for selected mode
                    return;
                }

                for (let key in meshes) setFocus(key);
                $('#three-model > .module-info').addClass('hide');
                selectedMode = false;
            });
        }
    });

    renderer.domElement.addEventListener('wheel', function () {
        render();
    });

    // for mobile touch move
    renderer.domElement.addEventListener('touchmove', function () {
        render();
    });

    // handle cursor's intersection with meshes
    function intersect(event, onIntersect, noIntersect) {
        mouse.x = (event.offsetX / renderer.domElement.clientWidth) * 2 - 1;
        mouse.y = -(event.offsetY / renderer.domElement.clientHeight) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        let intersects = raycaster.intersectObjects(Object.values(meshes));

        // clicking on ground or roof is treated as no intersection
        if (intersects.length > 0
            && !['ground', 'roof'].includes(intersects[0].object.name)) {
            onIntersect(intersects);
        } else {
            noIntersect(intersects);
        }

        render();
    }

    function setFocus(moduleName) {
        meshes[moduleName].material.opacity = MESH_OPACITY_FOCUS;
        lines[moduleName].material.opacity = LINE_OPACITY_FOCUS;
    }

    function setFade(moduleName) {
        meshes[moduleName].material.opacity = MESH_OPACITY_FADE;
        lines[moduleName].material.opacity = LINE_OPACITY_FADE;
    }

    function setHover(moduleName) {
        meshes[moduleName].material.opacity = MESH_OPACITY_HOVER;
        lines[moduleName].material.opacity = LINE_OPACITY_HOVER;
    }
}

// TODO: improve performance
let clock = new THREE.Clock();
let delta = 0;
// interval = 1 / fps
let interval = 1 / 25;

function render() {
    delta += clock.getDelta();
    if (delta  > interval) {
        // The draw or time dependent code are here
        renderer.render(scene, camera);
        delta = delta % interval;
    }
}

function animate() {
    requestAnimationFrame(animate);
    if (!geometryProcessComplete) {
        render();
    }
}

export default {init, animate};