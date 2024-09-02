
document.getElementById('wishes').textContent = ("I hate you, Bob")

const newImage = 'https://pbs.twimg.com/media/DnH2kP2XcAAv7et?format=jpg&name=small'
document.getElementById('image1').children[0].src = (newImage)

//in pb, of its images, we set each width
// cool thing enough is they dont need to initially have an attribute to change it
let element = document.getElementsByClassName('panel-body')[2]
let images = element.getElementsByTagName('img')//this gives us the array!
for(let img of images) {
    img.style.width = '300px'
}

let button = document.getElementsByClassName('btn')[0]
button.addEventListener('click', () => {
    //we need to grab 'node' the thing we WANT to replace
    let pg = button.parentElement
    let node = pg.childNodes[1]

    //create the replacement
    let span = document.createElement('span')
    span.style.color = 'red'
    span.style.fontSize = '15em'
    span.textContent = node.textContent

    //replace the 'empty' thing -node, with our newly made thing 'span'
    pg.replaceChild(span, node)
})

let element1 = document.getElementsByClassName('panel-body')[4]
circle = element1.getElementsByTagName('img')[0]
spanner = element1.getElementsByTagName('span')[0]

circle.addEventListener('mouseover', () => {
    spanner.classList.remove('hidden')
})

circle.addEventListener('mouseout', () => {
    spanner.classList.add('hidden')
})

let textIn = document.getElementsByClassName('panel-body')[5]
let textA = textIn.getElementsByTagName('input')[0]
let textB = textIn.getElementsByTagName('input')[1]

textA.addEventListener('input', () => {
    textB.value = textA.value
})

let focusBox = document.getElementsByClassName('panel-body')[6]
let input = focusBox.getElementsByTagName('input')[0]

input.addEventListener('focusout', () => {
    input.value = 'HAHA'
})

let checkBox = document.getElementsByClassName('panel-body')[7]
let box = checkBox.getElementsByTagName('input')[0]
let select = checkBox.getElementsByTagName('select')[0]

box.addEventListener('change', () => {
    box.checked ? select.classList.remove('hidden') : select.classList.add('hidden')
})

let timer = document.getElementsByClassName('panel-body')[8]
let header = timer.getElementsByTagName('h1')[0]
let timeData = parseInt(header.textContent)

function loop(time, part) {
    setTimeout(() => {
        if (time < 1) {
            //stop
            part.textContent = '0' //should be zero
            timeData = 0    //comment out fi you wanna do multiple times
            return
        } else {
            //continue - 1
            part.textContent = time - 1
            loop(time - 1, part)
        }
    }, 1000)
}

header.addEventListener('click', () => {
    loop(timeData, header)
})