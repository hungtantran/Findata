export default function GetCookie(cname) {
    var name = cname + '=';
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return '';
}

export function getSelectedKeyIndex(suggestions, selected) {
    var suggestionsLength = 0;
    for (let type in suggestions) {
        suggestionsLength += suggestions[type].length;
    }
    // Mod by suggestionsLength + 1 because there is an extra state of non-selected
    var overallIndex = selected % (suggestionsLength + 1);
    if (overallIndex < 0) {
        overallIndex += suggestionsLength + 1;
    }

    var key;
    var index;
    for (let type in suggestions) {
        if (overallIndex > suggestions[type].length) {
            overallIndex -= suggestions[type].length;
        } else {
            key = type;
            index = overallIndex;
            break;
        }
    }
    return [key, index];
}