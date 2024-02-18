function showcase_data(src, alt) {
    var img = document.createElement("img");
    img.src = src;
    img.width = 500;
    img.height = 500;
    img.alt = alt;
    document.body.appendChild(img); 
}

function remove_buttons() {
    button1.style.display = "none";
    button2.style.display = "none";
    button3.style.display = "none";
    button4.style.display = "none";
    button5.style.display = "none";
}


const button1 = document.createElement('button')
button1.innerText = '2023'
button1.addEventListener('click', () => {
    showcase_data("images/annual_2023.png", "2023 data")
    remove_buttons()
})
button1.className = 'bttn1'
document.body.appendChild(button1)

const button2 = document.createElement('button')
button2.innerText = '2022'
button2.addEventListener('click', () => {
    showcase_data("images/annual_2022.png", "2022 data")
    remove_buttons()
})
button2.className = 'bttn2'
document.body.appendChild(button2)


const button3 = document.createElement('button')
button3.innerText = '2021'
button3.addEventListener('click', () => {
    showcase_data("images/annual_2021.png", "2021 data")
    remove_buttons()
})
button3.className = 'bttn3'
document.body.appendChild(button3)

const button4 = document.createElement('button')
button4.innerText = '2020'
button4.addEventListener('click', () => {
    showcase_data("images/annual_2020.png", "2020 data")
    remove_buttons()
})
button2.className = 'bttn4'
document.body.appendChild(button4)

const button5 = document.createElement('button')
button5.innerText = '2019'
button5.addEventListener('click', () => {
    showcase_data("images/annual_2019.png", "2019 data")
    remove_buttons()
})
button5.className = 'bttn5'
document.body.appendChild(button5)






