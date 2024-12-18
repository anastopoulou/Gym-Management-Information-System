let countryList = document.getElementById('country'); //list with countries
let cityList = document.getElementById('city'); //list with cities

// get countries data  from url as json 
fetch('https://countriesnow.space/api/v0.1/countries').then(response => response.json()).then(data => {
  let countries = data.data;  //get the countries from api 
  countries.forEach(country => {  //create option elements for each country
    const option = document.createElement('option');
    option.value = country.country;
    countryList.appendChild(option); //insert options in the list
  })
}).catch(error => console.log("An error has occuried",error));

// get countries respective cities data from url as json
function getCities() {  fetch('https://countriesnow.space/api/v0.1/countries').then(response => response.json()).then(data => {
    cityList.innerHTML=''; /* remove previous options so if user selects a country and then another country, before submitting the form, 
    the list with cities will not keep the cities from users previous selected country*/
    let selectedCountry = document.getElementById('countries').value;
    let findSelectedCountry = data.data.find(country => country.country === selectedCountry); //find which country user has select
    let cities = findSelectedCountry.cities; //get the respective cities from the selected country 
    cities.forEach(city => {
      const option = document.createElement('option'); // create option elements for each city
      option.value = city;
      cityList.appendChild(option); //insert options in the list
    });
  }).catch(error => console.log("An error has occuried",error));
}