Handlebars.registerHelper("stringify", function(array) {
    var output = []
    for (var i = 0, len = array.length; i < len; i++) {
        output.push(JSON.stringify(array[i]))
    }
    return '[' + output + ']'
});