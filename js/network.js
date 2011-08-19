var labelType, useGradients, nativeTextSupport, animate;


function init(){
    //init data
    var json = JSON.parse(document.getElementById('data').innerHTML);
    console.debug(json) 
    //init RGraph
    var rgraph = new $jit.RGraph({
        //Where to append the visualization
        injectInto: 'infovis',
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
        
        levelDistance:110,
        transition:$jit.Trans.Expo.easeInOut,
        fps: 30,        
        //Add the name of the node in the correponding label
        //and a click handler to move the graph.
        //This method is called once, on label creation.
        // onBeforeCompute: function(node){
        //            var max_depth = 0;
        //            rgraph.graph.eachNode(function(n) {
        //               if (n._depth > max_depth) {
        //                 max_depth = n._depth;  
        //               };
        //            });
        //             rgraph.levelDistance = Math.floor(660 / max_depth);                 
        //           }, 
        onCreateLabel: function(domElement, node){
            domElement.innerHTML = node.name;
            domElement.onclick = function(){
                rgraph.onClick(node.id, {
                    onComplete: function() {
                        //Log.write("done");
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
            }
            
            var left = parseInt(style.left);
            var w = domElement.offsetWidth;
            style.left = (left - w / 2) + 'px';
        }
    });
    //load JSON data
    rgraph.loadJSON(json, 0);
    //trigger small animation
    rgraph.graph.eachNode(function(n) {
        // n.eachAdjacency(function(adj){
        //         if (adj.getData('ignore') && adj.getData('ignore') == 'true') {
        //             adj['ignore'] = true;
        //         } 
        //     });
      var pos = n.getPos();
      pos.setc(-500, -500);
    });
    var _root_ = rgraph.graph.getNode("1")
    _root_.eachAdjacency(function(adj){
          if (adj.getData('ignore') && adj.getData('ignore') == 'true') {
              adj['ignore'] = true;
          } 
      });
    rgraph.compute('end');
    rgraph.fx.animate({
      modes:['polar'],
      duration: 2000
    });
    
    //rgraph.refresh();
    //end
    //append information about the root relations in the right column

    // rgraph.controller.onBeforeCompute(rgraph.graph.getNode(rgraph.root));
    //

}
