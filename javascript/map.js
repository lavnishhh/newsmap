var json_data
var pins = {};
var places = [];
var news_sources = {}
var source_index = {'all': 0}
var sources_info;
var map;

function sourceLogoTempelate(image,source_id){
  const e = document.createElement('div')
  e.style.backgroundImage = "url({image-url})".replace('{image-url}',image)
  e.setAttribute('sourceid',source_id);
  e.classList.add('source-logo');
  f = document.createElement('div')
  f.appendChild(e)
  return f;
}

const loc_dropdown_item = 
`<div class="menu-item" locid="{place}">{place}</div>`

const source_dropdown_item = 
`<div class="menu-item" sourceid="{source-id}">{source}</div>`
var query_loc = ''
var query = new URLSearchParams(window.location.search)
var query_source = query.get('source')

window.history.pushState({}, document.title, window.location.pathname);

previous_selcted_map_source = null;

//var query_source_logo = document.getElementById('source-logo

if(query.get('loc')){
  query_loc = capitalize(query.get('loc'))
}
async function fetchData() {
  const response = await fetch('https://api.npoint.io/d45deb15252bacd419f4');
  json_data = await response.json();
  var index = 1
  sources_info = document.getElementById('sources-info')
  console.log(json_data)
  dropdown_menu_place = document.getElementById('loc-search-menu');
  dropdown_menu_source = document.getElementById('source-search-menu');

  json_data.forEach(source => {
      sources_info.appendChild(sourceLogoTempelate(source.image, source.source_tag))

      sources_info.lastChild.firstChild.addEventListener('mouseover', (event) => {
        event.target.classList.add('source-logo-hover')
      })
  
      sources_info.lastChild.firstChild.addEventListener('mouseout', (event) => {
        event.target.classList.remove('source-logo-hover')
      })
  
      sources_info.lastChild.firstChild.addEventListener('click', (event) => {
        createHeatmap(event)
      })
      news_sources[source.source_tag] = {'source-tag':source['source_tag'], 'image-url':source['image']};
      source_index[source.source_tag] = index;
      index += 1;

      dropdown_menu_source.innerHTML += source_dropdown_item.replace('{source}',source['name']).replace('{source-id}',source.source_tag)

      for(const [place, data] of Object.entries(source.data)){
        if(!places.includes(place)){
          places.push(place);
        }
      }
  });

  for(var i=0;i<dropdown_menu_source.children.length;i++){
    dropdown_menu_source.children[i].addEventListener('click',(event)=>{
      createHeatmap({target:document.getElementById('sources-info').children[source_index[event.target.getAttribute('sourceid')]].children[0]})
      for(var i=0;i<dropdown_menu_source.children.length;i++){
        dropdown_menu_source.children[i].classList.remove('menu-item-selected');
      }
      event.target.classList.add('menu-item-selected');
    })
  }

  places.sort();
  places.unshift("None")
  places.forEach((pl)=>{
    dropdown_menu_place.innerHTML += loc_dropdown_item.replaceAll('{place}',pl,2)
  })

  for(var i=0;i<dropdown_menu_place.children.length;i++){
    dropdown_menu_place.children[i].addEventListener('click',(event)=>{
      for(var i=0;i<dropdown_menu_place.children.length;i++){
        dropdown_menu_place.children[i].classList.remove('menu-item-selected');
      }
      event.target.classList.add('menu-item-selected');

      if(event.target.getAttribute('locid') == "None"){
        source_list.innerHTML = ''; 
        news_list.innerHTML = '';
        document.getElementById("loc-search").textContent = "None"
        query = '?source=' + query_source;
        if (history.pushState) {
          var newurl = window.location.origin + window.location.pathname + query;
          window.history.pushState({path:newurl},'',newurl);
        }
      }

      for(const [place, data] of Object.entries(pins)){
        if(place == event.target.getAttribute('locid')){
          const dic = {
            target:{
              metadata:{
                title: event.target.getAttribute('locid'),
                coordinates: data.coordinates,
                info: data.data
              }
            }
          }
          updateMenu(dic)
        }
      }
    })
  }

  createSignIn()

  //create heatmap after data is retreived
  if(!query_source){
    previous_selcted_map_source =document.getElementById('sources-info').children[0].children[0];
    createHeatmap({target:document.getElementById('sources-info').children[0].children[0]})
  }
  else{
    previous_selcted_map_source = document.getElementById('sources-info').children[source_index[query_source]].children[0];
    createHeatmap({target:previous_selcted_map_source});
  }
}

function initMap(){
  var mapZoom = 5
  if(screen.width <= 810){
    mapZoom = 4
  }
  map = new window.Microsoft.Maps.Map('#plotMap', {
    credentials: 'Asmd15OlhpdjArghMT1ycEvtCYiXMkL2Syp3DO0xxafdxG5JyWEURj2hCxmLNy3s',
    center: new window.Microsoft.Maps.Location(23.5, 83),
    maxZoom: 6,
    minZoom: 4,
    zoom: mapZoom,
    enableDrag:false,
    showMapTypeSelector: false,
    enableSearchLogo: false,
    enableClickableLogo: false,
    showMapTypeSelector: false,
    showDashboard: false,
    disableUserInput: false,
    showMapLabels: false,
    customMapStyle: hiddenCityLabels,
  });
  map.setOptions({
    maxBounds: map.getBounds(),
  });
  fetchData();
}

var map
var hiddenCityLabels = {
  "version": "1.0",
  "elements": {
      "point": {
          "labelVisible": false,
          "visible":false,
      },
      "transportation": {
        "visible": false
      },
      "river": {
        "visible": false
      },
      "vegetation": {
        "visible":false
      },
  }
};


function createHeatmap(event){
  var loc = [];
  pins = [];

  //clear source list and news list
  source_list.innerHTML = ""
  news_list.innerHTML = ''

  //clear pushpins
  for (var i = map.entities.getLength() - 1; i >= 0; i--) {
    var pushpin = map.entities.get(i);
    if (pushpin instanceof Microsoft.Maps.Pushpin) {
        map.entities.removeAt(i);
    }
  }

  //clear heatMap
  map.layers.clear();
  sourceid = event.target.getAttribute('sourceid');

  previous_selcted_map_source.classList.remove('source-logo-selected');
  event.target.classList.add('source-logo-selected')
  
  previous_selcted_map_source = event.target;

  if(sourceid=='all'){
    heat_data = json_data
    document.getElementById('source-search').textContent = "All"
  }
  else{
    heat_data = [json_data[source_index[sourceid]-1]]
    document.getElementById('source-search').textContent = json_data[source_index[sourceid]-1].name;

    //create source logo object to indicate selected source
    const link_list_item = document.getElementById('news_list');
    link_list_item.innerHTML = "";
  }

  //create heat data
  heat_data.forEach(source => {
    for(const [place, data] of Object.entries(source.data)){
      if(!(place in pins)){
        pins[place] = {}
        pins[place]['coordinates'] = [data.coordinates[0], data.coordinates[1]]
        pins[place]['data'] = {}
        pins[place]['data'][source.source_tag] = data.links
      }
      else{ 
        pins[place]['data'][source.source_tag] = data.links
      }
      for(let i = 0; i < data.count; i++){
        loc.push(new Microsoft.Maps.Location(data.coordinates[0], data.coordinates[1]))
      }
    }
  });

  //create pushpoints from heat data
  for(const [place, data] of Object.entries(pins)){
    if(place == query_loc){
      const dic = {
        target:{
          metadata:{
            title: query_loc,
            coordinates: data.coordinates,
            info: data.data
          }
        }
      }
      updateMenu(dic)
    }

    var infobox_source_html = '{source-logo}'
    for(const [source, links] of Object.entries(data.data)){
      infobox_source_html = infobox_source_html.replace('{source-logo}',loc_logo_template).replace('{image-url}',news_sources[source]['image-url'])
    }
    var pushpin = new Microsoft.Maps.Pushpin(new Microsoft.Maps.Location(data.coordinates[0], data.coordinates[1]),{
      icon: createNullPoint()
    });
    pushpin.metadata = {
      title: place,
      coordinates: data.coordinates,
      info: data.data
    }
    map.entities.push(pushpin);
    Microsoft.Maps.Events.addHandler(pushpin, 'mouseover', updateMenu);
    Microsoft.Maps.Events.addHandler(pushpin, 'click', updateMenu);

  }

  rad =  50000
  if(window.innerWidth < 700){
    rad = 75000
  }
  //create heatmap
  Microsoft.Maps.loadModule('Microsoft.Maps.HeatMap', function () {
    var heatmap = new Microsoft.Maps.HeatMapLayer(loc, {
        intensity: 0.1,
        radius: rad,
        unit: 'meters', 
        colorGradient: {
            '0': 'Black',
            '0.1': 'Purple',
            '0.4': 'Purple',
            '0.6': 'Red',
            '0.8': 'Yellow',
            '1': 'White'
        }
    });
    map.layers.insert(heatmap);
});
}
const loc_logo_template = 
`<div> 
  <div onclick="updateLinkMenu(event)" style="background-image: url({image-url});" tabindex="-1" class="source-logo" sourceid="{source-id}" place="{place}"></div>
</div>`

const news_item_template = 
`<div class="news-item">
<div>
    <a href="{news-url}" target="_blank"}>
      <img target="_blank" src="{image-url}">
    </a>
</div>
<a href="{news-url}" target="_blank">{title}</a>
</div>`

function sourceLocLogoTempelate(image,source_id,place){
  e = document.createElement('div')
  e.style.backgroundImage = "url({image-url})".replace('{image-url}',image)
  e.setAttribute('sourceid',source_id);
  e.setAttribute('place',place);
  e.classList.add('source-logo');
  e.addEventListener('click',(event)=>{
    updateLinkMenu(event)
  })
  e.addEventListener('mouseover',(event)=>{
    event.target.classList.add('source-logo-hover');
  })
  e.addEventListener('mouseout',(event)=>{
    event.target.classList.remove('source-logo-hover');
  })
  f = document.createElement('div')
  f.appendChild(e)
  return f;
}

//update news + location
function updateMenu(e){
  if(e.target.metadata){
    place_name.textContent = e.target.metadata.title;
    cordinates.textContent = e.target.metadata.coordinates[0] + ", " + e.target.metadata.coordinates[1];
    source_list.innerHTML = '' 

    document.getElementById("loc-search").textContent = e.target.metadata.title;

    for(const [source, links] of Object.entries(e.target.metadata.info)){
      source_list.appendChild(sourceLocLogoTempelate(news_sources[source]['image-url'], source, e.target.metadata.title))
    }
    previous_selcted_source = source_list.firstChild.children[0];
    updateLinkMenu({target:source_list.firstChild.children[0]})
  }
}
var previous_selcted_source;
//update news
function updateLinkMenu(event){

  query_source = event.target.getAttribute('sourceid')
  query_loc = event.target.getAttribute('place')


  previous_selcted_source.classList.remove('source-logo-selected')

  previous_selcted_source = event.target;
  event.target.classList.add('source-logo-selected')
  news_list.innerHTML = "";
  if(!query_source){return;}
  json_data[source_index[query_source]-1].data[query_loc].links.forEach(link_data => {
    var title= link_data.title
    if(title.length > 65 && screen.width<770){
      title = title.substring(0,65) + '. . .'
    }
    news_list.innerHTML += news_item_template
    .replace('{news-url}',link_data.url)
    .replace('{news-url}',link_data.url)
    .replace('{image-url}',link_data.image)
    .replace('{title}',title)
  })
}

function createNullPoint() {
  var c = document.createElement('canvas');
  c.width = 24;
  c.height = 24;
  var ctx = c.getContext('2d');
  ctx.fillStyle = '#f00';
  // Draw a path in the shape of an arrow.
  // Generate the base64 image URL from the canvas.
  return c.toDataURL();
}

function capitalize(place) {  
  var words = place.split(' ');  
  var final = [];  
  words.forEach(element => {  
      final.push(element[0].toUpperCase() + element.slice(1, element.length));  
  });  
  return final.join(' ');  
} 