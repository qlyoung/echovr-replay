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
    }
};

/* three globals */
var scene, camera, renderer, mesh;

/* our globals */
var ambient, light;
var savedgame;
var meshes = {};
orangePlayers = [];
bluePlayers = [];

function init() {
    //Create Scene
    scene = new THREE.Scene();

    //Create Camera
    camera = new THREE.PerspectiveCamera(20, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.set(80, 25, 80);
    camera.lookAt(0, -10, 0);

    //Create Renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    renderer.sortObjects = false;

    //Create Lighting
    ambient = new THREE.AmbientLight(0xA0A0A0);
    scene.add(ambient);
    light = new THREE.PointLight(0xffffff, 1, 10000);
    light.position.set(0, -35, 30);
    scene.add(light);

    //Object Loading Manager
    var loadingManager = new THREE.LoadingManager();
    loadingManager.onProgress = function(item, loaded, total) {
        //console.log(item, loaded, total);
    };
    loadingManager.onLoad = onResourcesLoaded;

    // Start loading meshes, and when complete, call onResourcesLoaded
    var objLoader = new THREE.OBJLoader(loadingManager);
    for (var _key in models) {
        (function(key) {
            objLoader.load(models[key].obj, function(mesh) {
                mesh.traverse(function(node) {
                    if (node instanceof THREE.Mesh) {
                        if (key == "arena") {
                            node.material = new THREE.MeshLambertMaterial({
                                color: 0x00ff00,
                                transparent: true,
                                opacity: 0.1,
                                wireframe: true,
                                wireframeLinewidth: 0.1
                            });
                            node.scale.set(.12, .12, .12);
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
                        }
                    }
                });
                models[key].mesh = mesh;
            });
        })(_key);
    }

    /* FIXME: do this in another thread */
    var request = new XMLHttpRequest();
    request.open("GET", "../data/game.json", false);
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

    loadingScreen.box.position.set(0, 0, 5);
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


    meshes["arena"].position.set(0, 0, 0);
    scene.add(meshes["arena"]);

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

        renderer.render(scene, camera);
    };


    anim();
}

window.onload = init;
