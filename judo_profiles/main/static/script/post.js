function get_positions(){
    let pos = []
    document.querySelectorAll(".move").forEach(position => {
        if (position.getAttribute("data-id")) {
            action = "update"
            id = parseInt(position.getAttribute("data-id"))
        } else {
            action = "add"
            id = null
        }
        if (position.style.display == "flex"){
            let x = getRelative(position)
            pos.push(
                {
                    "number": parseInt(position.className.slice(-1)),
                    "side": position.className[0] == "l",
                    "x": x[1],
                    "y": x[0],
                    "action": action,
                    "id": id
                }
            )
        } else if (id != null) {
            pos.push(
                {
                    "action": "delete",
                    "id": id
                }
            )
        }
    })
    return pos
}

function get_own_techniques(){
    let own_techniques = []
    document.querySelectorAll(".own_technique").forEach(div => {
        let side = div.querySelector(".direction").value == "l"
        let technique = div.querySelector(".technique").value
        let left = div.querySelector(".select_position.left").value
        let right = div.querySelector(".select_position.right").value
        let state = div.querySelector(".state").value
        let direction = div.id[3]
        if (technique && left && right && state && direction){
            if (div.getAttribute("data-id")) {
                action = "update"
                id = parseInt(div.getAttribute("data-id"))
            } else {
                action = "add"
                id = null
            }
            own_techniques.push(
                {
                    "side": side,
                    "technique": parseInt(technique),
                    "left": parseInt(left),
                    "right": parseInt(right),
                    "state": state,
                    "direction": parseInt(direction),
                    "action": action,
                    "id": id
                }
            )
        }
    })
    deleted_own_techniques.forEach(id => {
        own_techniques.push(
            {
                "action": "delete",
                "id": id
            }
        )
    })
    return own_techniques
}

function post_data(action = "redirect"){
    let name = document.getElementById("name").value
    let last_name = document.getElementById("last_name").value
    let year = document.getElementById("year").value
    let weight = document.getElementById("weight").value
    let left = document.getElementById("side_left").checked
    let right = document.getElementById("side_right").checked
    var side = null
    if (left && right){
        var side = 3
    } else if (left){
        var side = 1
    } else if (right){
        var side = 2
    }
    if (name && last_name && year && weight && side != null){
        let data = {
            "name": name,
            "last_name": last_name,
            "year": year,
            "weight": weight,
            "side": side,
            "action": action,
            "positions": get_positions(),
            "own_techniques": get_own_techniques()
        }
        const request = new Request(
            window.location.href,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json; charset=utf-8'
                },
                mode: 'same-origin',
                body: JSON.stringify(data)
            }
        )
        fetch(request).then(response => { location.href = response.url })
    }
}
