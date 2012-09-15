var publish = function() {
    $("#publish").click();
};

var back = function() {
    window.history.go(-1);
};

var home = function() {
    location.href = "http://" + location.host;
};

var go = function(loc) {
    location.href = "http://" + location.host + loc;
};

var search = function(query_page) {
    if (location.search.length) {
        var token = location.search.substring(1).split("&");
        var query = {}
        for (var i = 0; i < token.length; i ++) {
            var items = token[i].split("=");
            query[items[0]] = items[1];
        }
        location.href = "http://" + location.host + "/search?key=" + query["key"] + query_page;
    }
};

var up = function() {
    window.scrollTo(0, 0);
};

var down = function() {
    window.scrollTo(0, document.body.scrollHeight);
}
