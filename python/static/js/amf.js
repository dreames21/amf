var amf = {
  toggleDisplay: function(selector, section1, section2, _style) {
    _style = _style || "block";
    var update = function() {
      if (selector.val() == "Yes") {
        section1.css('display', "none");
        section2.css('display', _style);
      }
      else {
        section1.css('display', _style);
        section2.css('display', "none");
      }
    };
    selector.click(update);
    selector.change(update);
    selector.click();
  },

  toggleCathodes: function(single_cathode, initial_cathode, c1, c2) {
    var updateDisplay = function() {
      if (initial_cathode.val() == "1") {
        c1.show();
        if (single_cathode.val() == "Yes") {
          c2.hide();
        }
        else {
          c2.show();
        }
      }
      else if (initial_cathode.val() == "2") {
        c2.show();

        if (single_cathode.val() == "Yes") {
          c1.hide();
        }
        else {
          c1.show();
        }
      }
    };

    single_cathode.click(updateDisplay);
    initial_cathode.click(updateDisplay);
    single_cathode.change(updateDisplay);
    initial_cathode.change(updateDisplay);
    single_cathode.click();
    initial_cathode.click();
  },
  
  simulator: function(anchor, data) {
      if (anchor.length == 0) {
        return;
      }
      else if (! Detector.webgl) {
        Detector.addGetWebGLMessage();
        return;
      }
      
      var block = function(color, x, y) {
        return new body(new THREE.CubeGeometry(1, 1, 1), color, x, y)
      }
      
      var body = function(geometry, color, x, y) {
        var _this = this;
        _this.color = color;
        _this.x = x;
        _this.y = y;
        
        var material = new THREE.MeshPhongMaterial({
          opacity: 0.95,
          ambient: 0x000000,
          color: color,
          specular: 0x555555,
          shininess: 3,
          shading: THREE.Flatshading
        });
        
        geometry.computeBoundingBox();
        geometry.computeVertexNormals();
        
        _this._mesh = new THREE.Mesh(geometry, material);
        
        _this._mesh.position.x = x;
        _this._mesh.position.y = y;
        
        _this._mesh.scale.x = 0.8;
        _this._mesh.scale.y = 0.8;
        
        _this._mesh._parent = _this;
        
        scene.add(_this._mesh);
        
        // deletes this block from the board
        _this.delete = function() {
          scene.remove(_this._mesh);
        };
        
        _this.move = function(x, y) {
          x = x || _this.x;
          y = y || _this.x;
          if (x !== _this.x) {
            _this.x = x;
          }
          if (y !== _this.y) {
            _this.y = y;
          }
          _this._mesh.position.x = _this.x;
          _this._mesh.position.y = _this.y;
        };

        // moves the block to a specified location
        _this.animate = function(dest_x, dest_y) {
          print('moving from ' + _this.x + ', ' + _this.y + ' to ' + dest_x + ', ' + dest_y);
          
          var steps = 10;
          var delay = 20;
          
          var start_x = _this.x;
          var start_y = _this.y;
          var t = 0;
          var dir_x, dir_y;
          
          if (start_x > dest_x)
            dir_x = -1;
          else
            dir_x = 1;
          if (start_y > dest_y)
            dir_y = -1;
          else
            dir_y = 1;
          
          var interval = setInterval(function() {
            _this.x += dir_x * (dest_x - start_x) / steps;
            // j is inverted
            _this.y += -1 * dir_y * (dest_y - start_y) / steps;
            _this.move();
            t++;
            if (t >= steps) {
              _this.x = dest_x;
              _this.y = dest_y;
              _this.move();
              clearInterval(interval);
            }
          }, delay);
        };
      };

      var container_w = anchor.parent().width()
      var container_h = 500
      var camera, scene, renderer;

      var init = function() {
        camera = new THREE.OrthographicCamera(container_w / - 2, container_w / 2, container_h / 2, container_h / - 2, - 2000, 1000);
        camera.position.x = 0;
        camera.position.y = 100;
        camera.position.z = 0;

        scene = new THREE.Scene();

        // Grid

        var size = 500, step = 50;

        var geometry = new THREE.Geometry();

        for (var i = - size; i <= size; i += step) {
          geometry.vertices.push(new THREE.Vector3(-size, 0, i));
          geometry.vertices.push(new THREE.Vector3(size, 0, i));

          geometry.vertices.push(new THREE.Vector3(i, 0, -size));
          geometry.vertices.push(new THREE.Vector3(i, 0, size));
        }

        var material = new THREE.LineBasicMaterial({ color: 0x000000, opacity: 0.2 });

        var line = new THREE.Line(geometry, material);
        line.type = THREE.LinePieces;
        scene.add(line);

        // Cubes

        var geometry = new THREE.CubeGeometry(50, 50, 50);
        var material = new THREE.MeshLambertMaterial({ color: colors.red, shading: THREE.FlatShading, overdraw: true });

        for (var i = 0; i < 100; i++) {
          var cube = new THREE.Mesh(geometry, material);

          cube.position.x = Math.floor((Math.random() * 1000 - 500) / 50) * 50 + 25;
          cube.position.y = (cube.scale.y * 50) / 2;
          cube.position.z = Math.floor((Math.random() * 1000 - 500) / 50) * 50 + 25;

          scene.add(cube);

        }

        // Lights

        var ambientLight = new THREE.AmbientLight(0xffffff);
        scene.add(ambientLight);

        renderer = new THREE.CanvasRenderer();
        renderer.setSize(container_w, container_h);

        anchor.append(renderer.domElement);

        window.addEventListener('resize', onWindowResize, false);

      }

      var onWindowResize = function() {

        container_w = anchor.parent().width()
        container_h = 500

        camera.left = container_w / - 2;
        camera.right = container_w / 2;
        camera.top = container_h / 2;
        camera.bottom = container_h / - 2;

        camera.updateProjectionMatrix();

        renderer.setSize(container_w, container_h);

      }

      var animate = function() {
        requestAnimationFrame(animate);
        render();
      }

      var render = function() {
        //camera.position.x = Math.cos(timer) * 200;
        //camera.position.z = Math.sin(timer) * 200;
        camera.lookAt(scene.position);
        renderer.render(scene, camera);
      }
      
      // simulator main
      init();
      animate();
  },
  
  updateRates: function() {
    var mode = $('[name=run_mode]').val()
    var angle = $('[name=sweep_angle]').val()
    
    var rate = $('[name=dep_rate]')
    
    if (mode == 'platen_mode') {
      rate.text('Angstroms / second')
    }
    else {
      if (parseInt(angle) == 360) {
        rate.text('Angstroms / rev')
      }
      else {
        rate.text('Angstroms / sweep')
      }
    }
  }
}

// utils

var goBack = function() {
  window.history.back();
};

// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

function print(msg) {
  setTimeout(function() {
    console.log(msg);
  }, 0);
};

var colors = {
  red: 0xff0000,
  green: 0x00ff00,
  blue: 0x0000ff,
  yellow: 0xffff00,
  purple: 0xa020f0,
  whut: 0x00FFE3
};

// main

$(document).ready(function() {
  amf.toggleDisplay($("#generate_files"), $("#c1_file, #c2_file"), $("#c1_thickness, #c2_thickness"));
  amf.toggleDisplay($("#mandrel_use"), $("#platen_mode_params"), $("#mandrel_mode_params, #mandrel_sw"), "inline");
  amf.toggleCathodes($("#single_cathode"), $("#initial_cathode"), $("#c1"), $("#c2"));
  amf.simulator($('#simulator'))
  $('[name=run_mode]').change(amf.updateRates)
  $('[name=sweep_angle]').change(amf.updateRates)
  amf.updateRates();
  $('[name=run_mode]').change(function() {
    if ($(this).val() == 'mandrel_mode') {
      $('[name=mandrel_use]').val('Yes').change();
    }
  })
});
