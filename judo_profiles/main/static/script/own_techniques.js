let own1 = 1, own2 = 1, own3 = 1, own4 = 1;

function add_own(field, context = null){
    switch(field){
        case 1:
            number = own1
            break
        case 2:
            number = own2
            break
        case 3:
            number = own3
            break
        case 4:
            number = own4
            break
    }
    if (number <= 3){
        own_technique_html = `
        <div class="own_technique" id="own` + field + "_" + number + `">
            <select id="own` + field + "_" + "d" + number + `" class="direction">
                <option value="" selected>Auslage</option>
                <option value="l">Links</option>
                <option value="r">Rechts</option>
            </select>
            <select id="own` + field + "_" + "t" + number + `" class="technique">
                <option value="" selected>Technik</option>` +
            techniques +
            `</select>
            <select id="own` + field + "_" + "pl" + number + `" class="select_position left">
                <option value="" selected>linke Griffposition</option>
            </select>
            <select id="own` + field + "_" + "pr" + number + `" class="select_position right">
                <option value="" selected>rechte Griffposition</option>
            </select>
            <select id="own` + field + "_" + "s" + number + `" class="state">
                <option value="" selected>Stand</option>
                <option value="W">wettkampfsicher</option>
                <option value="T">Training</option>
                <option value="Z">zu lernen</option>
            </select>
            <button onclick="remove_own(` + field + ", " + number + `)">Löschen</button>
        </div>
        `

        $("#own" + field).append(own_technique_html)
        document.getElementById("own" + field + "_" + number).querySelectorAll("button").forEach(button => {
            button.addEventListener("click", event => { event.preventDefault() })
        })
        if (context != null) {
            document.getElementById("own" + field + "_t" + number).value = number
        }
        document.querySelectorAll(".move").forEach(position => {
            if (position.style.display == "flex"){
                $("#" + "own" + field + "_" + "p" + position.className[0] + number).append(
                    '<option value="' + position.className.slice(-1) + '">' + position.className.slice(-1) + '</option>'
                )
            }
        })

        switch(field){
            case 1:
                own1 += 1
                break
            case 2:
                own2 += 1
                break
            case 3:
                own3 += 1
                break
            case 4:
                own4 += 1
                break
        }
    }
}

function remove_own(field, number){
    $("#own" + field + "_" + number).remove()
    if (number < 3) {
        document.getElementById("own" + field).querySelectorAll("div").forEach(div => {
            curr_number = parseInt(div.id.slice(-1))
            console.log(curr_number)
            div.querySelectorAll("select").forEach(select => {
                if(curr_number > number) {
                    select.id = select.id.slice(0, -1) + (curr_number - 1)
                }
            })
            if(curr_number > number) {
                div.id = div.id.slice(0, -1) + (curr_number - 1)
            }
        })
    }

    switch(field){
            case 1:
                own1 -= 1
                break
            case 2:
                own2 -= 1
                break
            case 3:
                own3 -= 1
                break
            case 4:
                own4 -= 1
                break
        }
}
