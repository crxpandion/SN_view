var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
      }
};


function init(){
    //init data
    var json = JSON.parse(document.getElementById('data').innerHTML);
    console.debug(json) 
    //init RGraph
    var rgraph = new $jit.RGraph({
        //Where to append the visualization
        injectInto: 'infovis',
        //Optional: create a background canvas that plots
        //concentric circles.
        /*background: {
         CanvasStyles: {
            strokeStyle: '#555'
          }
        },*/
        //Add navigation capabilities:
        //zooming by scrolling and panning.
        Navigation: {
          enable: true,
          panning: true,
          zooming: 15
        },
        //Set Node and Edge styles.
        Node: {
            color: '#aacfe4'
        },
        
        Edge: {
          overridable : true,
          type : 'arrow',
          color: '#2feb51',
          lineWidth:1.0
        },
        
        levelDistance:120,
        transition:$jit.Trans.Expo.easeInOut,
        fps: 30,
        onBeforeCompute: function(node){

            Log.write("centering " + node.name + "...");
            //Add the relation list in the right column.
            //This list is taken from the data property of each JSON node.
            //$jit.id('inner-details').innerHTML = node.data.relation;
        },
        
        //Add the name of the node in the correponding label
        //and a click handler to move the graph.
        //This method is called once, on label creation.
        onCreateLabel: function(domElement, node){
            domElement.innerHTML = node.name;
            domElement.onclick = function(){
                rgraph.onClick(node.id, {
                    onComplete: function() {
                        Log.write("done");
                    }
                });
            };
        },
        //Change some label dom properties.
        //This method is called each time a label is plotted.
        onPlaceLabel: function(domElement, node){
            var style = domElement.style;
            style.display = '';
            style.cursor = 'pointer';
            
            if (node._depth <= 1) {
                style.fontSize = "0.8em";
                style.fontWeight = "bold";
                style.color = "#202020";
            
            } else{ //if(node._depth == 2){
                style.fontSize = "0.7em";
                style.color = "#696969";
            
          /*  } else {
                style.display = 'none';
            */}
            
            var left = parseInt(style.left);
            var w = domElement.offsetWidth;
            style.left = (left - w / 2) + 'px';
        }
    });
    //load JSON data
    rgraph.loadJSON(json, 0);
    //trigger small animation
    rgraph.graph.eachNode(function(n) {
      var pos = n.getPos();
      pos.setc(-500, -500);
    });
    
    rgraph.compute('end');
    rgraph.fx.animate({
      modes:['polar'],
      duration: 2000
    });
    
    //rgraph.refresh();
    //end
    //append information about the root relations in the right column

    rgraph.controller.onBeforeCompute(rgraph.graph.getNode(rgraph.root));
    //

}
