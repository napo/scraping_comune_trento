//get year
var GET = {};
var query = window.location.search.substring(1).split("&");
for (var i = 0, max = query.length; i < max; i++)
{
    if (query[i] === "") // check for trailing & with no param
        continue;

    var param = query[i].split("=");
    GET[decodeURIComponent(param[0])] = decodeURIComponent(param[1] || "");
}
//alert(GET.year);
if (GET.year==undefined || GET.year=="" || GET.year==2019) {
	year = 2019;
} else {
	year = 2015;
}

var treeViz = (function ($) {
	var _self = {},
		redrawTimer,
		boroughs,
		treeData,
		currentSort = "Comune",
		colors = ["334d5c","45b29e","efc94c","e27a3f","df4949","aeaeae","776355","57385c","4edaef","8db500"]
		barTemplate = '<div class="bar_wrapper cf"><div class="bar" style="width:100%;"><div class="bg"></div></div>\
                        <div class="meta">\
                            <span class="count"></span>\
                            <span class="location"></span>\
                        </div>\
                       </div></div>',
        treeTemplate = '<li><div><span class="Comune"></span><span class="Latino"></span><em></em></div></li>';


    function resizeCanvas() {
    	var viz = $('#viz_wrapper'),
    		canvas = $('#tree_canvas, #hover_canvas').attr("width",viz.outerWidth()).attr("height",viz.outerHeight());
    }
    function formatNumber(number) {
    	var strng = number.toString();
    	if (strng.length > 3) {
 			strng = (strng.slice(0,strng.length - 3) + ',' + strng.slice((strng.length - 3), Math.abs(strng.length)))
	    }
    	return strng;
    }
	function initBars() {
		var total = [],
			max_of_array;

		$.each(boroughs, function(){
			total.push(this.total);
		}); 
		max_of_array = Math.max.apply(Math, total);

		$.each(boroughs, function(index){
			var snippet = $(barTemplate),
				widthPercent = ((this.total / max_of_array) * 100).toFixed(2);
			
			snippet
				.find('.count').html("0%<br>0").end()
				.find(".location").html('<em>'+ this.name +'</em><br>' + formatNumber(this.total)).end()
				.find('.bar').attr("id", "borough-" + index).end()
				.css({"width": widthPercent + '%'})
				.appendTo('#bars');


		});
		resizeCanvas();
	}
	function initTrees() {
		var treeList = $('#trees_grid').find('ul');
		$.each(treeData, function(index){
			var template = $(treeTemplate);
			template
				.css("background-color", "#" + this.color)
				.find('.Comune').text(this.Comune).end()
				.find('.Latino').text(this.Latino).end()
				.find('div').css("background-image","url(trees/"+ this.file +")").end()
				.attr('id', 'tree-' + index)
				.appendTo(treeList);
			processTree(this, index);
		});
		resizeCanvas();
	

		$('.tooltip').tooltipster();
	}

	function processTree(tree, tree_index) {
		$.each(boroughs, function(index){
			var bar = $("#borough-" + index),
				widthPercent = ((tree[this.name] / this.total) * 100).toFixed(6),
				treeSpan = $('<span title="' + tree[currentSort] + ' : ' + formatNumber(tree[this.name]) + ' " data-tree="tree-' + tree_index + '" class="tree-' + tree_index + ' tooltip"></span>');
			treeSpan.data('count', tree[this.name]);
			treeSpan.width(widthPercent + "%").css('background-color', "#" + tree["color"]);
			bar.append(treeSpan);
			
		}); 
	}
	function loadTreeData() {
		var trees = $.getJSON( "data-"+year+"/common.json", function(data) {
				treeData = data;
				initTrees();
				resizeCanvas();
		    });
	}

	function loadBoroughData() {
		var temp = $.getJSON( "data-"+year+"/boroughs.json", function(data) {
				boroughs = data;
				initBars();
				loadTreeData();
		    });
	}
	
	function getArea(spanA, spanB) {

		var vizOffset =  $('#viz_wrapper').offset(),
			spanAOffset = $(spanA).offset(),
			spanBOffset = $(spanB).offset(),
			spanASize = {"width": $(spanA).width(), "height" : $(spanA).height()},
			spanBSize = {"width": $(spanB).width(), "height" : $(spanB).height()},
			pos1Y = spanAOffset.top + spanASize.height - vizOffset.top,
		    pos1X = spanAOffset.left - vizOffset.left,
		    pos2Y = spanAOffset.top + spanASize.height - vizOffset.top,
		    pos2X = spanAOffset.left + spanASize.width - vizOffset.left,
		    pos3Y = spanBOffset.top - vizOffset.top,
		    pos3X = spanBOffset.left + spanBSize.width - vizOffset.left,
		    pos4Y = spanBOffset.top - vizOffset.top,
		    pos4X = spanBOffset.left - vizOffset.left;

		return [pos1X, pos1Y, pos2X, pos2Y, pos3X, pos3Y, pos4X, pos4Y];

	}
	function connectSections(sections, tree, canvas) {

		$.each(sections, function(index){
			var nextItem = sections[index + 1];
			if ((index + 1) == sections.length) {
				nextItem = tree;
			}
			var points = getArea(sections[index], nextItem);
			$( canvas ).drawPath({
			  fillStyle: $(sections[index]).css("background-color"),
			  strokeWidth: 1,
			  p1: {
			    type: 'line',
			    x1: points[0], y1: points[1],
			    x2: points[2], y2: points[3],
			    x3: points[4], y3: points[5],
			    x4: points[6], y4: points[7]
			  }
			});
		});
	}

	function updateBarCounts() {
		$.each(boroughs, function(index){
			var bar = $("#borough-" + index),
				trees = bar.find('.selected'),
				count = 0,
				percent = 0,
				boroughTotal = this.total;
				
			trees.each(function(){
				count += parseInt($(this).data('count'));
			});
			percent = ((count / boroughTotal	) * 100).toFixed(2);
			bar.parent().find('.count').html(percent + '%<br>' + formatNumber(count));
		}); 
	}

	function connectTrees() {
		$('#tree_canvas').clearCanvas();
		$('#bars .selected').removeClass('selected');
		$( "#trees_grid .selected" ).each(function(){
			var sections = $('#bars').find('.' + $( this ).attr('id')).toggleClass('selected');
		  	connectSections(sections, this, '#tree_canvas');
		  	
		});
		updateBarCounts();
	}

	function hilightTree(tree) {
		$('#hover_canvas').clearCanvas();
		
		var sections = $('#bars').find('.' + $( tree ).attr('id'));
		$( tree ).addClass('hover');
		$('#bars').find('.hilite').removeClass('hilite');
		sections.addClass('hilite')
		connectSections(sections, tree, '#hover_canvas');
		
	} 
	function deHilightTree(tree) {
		$('#hover_canvas').clearCanvas();
		if ( tree ) $( tree ).removeClass('hover');
		$('#bars').find('.hilite').removeClass('hilite');

	}


	function sortTrees(prop, asc) {
		treeData = treeData.sort(function(a, b) {
	        if (asc) return (a[prop] > b[prop]) ? 1 : ((a[prop] < b[prop]) ? -1 : 0);
	        else return (b[prop] > a[prop]) ? 1 : ((b[prop] < a[prop]) ? -1 : 0);
	    });
	}

	function resetUI() {
		$('#hover_canvas').clearCanvas();
		$('#tree_canvas').clearCanvas();
		$('#trees_grid').find('ul').empty();
		$.each(boroughs, function(index){
			$("#borough-" + index).find('span').remove();
		}); 
		updateBarCounts();
	}

	function initEvents() {


		$( window ).resize(function() {
			resizeCanvas();
			if (redrawTimer) {
				clearTimeout(redrawTimer);
			}
			redrawTimer = setTimeout(connectTrees,300);

		});
		$( "#trees_grid" ).delegate( "li", "click", function() {
		  	$( this ).toggleClass( "selected" );
		  	connectTrees(); 
		})
		.delegate( "li", "mouseenter", function() {
			if ($(this).hasClass("selected")) {
				return;
			};
		    hilightTree(this)
		})
		.delegate( "li", "mouseleave", function() {
			deHilightTree($(this));
		});
		$( "#bars" ).delegate( " .bar span ", "click", function() {
		  	$('#' + $( this ).data('tree')).toggleClass('selected');
		  	connectTrees(); 
		})
		.delegate( ".bar span ", "mouseenter", function() {
			var tree = $('#' + $( this ).data('tree'));
			if (tree.hasClass("selected")) {
				return;
			};
		    hilightTree(tree)
		})
		.delegate( ".bar span ", "mouseleave", function() {
			var tree = $('#' + $( this ).data('tree'));
			deHilightTree(tree);
		});


		$( "#reset_ui" ).on("click", function(event){
			event.preventDefault();
			$('#trees_grid .selected').removeClass('selected');
			connectTrees();
		})
		$( "#options span" ).on("click", function(event){
			event.preventDefault();
			var newSort;
			if ($(this).hasClass("on")) {
				newSort = $(this).removeClass('on').siblings().addClass('on').data("sort");
				
			} else {
				newSort = $(this).siblings().removeClass('on').end().addClass('on').data("sort");

			}
			currentSort = newSort;
			$("#trees_grid").attr('class', newSort);
			resetUI();
			sortTrees(newSort, true);
			initTrees();
		})


	}
	_self.init = function () {
		loadBoroughData();
		initEvents();
	};
		return _self;

}(jQuery));
jQuery(document).ready(function(){
	treeViz.init(); 
	PointerEventsPolyfill.initialize({});
});
