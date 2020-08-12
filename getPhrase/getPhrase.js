/*
// checkboxes

function searchFunction(term, callback) {

    console.log(term)
    var xhttp = new XMLHttpRequest();

    xhttp.onload = function() {

        // only performing code if request succeeds
        // if valid acronym, www.path.to/json/ACRONYM will exist
        if (this.readyState == 4 && this.status == 200) {
            query = JSON.parse(this.responseText);
            // list comprehension (kind of) to get iterable list of dictionaries
            phraseList = query.map(function(element) {return element});
            for (p of phraseList) { // add term key with value to each phrase
                p['term'] = term;

            }
            //phraseList.push({key: 'term', value: term});
            results = results.concat(phraseList);
            //console.log(results);
        }
        callback();
        
    }

    xhttp.open("GET", 'https://my-json-server.typicode.com/kewilliams86/demo/' + term, true);
    //xhttp.open("GET", 'http://bioinformatics.easternct.edu/BCBET2/findphrase.php?q=' + term, true);
    xhttp.send();
}

function finish() {
    waiting--; // wait for all pages to load
    if (waiting == 0) {

        //console.log(results)
        if (results.length > 0) { // if any matches found
            dialogData = '<dialog>Potential acronym for ' + searchTerm + ':<br><br>The following phrase(s) are linked \
            to your search:  <br>';

            let i = 1;
            for (let r of results) { // create links for all associated phrases
                console.log(r[0]);
                //searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + r.phrase + '[MeSH Terms] ' + searchTerm.replace(r.term, '');
                //searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + r.phrase.toUpperCase() + '[MeSH Terms]';
                //dialogData += '<li><a href = "' + searchString + '">' + r.phrase + '</a></li>';
                
                dialogData += '<input type="checkbox" id="term + ' + i + '" name="term' + i +'" value="' + r.phrase.toUpperCase() + '"/>';
                dialogData += '<label for="term' + i + '">' + r.phrase.toUpperCase() + '</label>'
                i++;
            }

            dialogData += '<br>Click phrase to improve search results<br><br><button>Close</button></dialog>';

            document.body.innerHTML += dialogData;
            
            var dialog = document.querySelector("dialog");
        
            dialog.querySelector("button").addEventListener("click", function() {
                dialog.close();
            })
            
            dialog.style.top = '15%';
            dialog.style.right = '-70%';
            dialog.style.padding = '1%';
            dialog.showModal();
        }
    }
}

var results = [];
var searchTerm = $('input[name="term"]')[0].value.toUpperCase(); // get search term
searchTermList = searchTerm.split(' '); // split terms into list
waiting = searchTermList.length // get number of words
//console.log(searchTermList);
//loop through all words, find matches and execute finish 
searchTermList.forEach(function (term) { 
    searchFunction(term, finish)
})
*/


// multiple terms and retain unmmodified query

function searchFunction(term, callback) {

    console.log(term)
    var xhttp = new XMLHttpRequest();

    xhttp.onload = function() {

        // only performing code if request succeeds
        // if valid acronym, www.path.to/json/ACRONYM will exist
        if (this.readyState == 4 && this.status == 200) {
            query = JSON.parse(this.responseText);
            // list comprehension (kind of) to get iterable list of dictionaries
            phraseList = query.map(function(element) {return element});
            for (p of phraseList) { // add term key with value to each phrase
                p['term'] = term;

            }
            //phraseList.push({key: 'term', value: term});
            results = results.concat(phraseList);
            //console.log(results);
        }
        callback();
        
    }

    xhttp.open("GET", 'https://my-json-server.typicode.com/kewilliams86/demo/' + term, true);
    //xhttp.open("GET", 'http://bioinformatics.easternct.edu/BCBET2/findphrase.php?q=' + term, true);
    xhttp.send();
}

function finish() {
    waiting--; // wait for all pages to load
    if (waiting == 0) {

        //console.log(results)
        if (results.length > 0) { // if any matches found
            dialogData = '<dialog>Potential acronym for ' + searchTerm + ':<br><br>The following phrase(s) are linked \
            to your search:  <br><ul>';

            //console.log(results);
            for (let r of results) { // create links for all associated phrases
                //console.log(r);
                //searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + r.phrase + '[MeSH Terms] ' + searchTerm;
                searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + r.phrase.toUpperCase() + '[MeSH Terms] ' + searchTerm.replace(r.term, '');
                dialogData += '<li><a href = "' + searchString + '">' + r.phrase + '</a></li>';
                //dialogData += '<li><a href = "' + searchString + '">' + r.phrase + '</a> ' + r.meshID + '</li>'; // random testing thing
            }

            dialogData += '</ul>Click phrase to improve search results<br><br><button>Close</button></dialog>';

            document.body.innerHTML += dialogData;
            
            var dialog = document.querySelector("dialog");
        
            dialog.querySelector("button").addEventListener("click", function() {
                dialog.close();
            })
            
            dialog.style.top = '15%';
            dialog.style.right = '-70%';
            dialog.style.padding = '1%';
            dialog.showModal();
        }
    }
}

var results = [];
var searchTerm = $('input[name="term"]')[0].value.toUpperCase(); // get search term
searchTermList = searchTerm.split(' '); // split terms into list
waiting = searchTermList.length // get number of words
//console.log(searchTermList);
//loop through all words, find matches and execute finish 
searchTermList.forEach(function (term) { 
    searchFunction(term, finish)
})


/*

// Multiple Terms

function searchFunction(term, callback) {

    console.log(term)
    var xhttp = new XMLHttpRequest();

    xhttp.onload = function() {

        // only performing code if request succeeds
        // if valid acronym, www.path.to/json/ACRONYM will exist
        if (this.readyState == 4 && this.status == 200) {
            query = JSON.parse(this.responseText);
            // list comprehension (kind of) to get iterable list of dictionaries
            phraseList = query.map(function(element) {return element});
            results = results.concat(phraseList);
            //console.log(results);
        }
        callback();
        
    }

    xhttp.open("GET", 'https://my-json-server.typicode.com/kewilliams86/demo/' + term, true);
    //xhttp.open("GET", 'http://bioinformatics.easternct.edu/BCBET2/findphrase.php?q=' + term, true);
    xhttp.send();
}

function finish() {
    waiting--; // wait for all pages to load
    if (waiting == 0) {

        //console.log(results)
        if (results.length > 0) { // if any matches found
            dialogData = '<dialog>Potential acronym for ' + searchTerm + ':<br><br>The following phrase(s) are linked \
            to your search:  <br><ul>';

            for (let r of results) { // create links for all associated phrases
                console.log(r[0]);
                //searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + r.phrase + '[MeSH Terms] ' + searchTerm;
                searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + r.phrase.toUpperCase() + '[MeSH Terms]';
                dialogData += '<li><a href = "' + searchString + '">' + r.phrase + '</a></li>';
                //dialogData += '<li><a href = "' + searchString + '">' + r.phrase + '</a> ' + r.meshID + '</li>'; // random testing thing
            }

            dialogData += '</ul>Click phrase to improve search results<br><br><button>Close</button></dialog>';

            document.body.innerHTML += dialogData;
            
            var dialog = document.querySelector("dialog");
        
            dialog.querySelector("button").addEventListener("click", function() {
                dialog.close();
            })
            
            dialog.style.top = '15%';
            dialog.style.right = '-70%';
            dialog.style.padding = '1%';
            dialog.showModal();
        }
    }
}

var results = [];
var searchTerm = $('input[name="term"]')[0].value.toUpperCase(); // get search term
searchTermList = searchTerm.split(' '); // split terms into list
waiting = searchTermList.length // get number of words
//console.log(searchTermList);
//loop through all words, find matches and execute finish 
searchTermList.forEach(function (term) { 
    searchFunction(term, finish)
})

*/

// Single Term

/*
var phraseList;

function getInfo(searchTerm) {

    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        // only performing code if request succeeds
        // if valid acronym, www.path.to/json/ACRONYM will exist
        if (this.readyState == 4 && this.status == 200) {
            query = JSON.parse(this.responseText);
            // list comprehension (kind of) to get iterable list of dictionaries
            phraseList = query.map(function(element) {return element});

            // collect data for dialogbox
            dialogData = '<dialog>Potential acronym for ' + searchTerm + ':<br><br>The following phrase(s) are linked \
                        to your search:  <br><ul>';
            for (let p of phraseList) { // create links for all associated phrases
                searchString = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + p.phrase + '[MeSH Terms] ';
                dialogData += '<li><a href = "' + searchString + '">' + p.phrase + '</a></li>';
                //dialogData += '<li><a href = "' + searchString + '">' + p.phrase + '</a> ' + p.meshID + '</li>'; // random testing thing
            }
            dialogData += '</ul>Click phrase to improve search results<br><br><button>Close</button></dialog>';

            document.body.innerHTML += dialogData;
            var dialog = document.querySelector("dialog");
            dialog.querySelector("button").addEventListener("click", function() {
                dialog.close();
            })
            dialog.style.top = '15%';
            dialog.style.right = '-70%';
            dialog.style.padding = '1%';
            dialog.showModal();
        }
    }
    xhttp.open("GET", 'https://my-json-server.typicode.com/kewilliams86/demo/' + searchTerm, true);
    //xhttp.open("GET", 'http://bioinformatics.easternct.edu/BCBET2/findphrase.php?q=' + searchTerm, true);
    xhttp.send();
};


var searchTerm = $('input[name="term"]')[0].value.toUpperCase(); // get search term
getInfo(searchTerm);

*/