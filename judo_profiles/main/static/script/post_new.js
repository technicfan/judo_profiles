function get_positions(){
    let pos = []
    document.querySelectorAll(".move").forEach(position => {
        if (position.style.display == "flex"){
            let x = getRelative(position)
            pos.push(
                {
                    "number": parseInt(position.className.slice(-1)),
                    "side": position.className[0] == "l" ? true : false,
                    "x": x[1],
                    "y": x[0]
                }
            )
        }
    })
    return pos
}

function get_own_techniques(){
    let own_techniques = []
    document.querySelectorAll(".own_technique").forEach(div => {
        let side = div.querySelector(".direction").value == "l" ? true : false
        let technique = div.querySelector(".technique").value
        let left = div.querySelector(".select_position.left").value
        let right = div.querySelector(".select_position.right").value
        let state = div.querySelector(".state").value
        let direction = div.id[3]
        if (technique && left && right && state && direction){
            own_techniques.push(
                {
                    "side": side,
                    "technique": parseInt(technique),
                    "left": parseInt(left),
                    "right": parseInt(right),
                    "state": state,
                    "direction": parseInt(direction)
                }
            )
        }
    })
    return own_techniques
}

function post_data(){
    let name = document.getElementById("name").value
    let last_name = document.getElementById("last_name").value
    let year = document.getElementById("year").value
    let weight = document.getElementById("weight").value
    let left = document.getElementById("side_left").checked
    let right = document.getElementById("side_right").checked
    let side
    if (left && right){
        side = 2
    } else if (left){
        side = 1
    } else if (right){
        side = 0
    }
    if (name && last_name && year && weight && side != ""){
        let data = {
            "name": name,
            "last_name": last_name,
            "year": year,
            "weight": weight,
            "side": side,
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
