let own0 = 0, own1 = 0, own2 = 0, own3 = 0, own4 = 0, own5 = 0, deleted_own_techniques = []

function add_own(field, context = null){
    switch(field){
        case 0:
            own0 += 1
            number = own0
            break
        case 1:
            own1 += 1
            number = own1
            break
        case 2:
            own2 += 1
            number = own2
            break
        case 3:
            own3 += 1
            number = own3
            break
        case 4:
            own4 += 1
            number = own4
            break
        case 5:
            own5 += 1
            number = own5
            break
    }
    if (number <= 3){
        own_technique_html = `
        <div class="own_technique" id="own` + field + "_" + number + `">
            <select id="own` + field + "_d" + number + `" class="direction">
                <option value="" selected>Auslage</option>
                <option value="l">Links</option>
                <option value="r">Rechts</option>
            </select>
            <select id="own` + field + "_t" + number + `" class="technique">
                <option value="" selected>Technik</option>` +
            stechniques +
            `</select>
            <select id="own` + field + "_pl" + number + `" class="select_position left">
                <option value="" selected>linke Griffposition</option>
            </select>
            <select id="own` + field + "_pr" + number + `" class="select_position right">
                <option value="" selected>rechte Griffposition</option>
            </select>
            <select id="own` + field + "_s" + number + `" class="state">
                <option value="" selected>Stand</option>
                <option value="W">wettkampfsicher</option>
                <option value="T">Training</option>
                <option value="Z">zu lernen</option>
            </select>
            <button id="own` + field + "_b" + number + `" onclick="remove_own(` + field + `, this)">Löschen</button>
        </div>
        `

        $("#own" + field).append(own_technique_html)
        let div = document.getElementById("own" + field + "_" + number)
        document.getElementById("own" + field + "_" + number).querySelectorAll("button").forEach(button => {
            button.addEventListener("click", event => { event.preventDefault() })
        })
        document.querySelectorAll(".move").forEach(position => {
            if (position.style.display == "flex"){
                $("#" + "own" + field + "_" + "p" + position.className[0] + number).append(
                    '<option value="' + position.className.slice(-1) + '">' + position.className.slice(-1) + '</option>'
                )
            }
        })
        if (context != null) {
            div.setAttribute("data-id", context["id"])
            div.querySelector(".direction").value = context["side"]
            div.querySelector(".technique").value = context["technique"]
            div.querySelector(".left").value = context["left"]
            div.querySelector(".right").value = context["right"]
            div.querySelector(".state").value = context["state"]
        }
    } else {
        switch(field){
            case 0:
                own0 -= 1
                break
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
            case 5:
                own5 -= 1
                break
        }
    }
}

function remove_own(field, element){
    number = element.id.slice(-1)
    if (document.getElementById("own" + field + "_" + number).getAttribute("data-id")){
        deleted_own_techniques.push(parseInt(document.getElementById("own" + field + "_" + number).getAttribute("data-id")))
    }
    $("#own" + field + "_" + number).remove()
    if (number < 3) {
        document.getElementById("own" + field).querySelectorAll("div").forEach(div => {
            curr_number = parseInt(div.id.slice(-1))
            div.querySelectorAll("select, button").forEach(select => {
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
            case 0:
                own0 -= 1
                break
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
            case 5:
                own5 -= 1
                break
        }
}
