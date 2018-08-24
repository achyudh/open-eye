// Define the size of the map group.
w = 3000;
h = 1250;

var minZoom;
var maxZoom;

// Map projection
var projection = d3
   .geoEquirectangular()
   .center([0, 15]) // Center of the projection is 15 degrees north of the Equator.
   .scale([w/(2*Math.PI)]) // The scale is the width defined above divided by the total angular circumference of the world,
   .translate([w/2,h/2]) // Ensures the map is centered with the group.
;

// Map path
var path = d3
   .geoPath()
   .projection(projection)
;

function zoomed() {
  t = d3
     .event
     .transform
  ;
  countriesGroup.attr(
     "transform","translate(" + [t.x, t.y] + ")scale(" + t.k + ")"
  );
}

// Define map zoom behaviour
var zoom = d3
   .zoom()
   .on("zoom", zoomed)
;

// Drawing the map
var svg = d3
  .select("#map-holder")
  .append("svg")
  // Set to the same size as the "map-holder" div
  .attr("width", $("#map-holder").width())
  .attr("height", $("#map-holder").height())
;

// Contains every part of the map.
countriesGroup = svg
.append("g")
.attr("id", "map")
;

// Draw a path for each feature/country.
countries = countriesGroup
.selectAll("path")
.data(mapData.features)
.enter()
.append("path")
.attr("d", path)
.attr("id", function(d, i) {
  return d.properties.name.split(' ').join('-');
})
.attr("class", "country")
.attr("class", function(d, i) {

    var countryName = d.properties.name;
    if(countryName == "United States of America") {
      countryName = "United States";
    }

    var sentiment = sentiments[countryName];

    if(sentiment >= -100 && sentiment <= -75) {
      return "neg-sen-4"
    } else if(sentiment > -75 && sentiment <= -50) {
      return "neg-sen-3"
    } else if(sentiment > -50 && sentiment <= -25) {
      return "neg-sen-2"
    } else if(sentiment > -25 && sentiment < 0) {
      return "neg-sen-1"
    } else if(sentiment > 0 && sentiment <= 25) {
      return "pos-sen-1"
    } else if(sentiment > 25 && sentiment <= 50) {
      return "pos-sen-2"
    } else if(sentiment > 50 && sentiment <= 75) {
      return "pos-sen-3"
    } else if(sentiment > 75 && sentiment <= 100) {
      return "pos-sen-4"
    }
})
.on("click", function(d, i) {
  boxZoom(path.bounds(d), path.centroid(d), 20);
})

function initiateZoom(){
  // Define a "min zoom"
  minZoom = Math.max($("#map-holder").width()/w,$("#map-holder").height()/h);
  // Define a "max zoom" 
  maxZoom = 20*minZoom;
  //apply these limits of 
  zoom
     .scaleExtent([minZoom, maxZoom]) // set min/max extent of zoom
     .translateExtent([[0, 0], [w, h]]) // set extent of panning
  ;
  // define X and Y offset for centre of map
  midX = ($("#map-holder").width() - (minZoom*w))/2;
  midY = ($("#map-holder").height() - (minZoom*h))/2;
 // change zoom transform to min zoom and centre offsets
  svg.call(zoom.transform,d3.zoomIdentity.translate(midX, midY).scale(minZoom));
}

// zoom to show a bounding box, with optional additional padding as percentage of box size
function boxZoom(box, centroid, paddingPerc) {
  minXY = box[0];
  maxXY = box[1];
  // find size of map area defined
  zoomWidth = Math.abs(minXY[0] - maxXY[0]);
  zoomHeight = Math.abs(minXY[1] - maxXY[1]);
  // find midpoint of map area defined
  zoomMidX = centroid[0];
  zoomMidY = centroid[1];
  // increase map area to include padding
  zoomWidth = zoomWidth * (1 + paddingPerc / 100);
  zoomHeight = zoomHeight * (1 + paddingPerc / 100);
  // find scale required for area to fill svg
  maxXscale = $("svg").width() / zoomWidth;
  maxYscale = $("svg").height() / zoomHeight;
  zoomScale = Math.min(maxXscale, maxYscale);
  // handle some edge cases
  // limit to max zoom (handles tiny countries)
  zoomScale = Math.min(zoomScale, maxZoom);
  // limit to min zoom (handles large countries and countries that span the date line)
  zoomScale = Math.max(zoomScale, minZoom);
  // Find screen pixel equivalent once scaled
  offsetX = zoomScale * zoomMidX;
  offsetY = zoomScale * zoomMidY;
  // Find offset to centre, making sure no gap at left or top of holder
  dleft = Math.min(0, $("svg").width() / 2 - offsetX);
  dtop = Math.min(0, $("svg").height() / 2 - offsetY);
  // Make sure no gap at bottom or right of holder
  dleft = Math.max($("svg").width() - w * zoomScale, dleft);
  dtop = Math.max($("svg").height() - h * zoomScale, dtop);
  // set zoom
  svg
    .transition()
    .duration(500)
    .call(
      zoom.transform,
      d3.zoomIdentity.translate(dleft, dtop).scale(zoomScale)
    );
} 

function displayCountry() {

  var countryToDisplay = document.getElementsByClassName("form-control")[1].value;
  
  var country = mapData["features"].find(x => x.properties.name.toLowerCase() === countryToDisplay.toLowerCase())

    if(country == null) {
      initiateZoom();
    } else {
      boxZoom(path.bounds(country), path.centroid(country), 20);
  }
}

initiateZoom();