// disable submitting for unwanted buttons
document.querySelectorAll("button").forEach(button => { button.addEventListener("click", event => { event.preventDefault() }) })

// Own Techniques
let own1 = 1, own2 = 1, own3 = 1, own4 = 1;
const techniques = $("#hidden_techniques").html()

function add_own(field){
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
            <button onclick="remove_own(` + field + ", " + number + `)" class="dont_submit">Löschen</button>
        </div>
        `

        $("#own" + field).append(own_technique_html)
        for (let i = 0; i < positions.length; i++) {
            let position = positions.item(i)
            if (position.style.display == "flex"){
                $("#" + "own" + field + "_" + "p" + position.className[0] + number).append(
                    '<option value="' + position.className.slice(-1) + '">' + position.className.slice(-1) + '</option>'
                )
            }
        }

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

// Positions
let newX = 0, newY = 0, startX = 0, startY = 0, delete_mode = false, move = null;
const image = document.getElementById("image")
const positions = document.getElementsByClassName("move")
document.querySelectorAll(".option").forEach(element => { element.addEventListener("mousedown", mouseDownOpt) })

function mouseDownOpt(e){
    if (move != null){
        mouseDownDoc(e)
    }
    target = e.target
    move = document.getElementById(getMatchingID(target.id))
    colorSelected(target.className[0] + " " + target.className.slice(-1), "black")
    image.addEventListener("mousedown", mouseDownImg)
    document.addEventListener("mousedown", mouseDownDoc)
}

function mouseDownDoc(e){
    if (move != null){
        if (e.target.id != "image" && e.target.id != getMatchingID(move.id) && move.style.display != "flex"){
            colorSelected(move.className[0] + " " + move.className.slice(-1), "grey")
            image.removeEventListener("mousedown", mouseDownImg)
        }
        if (e.target.id != getMatchingID(move.id)){
            document.removeEventListener("mousedown", mouseDownDoc)
        }
    }
}

function mouseDownImg(e){
    if (move != null){
        move.style.display = "flex"
        placeRelative(move, (e.clientY - move.clientHeight / 2 - image.getBoundingClientRect().top) / image.clientHeight, 
                        (e.clientX - move.clientWidth / 2 - image.getBoundingClientRect().left) / image.clientWidth)
        if (move.className[0] == "l"){
            side = "left"
        } else {
            side = "right"
        }
        document.querySelectorAll("." + side).forEach(select => {
            if ($("#" + select.id).find("[value='" + move.className.slice(-1) + "']").text() == ""){
                $("#" + select.id).append('<option value="' + move.className.slice(-1) + '">' + move.className.slice(-1) + '</option>')
            }
        })
        move.addEventListener("mousedown", mouseDownPos)
    }
}

function mouseDownPos(e){
    move = document.getElementById(e.target.id)
    if (delete_mode){
        move.style.display = "none"
        document.getElementById(getMatchingID(move.id)).style.borderColor = "grey"
        for (let i = 0; i < positions.length; i++) {
            if (positions.item(i).style.display == "flex"){
                positions.item(i).style.borderColor = "black"
                positions.item(i).style.cursor = "grab"
            }
        }
        if (move.className[0] == "l"){
            side = "left"
        } else {
            side = "right"
        }
        $('.' + side + ' [value="' + move.className.slice(-1) + '"]').remove()
        $('.' + side).val('').trigger('chosen:updated')
        delete_mode = false
        move = null
    } else {
        startX = e.clientX
        startY = e.clientY
        move.style.cursor = "grabbing"
        document.addEventListener("mousemove", mouseMovePos)
        document.addEventListener("mouseup", mouseUpPos)
    }
}

function mouseMovePos(e){
    if (move != null){
        if (e.clientX <= image.getBoundingClientRect().left + image.offsetWidth && e.clientX >= image.getBoundingClientRect().left){
            newX = startX - e.clientX
            startX = e.clientX
        }
        if (e.clientY <= image.getBoundingClientRect().top + image.clientHeight && e.clientY >= image.getBoundingClientRect().top){
            newY = startY - e.clientY
            startY = e.clientY
        }
        placeRelative(move, (move.getBoundingClientRect().top - newY - image.getBoundingClientRect().top) / image.clientHeight,
                        (move.getBoundingClientRect().left - newX - image.getBoundingClientRect().left) / image.clientWidth)
    }
}

function mouseUpPos(e){
    if (move != null){
        move.style.cursor = "grab"
        document.removeEventListener("mousemove", mouseMovePos)
    }
}

function placeRelative(object, relativeY, relativeX){
    borderWidth = parseInt(window.getComputedStyle(object).borderWidth)
    maxY = 1 - (object.clientHeight + 2 * borderWidth) / image.clientHeight
    maxX = 1 - (object.clientWidth + 2 * borderWidth) / image.clientWidth

    if (relativeY >= maxY){
        relativeY = maxY
    } else if (relativeY <= 0){
        relativeY = 0
    }
    if (relativeX >= maxX){
        relativeX = maxX
    } else if (relativeX <= 0){
        relativeX = 0
    }

    console.log(window.scrollY)
    console.log(relativeX, relativeY)

    object.style.top = relativeY * image.clientHeight + image.getBoundingClientRect().top + window.scrollY + "px"
    object.style.left = relativeX * image.clientWidth + image.getBoundingClientRect().left + window.scrollX + "px"
}

function getRelative(object){
    y = (parseInt(object.style.top) - image.getBoundingClientRect().top - window.scrollY) / image.clientHeight
    x = (parseInt(object.style.left) - image.getBoundingClientRect().left - window.scrollX) / image.clientWidth
    
    return [y, x]
}

function colorSelected(classes, color){
    selected = document.getElementsByClassName(classes)
    for (let i = 0; i < selected.length; i++) {
        selected.item(i).style.borderColor = color
    }
}

function getMatchingID(id){
    if (id[0] == "p"){
        return "o" + id.slice(1)
    } else if (id[0] == "o"){
        return "p" + id.slice(1)
    }
}

function delClick(){
    for (let i = 0; i < positions.length; i++) {
        if (positions.item(i).style.display == "flex"){
            positions.item(i).style.borderColor = "red"
            positions.item(i).style.cursor = "not-allowed"
            delete_mode = true
        }
    }
}

function submit_positions(){
    pos = []
    for (let i = 0; i < positions.length; i++) {
        if (positions.item(i).style.display == "flex"){
            x = getRelative(positions.item(i))
            pos.push([positions.item(i).className.slice(-1), positions.item(i).className[0], x[0], x[1]])
        }
    }
    console.log(pos)
}

function get_own_techniques(){
    document.querySelectorAll(".own_technique").forEach(div => {
        this.direction = div.querySelector(".direction").value
        this.technique = div.querySelector(".technique").value
        this.left = div.querySelector(".select_position.left").value
        this.right = div.querySelector(".select_position.right").value
        this.state = div.querySelector(".state").value
    })
}