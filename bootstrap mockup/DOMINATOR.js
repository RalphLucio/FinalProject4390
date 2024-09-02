
let first = document.getElementById("first")
let second = document.getElementById("second")
let third = document.getElementById("third")

let sub1 = document.getElementById("sub1")
let sub2 = document.getElementById("sub2")
let sub3 = document.getElementById("sub3")
let sub4 = document.getElementById("sub4")
let sub5 = document.getElementById("sub5")
let sub6 = document.getElementById("sub6")
let sub7 = document.getElementById("sub7")
let sub8 = document.getElementById("sub8")
let sub9 = document.getElementById("sub9")
let sub10 = document.getElementById("sub10")
let sub11 = document.getElementById("sub11")
let sub12 = document.getElementById("sub12")
let sub13 = document.getElementById("sub13")
let sub14 = document.getElementById("sub14")
let sub15 = document.getElementById("sub15")
let sub16 = document.getElementById("sub16")
let sub17 = document.getElementById("sub17")
let sub18 = document.getElementById("sub18")
let sub19 = document.getElementById("sub19")
let sub20 = document.getElementById("sub20")

function startLoading() {

    // OFF RIP
    first.classList.remove('mainTextNeutral');
    first.classList.add('mainTextLarge');

    //small objectives
    setTimeout(() => {sub1.classList.add('subtextFadeIn');}, 1000)
    setTimeout(() => {sub2.classList.add('subtextFadeIn');}, 3000)

    setTimeout(() => {sub4.classList.add('subtextFadeIn');}, 4000)
    setTimeout(() => {sub5.classList.add('subtextFadeIn');}, 6000)

    setTimeout(() => {sub7.classList.add('subtextFadeIn');}, 7000)
    setTimeout(() => {sub8.classList.add('subtextFadeIn');}, 9000)

    // -> End First Animation, Start Second Animation
    setTimeout(() => {
        first.classList.remove('mainTextLarge');
        first.classList.add('mainTextSmall');

        second.classList.remove('mainTextNeutral');
        second.classList.add('mainTextLarge');
    }, 10000)

    //small objectives
    setTimeout(() => {sub10.classList.add('subtextFadeIn');}, 11000)
    setTimeout(() => {sub11.classList.add('subtextFadeIn');}, 13000)

    // -> End Second Animation, Start Third Animation
    setTimeout(() => {
        second.classList.remove('mainTextLarge');
        second.classList.add('mainTextSmall');

        third.classList.remove('mainTextNeutral');
        third.classList.add('mainTextLarge');
    }, 14000)

    //small objectives
    setTimeout(() => {sub13.classList.add('subtextFadeIn');}, 15000)
    setTimeout(() => {sub14.classList.add('subtextFadeIn');}, 17000)
    setTimeout(() => {sub15.classList.add('subtextFadeIn');}, 20000)
    setTimeout(() => {sub16.classList.add('subtextFadeIn');}, 23000)
    setTimeout(() => {sub17.classList.add('subtextFadeIn');}, 26000)
    setTimeout(() => {sub18.classList.add('subtextFadeIn');}, 28000)
    setTimeout(() => {sub19.classList.add('subtextFadeIn');}, 30000)
    setTimeout(() => {sub20.classList.add('subtextFadeIn');}, 31000)
    setTimeout(() => {sub20.textContent = 'Loading.'; }, 32000)
    setTimeout(() => {sub20.textContent = 'Loading..'; }, 33000)
    setTimeout(() => {sub20.textContent = 'Loading...'; }, 34000)
    setTimeout(() => {window.location.href = 'summary.html';}, 35000)

    console.log("Page loaded, and function executed.");
}