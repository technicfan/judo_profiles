const image = document.getElementById("image_container")

function placeRelative(object, relativeY, relativeX){
    image_rect = image.getBoundingClientRect()
    object_rect = object.getBoundingClientRect()
    maxY = 1 - object_rect.height / 2 / image_rect.height
    maxX = 1 - object_rect.width / 2 / image_rect.width
    minY = object_rect.height / 2 / image_rect.height
    minX = object_rect.width / 2 / image_rect.width

    if (relativeY >= maxY){
        relativeY = maxY
    } else if (relativeY <= minY){
        relativeY = minY
    }
    if (relativeX >= maxX){
        relativeX = maxX
    } else if (relativeX <= minX){
        relativeX = minX
    }

    object.style.top = relativeY * 100 - object_rect.height / 2 / image_rect.height * 100 + "%"
    object.style.left = relativeX * 100 - object_rect.width / 2 / image_rect.width * 100 + "%"
}

function colorSelected(classes, color){
    selected = document.getElementsByClassName(classes)
    for (let i = 0; i < selected.length; i++) {
        selected.item(i).style.borderColor = color
    }
}
