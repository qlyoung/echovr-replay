var scene, camera, renderer, mesh;
var ambient, light;

var loadingScreen = {
    scene: new THREE.Scene(),
    camera: new THREE.PerspectiveCamera(90, 1280/720, 0.1, 100),
    box: new THREE.Mesh(
        new THREE.BoxGeometry(0.5,0.5,0.5),
        new THREE.MeshBasicMaterial({ color:0x4444ff })
    )
};
var loadingManager = null;
var RESOURCES_LOADED = false;

// Models index
var models = {
    arena: {
        obj:"models/map.obj",
        mesh: null
    }
};

var echoModel = {
    echo: {
        obj:"models/echo.obj",
        mesh: null
    }
};

var blueModel = {
    echo: {
        obj:"models/echo.obj",
        mesh: null
    }
};

// Meshes index
var meshes = {};


function init(){
    //Create Scene
    scene = new THREE.Scene();

    //Create Camera
    camera = new THREE.PerspectiveCamera( 20, window.innerWidth/window.innerHeight, 1, 1000 );
    camera.position.set(80, 25, 80);
    camera.lookAt(0,-10,0);

    //Create Renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );
    renderer.sortObjects = false;

    //Create Lighting
    ambient = new THREE.AmbientLight(0xA0A0A0);
    scene.add(ambient);
    light = new THREE.PointLight(0xffffff, 1, 10000);
    light.position.set(0, -35, 30);
    scene.add( light );

    //Loading Screen
    loadingScreen.box.position.set(0,0,5);
    loadingScreen.camera.lookAt(loadingScreen.box.position);
    loadingScreen.scene.add(loadingScreen.box);

    //Object Loading Manager
    loadingManager = new THREE.LoadingManager();
    loadingManager.onProgress = function(item, loaded, total){
       //console.log(item, loaded, total);
    };
    loadingManager.onLoad = function(){
      //console.log("loaded all resources");
        RESOURCES_LOADED = true;
        onResourcesLoaded();
    };

    // Load Arena Instance
    var objLoader = new THREE.OBJLoader(loadingManager);
    for( var _key in models ){
        (function(key){
            objLoader.load(models[key].obj, function(mesh){
                mesh.traverse(function(node){
                    if( node instanceof THREE.Mesh ){
                        node.material = new THREE.MeshLambertMaterial({color: 0x00ff00, transparent: true, opacity: 0.1, wireframe: true, wireframeLinewidth: 0.1});
                        node.scale.set(.12,.12,.12);
                    }
                });
                models[key].mesh = mesh;
            });
        })(_key);
    }

    // Load Orange Team Instance
    for( var echoKey in echoModel ){
        (function(key){
            objLoader.load(echoModel[key].obj, function(mesh){
                mesh.traverse(function(node){
                    if( node instanceof THREE.Mesh ){
                        node.material = new THREE.MeshLambertMaterial({color: 0xf46036, transparent: true, opacity: 0.1, wireframe: true, wireframeLinewidth: 0.1});
                        node.scale.set(.1,.1,.1);
                    }
                });
                echoModel[key].mesh = mesh;
            });
        })(echoKey);
    }

    // Load Blue Team Instance
    for( var blue in blueModel ){
        (function(key){
            objLoader.load(blueModel[key].obj, function(mesh){
                mesh.traverse(function(node){
                    if( node instanceof THREE.Mesh ){
                        node.material = new THREE.MeshLambertMaterial({color: 0x5333ff, transparent: true, opacity: 0.1, wireframe: true, wireframeLinewidth: 0.1});
                        node.scale.set(.1,.1,.1);
                    }
                });
                blueModel[key].mesh = mesh;
            });
        })(blue);
    }

    // Load Frames
    var request = new XMLHttpRequest();
    request.open("GET", "../data/game.json", false);
    request.send(null)
    var savedGame = JSON.parse(request.responseText);
    var frames = savedGame['frames'];

    orangePlayers = []
    bluePlayers = []
    meshes["echo0"] = echoModel.echo.mesh.clone();
    meshes["echo1"] = echoModel.echo.mesh.clone();
    meshes["echo2"] = echoModel.echo.mesh.clone();
    meshes["echo3"] = blueModel.echo.mesh.clone();
    meshes["echo4"] = blueModel.echo.mesh.clone();
    meshes["echo5"] = blueModel.echo.mesh.clone();
    var playerGeo = new THREE.SphereGeometry( 1, 32, 32 );
    var playerOrangeMat = new THREE.MeshBasicMaterial({color: 0xffa500});
    var playerBlueMat = new THREE.MeshBasicMaterial({color: 0x0000ff});

    orangePlayers.push(meshes["echo0"]);
    orangePlayers.push(meshes["echo1"]);
    orangePlayers.push(meshes["echo2"]);
    bluePlayers.push(meshes["echo3"]);
    bluePlayers.push(meshes["echo4"]);
    bluePlayers.push(meshes["echo5"]);
    for (var i = 0; i < 6; i++) {
        scene.add(orangePlayers[i]);
        scene.add(bluePlayers[i]);
    }

    var setPlayerPosition = function(player, framepos) {
        player.position.x = framepos[2];
        player.position.y = framepos[0];
        player.position.z = framepos[1];
    }
    /* frame index */
    var idx = 0;

    var animate = function () {
        frame = frames[idx];
        idx += 1;
        requestAnimationFrame( animate );

        for (var i = 0; i < 3; i++) {
            setPlayerPosition(orangePlayers[i], frame.teams[0].players[i].position);
            setPlayerPosition(bluePlayers[i], frame.teams[1].players[i].position);
        }

        renderer.render( scene, camera );
    };


    animate();

}

// Runs when all resources are loaded
function onResourcesLoaded(){

    // Clone models into meshes.
    meshes["arena"] = models.arena.mesh.clone();
    meshes["echo"] = echoModel.echo.mesh.clone();

    // Reposition individual meshes, then add meshes to scene
    meshes["arena"].position.set(0, 0, 0);
    scene.add(meshes["arena"]);

    meshes["echo"].position.set(0, 5, 0);
}

function animate(){

    // Play the loading screen until resources are loaded.
    if( RESOURCES_LOADED == false ){
        requestAnimationFrame(animate);

        loadingScreen.box.position.x -= 0.05;
        if( loadingScreen.box.position.x < -10 ) loadingScreen.box.position.x = 10;
        loadingScreen.box.position.y = Math.sin(loadingScreen.box.position.x);

        renderer.render(loadingScreen.scene, loadingScreen.camera);
        return;
    }

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

window.onload = init;

