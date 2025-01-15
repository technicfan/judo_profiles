const image = document.getElementById("image")

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

    object.style.top = relativeY * image.clientHeight + image.getBoundingClientRect().top + window.scrollY + "px"
    object.style.left = relativeX * image.clientWidth + image.getBoundingClientRect().left + window.scrollX + "px"
}

function colorSelected(classes, color){
    selected = document.getElementsByClassName(classes)
    for (let i = 0; i < selected.length; i++) {
        selected.item(i).style.borderColor = color
    }
}
