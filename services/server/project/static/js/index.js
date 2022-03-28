
var area_table = $('#area-table').DataTable();
area_table;


var baseLayer = L.tileLayer(
  'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution: '...',
    maxZoom: 18
  }
);

var greenIcon = L.icon({
    iconUrl: 'https://cdn.iconscout.com/icon/premium/png-256-thumb/virus-71-568647.png',

    iconSize:     [50, 50], // size of the icon// point of the icon which will correspond to marker's location// the same for the shadow
    popupAnchor:  [-3, -10] // point from which the popup should open relative to the iconAnchor
});
var redIcon = L.icon({
    iconUrl: 'https://cdn3.iconfinder.com/data/icons/science-116/64/virus-lab-scientist-biology-cell-medical-512.png',

    iconSize:     [50, 50], // size of the icon// point of the icon which will correspond to marker's location// the same for the shadow
    popupAnchor:  [-3, -10] // point from which the popup should open relative to the iconAnchor
});


var cfg = {
  // radius should be small ONLY if scaleRadius is true (or small radius is intended)
  // if scaleRadius is false it will be the constant radius used in pixels
  "radius": 2,
  "maxOpacity": .8,
  // scales the radius based on map zoom
  "scaleRadius": true,
  // if set to false the heatmap uses the global maximum for colorization
  // if activated: uses the data maximum within the current map boundaries
  //   (there will always be a red spot with useLocalExtremas true)
  "useLocalExtrema": true,
  // which field name in your data represents the latitude - default "lat"
  latField: 'lat',
  // which field name in your data represents the longitude - default "lng"
  lngField: 'lng',
  // which field name in your data represents the data value - default "value"
  valueField: 'count'
};


function markonClick(e) {
	area_name = e.target._popup._content.split(" ")[0];
			$.ajax({
		url: '/api/getlocation/' + area_name,
		type: "GET",
		success: function (msg) {
			area_table.clear();
			d = [msg['provinceName'], msg['all_confirmed'],msg['update_confirmed'],msg['all_cured'],msg['update_cured'],msg['all_dead'],msg['update_dead']];
			area_table.row.add(d).draw();
		}, error: function (msg) {
			console.log('無法送出');
		}
	});

}

var heatmapLayer = new HeatmapOverlay(cfg);
var map = new L.Map('map-canvas', {
  center: new L.LatLng(23.5, 121),
  zoom: 6,
  layers: [baseLayer, heatmapLayer]
});
    for(i=0;i<testData.data.length;i++){
        if(testData.data[i].type == "green") {
        	loc_name = testData.data[i]["name"];
            L.marker([testData.data[i]["lat"], testData.data[i]["lng"]], {icon: greenIcon}).addTo(map).bindPopup(loc_name + " 確診人數： " + testData.data[i]["count"]).on('click', function(e){markonClick(e)});
        }
        else{
        	loc_name = testData.data[i]["name"];
            L.marker([testData.data[i]["lat"], testData.data[i]["lng"]], {icon: redIcon}).addTo(map).bindPopup(loc_name + " 確診人數： " + testData.data[i]["count"]).on('click', function(e){markonClick(e)});
        }
        }
heatmapLayer.setData(testData);



    (function ($) {
	$.fn.countTo = function (options) {
		options = options || {};

		return $(this).each(function () {
			// set options for current element
			var settings = $.extend({}, $.fn.countTo.defaults, {
				from:            $(this).data('from'),
				to:              $(this).data('to'),
				speed:           $(this).data('speed'),
				refreshInterval: $(this).data('refresh-interval'),
				decimals:        $(this).data('decimals')
			}, options);

			// how many times to update the value, and how much to increment the value on each update
			var loops = Math.ceil(settings.speed / settings.refreshInterval),
				increment = (settings.to - settings.from) / loops;

			// references & variables that will change with each update
			var self = this,
				$self = $(this),
				loopCount = 0,
				value = settings.from,
				data = $self.data('countTo') || {};

			$self.data('countTo', data);

			// if an existing interval can be found, clear it first
			if (data.interval) {
				clearInterval(data.interval);
			}
			data.interval = setInterval(updateTimer, settings.refreshInterval);

			// initialize the element with the starting value
			render(value);

			function updateTimer() {
				value += increment;
				loopCount++;

				render(value);

				if (typeof(settings.onUpdate) == 'function') {
					settings.onUpdate.call(self, value);
				}

				if (loopCount >= loops) {
					// remove the interval
					$self.removeData('countTo');
					clearInterval(data.interval);
					value = settings.to;

					if (typeof(settings.onComplete) == 'function') {
						settings.onComplete.call(self, value);
					}
				}
			}

			function render(value) {
				var formattedValue = settings.formatter.call(self, value, settings);
				$self.html(formattedValue);
			}
		});
	};

	$.fn.countTo.defaults = {
		from: 0,               // the number the element should start at
		to: 0,                 // the number the element should end at
		speed: 1000,           // how long it should take to count between the target numbers
		refreshInterval: 100,  // how often the element should be updated
		decimals: 0,           // the number of decimal places to show
		formatter: formatter,  // handler for formatting the value before rendering
		onUpdate: null,        // callback method for every time the element is updated
		onComplete: null       // callback method for when the element finishes updating
	};

	function formatter(value, settings) {
		return value.toFixed(settings.decimals);
	}
}(jQuery));

jQuery(function ($) {
  // custom formatting example
  $('.count-number').data('countToOptions', {
	formatter: function (value, options) {
	  return value.toFixed(options.decimals).replace(/\B(?=(?:\d{3})+(?!\d))/g, ',');
	}
  });

  // start all the timers
  $('.timer').each(count);

  function count(options) {
	var $this = $(this);
	options = $.extend({}, options || {}, $this.data('countToOptions') || {});
	$this.countTo(options);
  }
});


var example_table = $('#example').DataTable();
example_table;
//
// $(document).ready(function() {
//     $('#example').DataTable( {
//         "serverSide": true,
// 		"processing": true,
//         "ajax": "api/getlazy"
//     } );
// } );