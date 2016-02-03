function suppress_default(e){
    e.preventDefault();
}

function contain(e){
    e.stopPropagation();
}

function flip(elem, e){
    if(elem.hasClass("parent")){
	contain(e);
	if (elem.hasClass("closed")){
	    elem.removeClass("closed");
	    elem.children(":not(.parent_text)").removeClass("hidden");
	}else{
	    elem.children(":not(.parent_text)").addClass("hidden");
	    elem.addClass("closed");
	}
	return;
    }
    flip(elem.parent(), e);
    return;
}

function flip_event(e){
    elem = $(e.target);
    flip(elem, e);
}

function setup(){
    $(".parent").click(flip_event);
    $(".no_default").click(suppress_default);
    $(".parent").children(":not(.parent_text)").click(contain);
    $(".parent").filter(".closed").children(":not(.parent_text)").addClass("hidden");
}
