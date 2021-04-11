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

            dialogData = '<dialog id = "dialogAcronymExt">';

            dialogData += 'The following potential acronyms were detected: <br>';

            for (let t of results) {
                t = t.sort(function (a, b) {
                    return b.count - a.count;
                })

                //console.log(results)
                console.log(t)
                //console.log(typeOf(t[0].acronym))

                dialogData += '<button class="accordion">' + t[0].acronym + '</button>';
                dialogData += '<div class="panel" style="display: none;">'

                for (let r of t) {
                    //console.log(r);

                    dialogData += '<input type="checkbox" class = "selections" meshID = "' + r.meshID;
                    dialogData += '" acronym="' + r.acronym + '" phrase="' + r.phrase + '"\>';
                    dialogData += r.phrase.toUpperCase() + ' (' + r.count + ')<br>';
                }
                dialogData += '</div>'
            }

            //console.table(results);

            dialogData += '</ol><br>Select desired phrases:<br><br>';
            dialogData += '<input id="containAcronyms" type="checkbox">Retain acronym in search query?<br>';

            dialogData += '<button id = "dialogClose" style = "float: left; background-color: #ffffff; border: 1px solid black; border-color: #20558a; color: #20558a;">Close</button>' // search button
            dialogData += '<label id = "notFound" style = "color: red; padding-left: 10px;"></label>';
            dialogData += '<button id = "dialogSearch" style = "float: right; background-color: #20558a;">Search</button></dialog> ';

            document.body.innerHTML += dialogData;

            /*
            let acc = document.getElementsByName("selections");

            //iterate through accordian buttons add event listener to show/unshow elements
            for (let i = 0; i < acc.length; i++) {
                acc[i].addEventListener("click", function () {
                    this.classList.toggle("active");
                    var panel = this.nextElementSibling;
                    if (panel.style.display === "block") {
                        panel.style.display = "none";
                    } else {
                        panel.style.display = "block";
                    }
                });
            }
            */

            var dialog = document.getElementById("dialogAcronymExt");

            let acc = dialog.querySelectorAll("[class = 'accordion']");

            //iterate through accordian buttons add event listener to show/unshow elements
            for (let i = 0; i < acc.length; i++) {
                acc[i].addEventListener("click", function () {
                    this.classList.toggle("active");
                    var panel = this.nextElementSibling;
                    if (panel.style.display === "block") {
                        panel.style.display = "none";
                    } else {
                        panel.style.display = "block";
                    }
                });
            }

            dialog.querySelector("button[id = 'dialogSearch']").addEventListener("click", function () {
                var phraseSelected = false;
                let checkboxes = dialog.getElementsByClassName('selections');
                let replaceAcronym = document.querySelector("[id = 'containAcronyms']");

                var newPhraseString = "";

                for (let c of checkboxes) {
                    if (c.checked == true) {
                        phraseSelected = true;
                        let acronym = c.getAttribute('acronym');
                        let phrase = c.getAttribute('phrase');
                        let meshID = c.getAttribute('meshid');



                        if (meshID.startsWith('D')) {
                            newPhraseString += ' ' + phrase + '[MeSH Terms]';
                        } else if (meshID.startsWith('C')) {
                            newPhraseString += ' ' + phrase + '[Supplementary Concept]';
                        }

                        if (!replaceAcronym.checked) {
                            searchTerm = searchTerm.replace(acronym, '');
                        }
                    }
                }

                if (phraseSelected) {
                    console.log(searchTerm);
                    window.location.href = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + searchTerm + newPhraseString;
                } else {
                    //notFound = 'No phrase selected';
                    //document.getElementById('notFound').innerHTML = notFound.fontcolor('red');
                    document.getElementById('notFound').innerHTML = 'No phrase selected'
                    //alert('no items selected');
                    //console.log('no items selected');
                }
            })



            dialog.querySelector("button[id = 'dialogClose']").addEventListener("click", function () {
                dialog.close();
            })
            /*
            dialog.style.position = 'fixed';
            dialog.style.backgroundColor = '#ffffff';
            dialog.style.color = '#20558a';
            dialog.style.top = '0%';
            dialog.style.right = '-60%';
            dialog.style.padding = '1%';
            */
            dialog.showModal();

            window.localStorage.setItem('acronymDetector', 'skip');
            
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
if (localStorage.getItem('acronymDetector') === null) {
    searchTermList.forEach(function (term) {
        searchFunction(term, generateDialogBox);
    })
} else {
    window.localStorage.removeItem('acronymDetector');
}
