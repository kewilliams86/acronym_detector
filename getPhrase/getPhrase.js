function searchFunction(term, callback) {

    //console.log(term)
    var xhttp = new XMLHttpRequest();

    xhttp.onload = function() {

        // only generate phrases if request succeeds
        // if valid acronym, www.path.to/json/ACRONYM will exist
        try {
            if (this.readyState == 4 && this.status == 200) {
                query = JSON.parse(this.responseText);
                // get array of objects containing acronym, phrase, count, and MeSH ID
                let phraseList = query.map(function (element) { return element });
                results.push(phraseList); // make multidimensional array, index for each found acronym
            }
        } catch (err) { // ??? if word not acronym, not sure how to handle this as error occasionally occurred without
            console.log(term + ' not found');
        } finally {
            callback(); // call generateDialogBox
        }
        
    }

    //xhttp.open("GET", 'https://my-json-server.typicode.com/kewilliams86/demo/' + term, true);
    xhttp.open("GET", 'https://bioinformatics.easternct.edu/BCBET2/findphrase.php?q=' + term, true);
    xhttp.send();
}

function generateDialogBox() {
    waiting--; // wait for all pages to load
    if (waiting == 0) {

        //console.log(results)
        if (results.length > 0) { // if any matches found

            let optionCnt = 0; // number to increment when creating option values
            let acronymCnt = 0; // number to increment when creating acronym ids

            //begin generation of dialog box and initialize unordered list of acronyms
            dialogData = '<dialog id = "dialogAcronymExt"> The following potential acronyms were detected: <br><ol>'

            
            for (let t of results) { // add acronym and dropbox for each associated phrase to list
                t = t.sort(function (a, b) { // sort phrases by count - highest to lowest
                    return b.count - a.count;
                })
                dialogData += '<li>' + t[0].acronym.toUpperCase() + '</li>'; // add acronym to list
                dialogData += '<div class="modal-body"><select id="acronym' + acronymCnt + '">' // generate dropbox for each phrase
                dialogData += '<option value="phrase' + optionCnt + '"></option > '; // blank phrase option, no name attribute

                for (let r of t) { // generate option with value=phrase#, name=acronym, and text='phrase and its count'
                    optionCnt++;
                    dialogData += '<option value="phrase' + optionCnt + '" name="' + r.acronym + '">';
                    dialogData += r.phrase.toUpperCase() + ' (' + r.count + ')';
                    dialogData += '</option >';
                }
                dialogData += '</select>';
                acronymCnt++;
            }

            console.table(results);

            dialogData += '</ol>';
            dialogData += '<label id = "notFound" style = "color: red; padding-left: 10px;"></label><br>'; // label for no selection made ??? not sure if wanted
            dialogData += '<button id = "dialogSearch" style = "float: left;">Search</button>' // search button
            dialogData += '<button id = "dialogClose" style = "float: right;">Close</button></dialog> '; // close button

            document.body.innerHTML += dialogData; // insert dialog box into pubmed page

            let dialog = document.getElementById("dialogAcronymExt"); //access newly inserted dialog box for button interactions

            // code to be executed when search button is clicked
            dialog.querySelector("button[id = 'dialogSearch']").addEventListener("click", function () {
                var phraseSelected = false;
                for (i = 0; i < acronymCnt; i++) { // loop through found acronyms
                    let input = document.getElementById("acronym" + i); // retrieve each acronym by id
                    input = input.options[input.selectedIndex]; // modify input to contain current option selected
                    acronym = input.getAttribute('name'); // retrieve phrase selected for acronym (null if none)
                    //console.log(acronym);
                    // if phrase selected, change flag, retrieve phrase, remove count '(###)', and replace acronym in search string with mesh term
                    if (acronym != null) {
                        phraseSelected = true
                        phrase = input.text.split(' ');
                        phrase = phrase.slice(0, phrase.length - 1).join(' ');
                        //console.log(phrase);
                        searchTerm = searchTerm.replace(acronym, phrase + '[MeSH Terms]');
                    }
                }
                if (phraseSelected) { // if phrase selected, reload pubmed webpage with modified search string
                    //console.log(searchTerm);
                    window.location.href = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + searchTerm;
                } else {
                    document.getElementById('notFound').innerHTML = 'No phrase selected'; // ??? what to do when no selection
                    //alert('no items selected');
                    //console.log('no items selected');
                }
            })
            // exit dialog on close button click
            dialog.querySelector("button[id = 'dialogClose']").addEventListener("click", function () {
                dialog.close();
            })
            // dialog style settings
            dialog.style.position = 'absolute';
            dialog.style.color = '#20558a';
            dialog.style.top = '-60%';
            dialog.style.right = '-60%';
            dialog.style.padding = '1%';
            dialog.showModal();
        }
    }
}

var results = [];
var searchTerm = $('input[name="term"]')[0].value.toUpperCase(); // get search term

//searchTermList = searchTerm.split(' '); // split terms into list

// remove ' " ( ) to allow detect of acronym next to these characters ??? not sure if good idea
var searchTermList = searchTerm.replace(/[/()'"]/g, '').split(' ');
//updateSearchTerm = searchTerm.replace(/[/()'"]/g, '');
//searchTermList = updateSearchTerm.split(' ');

var waiting = searchTermList.length // get number of words to track when all executions of searchFunction() complete

//console.log(searchTermList);
//loop through all words, find matches and execute finish 
searchTermList.forEach(function (term) { 
    searchFunction(term, generateDialogBox)
})