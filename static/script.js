const flags = {

USD:"🇺🇸",
UGX:"🇺🇬",
EUR:"🇪🇺",
GBP:"🇬🇧",
KES:"🇰🇪",
TZS:"🇹🇿",
NGN:"🇳🇬",
CAD:"🇨🇦",
AUD:"🇦🇺",
JPY:"🇯🇵",
CNY:"🇨🇳",
INR:"🇮🇳",
ZAR:"🇿🇦",
CHF:"🇨🇭",
AED:"🇦🇪",
SAR:"🇸🇦",
RUB:"🇷🇺",
SGD:"🇸🇬",
HKD:"🇭🇰",
BTC:"🪙",
ETH:"⚡"

};

function updateClock(){

const now = new Date();

document.getElementById("clock").innerText =
now.toLocaleTimeString();

}

setInterval(updateClock,1000);

updateClock();

function updateFlags(){

const from =
document.getElementById("fromCurrency").value;

const to =
document.getElementById("toCurrency").value;

document.getElementById("fromFlag").innerText =
flags[from];

document.getElementById("toFlag").innerText =
flags[to];

}

document.getElementById("fromCurrency")
.addEventListener("change", updateFlags);

document.getElementById("toCurrency")
.addEventListener("change", updateFlags);

let chart;

function drawChart(){

const ctx =
document.getElementById("forexChart");

if(chart){

chart.destroy();

}

chart = new Chart(ctx, {

type:'line',

data:{
labels:[
'Mon','Tue','Wed','Thu','Fri'
],

datasets:[{
label:'Forex Trend',
data:[
12,19,10,15,22
],
borderWidth:3
}]
},

options:{
responsive:true
}

});

}

drawChart();

async function convertCurrency(){

const amount =
document.getElementById("amount").value;

const fromCurrency =
document.getElementById("fromCurrency").value;

const toCurrency =
document.getElementById("toCurrency").value;

const loader =
document.getElementById("loader");

loader.style.display = "block";

const response = await fetch("/convert",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

amount:amount,
from:fromCurrency,
to:toCurrency

})

});

const data = await response.json();

loader.style.display = "none";

document.getElementById("result").innerText =
`Result: ${data.result} ${toCurrency}`;

document.getElementById("rateText").innerText =
`1 ${fromCurrency} = ${data.rate} ${toCurrency}`;

saveHistory(amount, fromCurrency, toCurrency, data.result);

showToast();

playSound();

}

function playSound(){

document.getElementById("sound").play();

}

function swapCurrencies(){

let from =
document.getElementById("fromCurrency");

let to =
document.getElementById("toCurrency");

let temp = from.value;

from.value = to.value;

to.value = temp;

updateFlags();

}

function saveHistory(amount, from, to, result){

const historyList =
document.getElementById("historyList");

const li = document.createElement("li");

li.innerText =
`${amount} ${from} → ${result} ${to}`;

historyList.prepend(li);

}

function showToast(){

const toast =
document.getElementById("toast");

toast.classList.add("show");

setTimeout(()=>{

toast.classList.remove("show");

},2000);

}

function toggleTheme(){

document.body.classList.toggle("light-mode");

}

function downloadReceipt(){

const result =
document.getElementById("result").innerText;

const rate =
document.getElementById("rateText").innerText;

const content =
`${result}\n${rate}`;

const blob =
new Blob([content], {type:"text/plain"});

const a =
document.createElement("a");

a.href = URL.createObjectURL(blob);

a.download = "rash_receipt.txt";

a.click();

}

document.getElementById("amount")
.addEventListener("input", ()=>{

if(document.getElementById("amount").value !== ""){

convertCurrency();

}

});

updateFlags();