var models = {
    arena: {
        obj: "models/map.obj",
        mesh: null
    },
    echoOrange: {
        obj: "models/echo.obj",
        mesh: null
    },
    echoBlue: {
        obj: "models/echo.obj",
        mesh: null
    },
    floor: {
        obj: "models/floor1.obj",
        mesh: null
    },
    floorOutline: {
        obj: "models/floorOutline.obj",
        mesh: null
    }
};

/* three globals */
var scene, camera, controls, renderer, mesh;

/* our globals */
var ambient, light, orangeLight, blueLight;
var savedgame;
var meshes = {};
orangePlayers = [];
bluePlayers = [];

function init() {
    //Create Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1b1b1e);
    //  scene.background = new THREE.Color( 0x02020B );

    //Create Camera
    camera = new THREE.PerspectiveCamera(20, window.innerWidth / window.innerHeight, 1, 1000);
    controls = new THREE.OrbitControls(camera);
    camera.position.set(200, 25, 200);
    camera.lookAt(50, 0, 0);
    controls.update();

    //Create Renderer
    renderer = new THREE.WebGLRenderer({
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    renderer.sortObjects = false;

    //Create Lighting
    ambient = new THREE.AmbientLight(0xFFFFFF, 1, 100);
    ambient.position.set(0, 10, 0);
    scene.add(ambient);

    light = new THREE.PointLight(0xffffff, 2, 10000);
    light.position.set(0, -35, 30);
    scene.add(light);

    orangeLight = new THREE.PointLight(0xf76707, 2, 100);
    orangeLight.position.set(60, 0, 0);
    scene.add(orangeLight);

    blueLight = new THREE.PointLight(0x1c7ed6, 2, 100);
    blueLight.position.set(-30, 0, 0);
    scene.add(blueLight);

    //Object Loading Manager
    var loadingManager = new THREE.LoadingManager();
    loadingManager.onLoad = onResourcesLoaded;

    var arenaMat = new THREE.MeshPhysicalMaterial({
        side: THREE.Doubleside,
        color: 0x3433a40,
        roughness: 0.9,
        clearCoat: 1.,
        clearCoatRoughness: 1.0,
        reflectivity: .3,
    });
    var floorMat = new THREE.MeshPhysicalMaterial({
        color: 0x495057,
        roughness: 0.9,
        clearCoat: 1.,
        clearCoatRoughness: 1.0,
        reflectivity: .3,
    });

    var backMat = new THREE.MeshPhysicalMaterial({
        color: 0x343a40,
        roughness: 1,
        clearCoat: .7,
        clearCoatRoughness: 1.0,
        reflectivity: .1,
    });

    var outlineMat = new THREE.MeshPhysicalMaterial({
        color: 0xced4da,
        roughness: 0.9,
        clearCoat: 1.,
        clearCoatRoughness: 1.0,
        reflectivity: .2,
    });

    // Start loading meshes, and when complete, call onResourcesLoaded
    var objLoader = new THREE.OBJLoader(loadingManager);
    for (var _key in models) {
        (function(key) {
            objLoader.load(models[key].obj, function(mesh) {
                mesh.traverse(function(node) {
                    if (node instanceof THREE.Mesh) {
                        if (key == "arena") {
                            node.material = arenaMat;
                            node.material.transparent = true,
                                node.material.opacity = .15,
                                node.castShadow = true;
                            node.receiveShadow = true;
                            node.scale.set(1.5, 1.5, 1.5);
                        } else if (key == "echoBlue") {
                            node.material = new THREE.MeshLambertMaterial({
                                color: 0x5333ff,
                                transparent: true,
                                opacity: 0.1,
                                wireframe: true,
                                wireframeLinewidth: 0.1
                            });
                            node.scale.set(.1, .1, .1);
                        } else if (key == "echoOrange") {
                            node.material = new THREE.MeshLambertMaterial({
                                color: 0xf46036,
                                transparent: true,
                                opacity: 0.1,
                                wireframe: true,
                                wireframeLinewidth: 0.1
                            });
                            node.scale.set(.1, .1, .1);
                        } else if (key == "floor") {
                            node.material = floorMat;
                            node.receiveShadow = true;
                            node.scale.set(1.5, 1.5, 1.5);
                        } else if (key == "floorOutline") {
                            node.material = outlineMat;
                            node.receiveShadow = true;
                            node.scale.set(1.5, 1.5, 1.5);
                        }

                    }
                });
                models[key].mesh = mesh;
            });
        })(_key);
    }

    /* FIXME: do this in another thread */
    var request = new XMLHttpRequest();
    request.open("GET", "data/game.json", false);
    request.send(null)
    savedgame = JSON.parse(request.responseText);
    savedgame['frames'];

    /* Show a loading screen */
    var loadingScreen = {
        scene: new THREE.Scene(),
        camera: new THREE.PerspectiveCamera(90, window.innerWidth / window.innerHeight, 0.1, 100),
        box: new THREE.Mesh(
            new THREE.BoxGeometry(0.5, 0.5, 0.5),
            new THREE.MeshBasicMaterial({
                color: 0x4444ff
            })
        )
    };

    loadingScreen.box.position.set(0, 5, 5);
    loadingScreen.camera.lookAt(loadingScreen.box.position);
    loadingScreen.scene.add(loadingScreen.box);
}

function onResourcesLoaded() {
    meshes["echo0"] = models.echoBlue.mesh.clone();
    meshes["echo1"] = models.echoBlue.mesh.clone();
    meshes["echo2"] = models.echoBlue.mesh.clone();
    meshes["echo3"] = models.echoOrange.mesh.clone();
    meshes["echo4"] = models.echoOrange.mesh.clone();
    meshes["echo5"] = models.echoOrange.mesh.clone();
    meshes["arena"] = models.arena.mesh.clone();
    meshes["floor"] = models.floor.mesh.clone();
    meshes["floorOutline"] = models.floorOutline.mesh.clone();

    orangePlayers.push(meshes["echo0"]);
    orangePlayers.push(meshes["echo1"]);
    orangePlayers.push(meshes["echo2"]);
    bluePlayers.push(meshes["echo3"]);
    bluePlayers.push(meshes["echo4"]);
    bluePlayers.push(meshes["echo5"]);
    for (var i = 0; i < 3; i++) {
        scene.add(orangePlayers[i]);
        scene.add(bluePlayers[i]);
    }


    meshes["arena"].position.set(20, 4, -2);
    meshes["arena"].doubleSided = true;
    scene.add(meshes["arena"]);
    meshes["floor"].position.set(20, 12, -2);
    scene.add(meshes["floor"]);
    meshes["floorOutline"].position.set(20, 12, -2);
    scene.add(meshes["floorOutline"]);
    run();
}

function run() {

    var setPlayerPosition = function(player, framepos) {
        player.position.x = framepos[2];
        player.position.y = framepos[0];
        player.position.z = framepos[1];
    }

    /* frame index */
    var idx = 0;

    var anim = function() {
        requestAnimationFrame(anim);

        frame = savedgame.frames[idx];
        idx += 1;

        for (var i = 0; i < 3; i++) {
            setPlayerPosition(orangePlayers[i], frame.teams[0].players[i].position);
            setPlayerPosition(bluePlayers[i], frame.teams[1].players[i].position);
        }

        controls.update();

        renderer.render(scene, camera);
    };


    anim();
}

window.onload = init;