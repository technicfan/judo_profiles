let special = 0, ground = 0, combination = 0, deleted_rank_items = []

function add_rank_item(type, context = null){
    switch(type){
        case "special":
            special += 1
            var number = special
            var html = `
            <div class="special rank_item" id="special_item` + number + `">
                <p class="number"><b>` + number + `</b></p>
                <select id="special_t` + number + `" class="technique form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>Technik</option>` +
                    techniques +
                `</select>
                <button id="special_b` + number + `" class="btn btn-danger btn-sm" onclick="remove_rank('special', this)">Entfernen</button>
            </div>
            `
            break
        case "ground":
            ground += 1
            var number = ground
            var html = `
            <div class="ground rank_item" id="ground_item` + number + `">
                <p class="number"><b>` + number + `</b></p>
                <select id="ground_t` + number + `" class="technique form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>Technik</option>` +
                    gtechniques +
                `</select>
                <button id="ground_b` + number + `" class="btn btn-danger btn-sm" onclick="remove_rank('ground', this)">Entfernen</button>
            </div>
            `
            break
        case "combination":
            combination += 1
            var number = combination
            var html = `
            <div class="combination rank_item" id="combination_item` + number + `">
                <p class="number"><b>` + number + `</b></p>
                <select id="combination_t1` + number + `" class="technique1 form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>1. Technik</option>` +
                    techniques +
                `</select>
                <select id="combination_t2` + number + `" class="technique2 form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>2. Technik</option>` +
                    techniques +
                `</select>
                <button id="combination_b` + number + `" class="btn btn-danger btn-sm" onclick="remove_rank('combination', this)">Entfernen</button>
            </div>
            `
            break
    }
    if (number <= 4){
        $("#" + type + number).append(html)
        var div = document.getElementById(type + "_item" + number)
        div.querySelector("button").addEventListener("click", event => { event.preventDefault() })

        if (context != null) {
            div.setAttribute("data-id", context["id"])
            if (type == "combination"){
                div.querySelector(".technique1").value = context["technique1"]
                div.querySelector(".technique2").value = context["technique2"]
            } else {
                div.querySelector(".technique").value = context["technique"]
            }
        }
    } else {
        switch(type){
            case "special":
                special -= 1
                break
            case "ground":
                ground -= 1
                break
            case "combination":
                combination -= 1
                break
        }
    }
}

function remove_rank(type, element){
    var number = element.id.slice(-1)
    if (document.getElementById(type + "_item" + number).getAttribute("data-id")){
        deleted_rank_items.push({
            "type": type,
            "id": parseInt(document.getElementById(type + "_item" + number).getAttribute("data-id"))
        })
    }
    $("#" + type + "_item" + number).remove()
    if (number < 4) {
        document.querySelectorAll("." + type + ".rank_item").forEach(div => {
            var curr_number = parseInt(div.id.slice(-1))
            div.querySelectorAll("select, button").forEach(select => {
                if(curr_number > number) {
                    select.id = select.id.slice(0, -1) + (curr_number - 1)
                }
            })
            if(curr_number > number) {
                let id = div.id
                $("#" + type + (curr_number - 1)).append(div)
                var div = document.getElementById(id)
                div.querySelector("p").innerHTML = "<b>" + (curr_number - 1)  + "</b>"
                div.id = div.id.slice(0, -1) + (curr_number - 1)
            }
        })
    }

    switch(type){
            case "special":
                special -= 1
                break
            case "ground":
                ground -= 1
                break
            case "combination":
                combination -= 1
                break
        }
}
