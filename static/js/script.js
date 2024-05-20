document.addEventListener('DOMContentLoaded', async function () {
    var citySelect = document.getElementById('city');
    await fetchRandomProperties();
    var applyFiltersBtn = document.getElementById('applyFiltersBtn');
    applyFiltersBtn.addEventListener('click', async function () {
        await applyFilters();
    });

    // Trigger population of bedrooms when city selection changes
    citySelect.addEventListener('change', async function () {
        var selectedCity = citySelect.value;
        
        if(!selectedCity){
            document.getElementById('societyNames').value = "";
            document.getElementById('agencyNames').value = "";
        }
        
        await populateBedrooms(selectedCity);
        await populateBathrooms(selectedCity);
        await populateSocieties(selectedCity);
        await populateAgencies(selectedCity);
    });
    await populateBedrooms('');
    await populateBathrooms('');
});

// Function to populate bathrooms based on selected city
async function populateBathrooms(city) {
    var bathroomSelect = document.getElementById('numBathrooms');
    bathroomSelect.innerHTML = '';

    var option = document.createElement('option');
    option.value = '';
    option.textContent = 'Select No of Bathrooms';
    bathroomSelect.appendChild(option);

    data = await fetch('/api/bathrooms?city=' + (city || 'nocity'), {
        method: 'GET'
    });
    bathrooms = await data.json();

    bathrooms.forEach(bathroom => {
        var option = document.createElement('option');
        option.value = bathroom.NUMBATHROOMS;
        option.textContent = bathroom.NUMBATHROOMS + ' Bathrooms';
        bathroomSelect.appendChild(option);
    });
}

async function populateAgencies(selectedCity) {
    var agencyNames = document.getElementById('agencies');
    if(selectedCity == ''){
        agencyNames.style.display = "none";
        return;
    }

    agencyNames.style.display = "block";
    agencyNames = document.getElementById('agencyNames');
    agencyNames.innerHTML = '';

    var option = document.createElement('option');
    option.value = '';
    option.textContent = 'Select Agency';
    agencyNames.appendChild(option);

    data = await fetch('/api/agencies?city=' + (selectedCity || 'nocity'), {
        method: 'GET'
    });
    agencies = await data.json();

    console.log(agencies);
    agencies.forEach(agency => {
        var option = document.createElement('option');
        option.value = agency.AGENCYNAME;
        option.textContent = agency.AGENCYNAME;
        agencyNames.appendChild(option);
    });
}

async function populateSocieties(selectedCity) {
    var societyNames = document.getElementById('societies');
    if(selectedCity == ''){
        societyNames.style.display = "none";
        return;
    }

    societyNames.style.display = "block";
    societyNames = document.getElementById('societyNames');
    societyNames.innerHTML = '';

    var option = document.createElement('option');
    option.value = '';
    option.textContent = 'Select Society Name';
    societyNames.appendChild(option);

    data = await fetch('/api/societies?city=' + (selectedCity || 'nocity'), {
        method: 'GET'
    });
    societies = await data.json();

    societies.forEach(society => {
        var option = document.createElement('option');
        option.value = society.SOCIETYNAME;
        option.textContent = society.SOCIETYNAME;
        societyNames.appendChild(option);
    });
}

async function fetchRandomProperties() {

    data = await fetch('/api/random_properties', {
        method: 'GET'
    });
    properties = await data.json();
    displayProperties(properties);
}

async function applyFilters() {
    var minPrice = document.getElementById('minPrice').value;
    var maxPrice = document.getElementById('maxPrice').value;
    var city = document.getElementById('city').value;
    var bedrooms = document.getElementById('numBedrooms').value;
    var bathrooms = document.getElementById('numBathrooms').value;
    var society = document.getElementById('societyNames').value;
    var agency = document.getElementById('agencyNames').value;

    // Make AJAX request to fetch properties based on filters
    data = await fetch('/filter?minPrice=' + minPrice + 
                        '&maxPrice=' + maxPrice + 
                        '&city=' + city + 
                        '&bedrooms=' + (bedrooms == "" ? "": parseInt(bedrooms)) +
                        '&bathrooms=' + (bathrooms == "" ? "": parseInt(bathrooms)) +
                        '&agency=' + agency +
                        '&society=' + society, {
                            method: 'GET'
                        }
                    );
    filteredProperties = await data.json();
    displayProperties(filteredProperties);
}

function displayProperties(properties) {
    var propertyList = document.getElementById('propertyList');
    propertyList.innerHTML = '';

    properties.forEach(function (property) {
        var propertyBox = document.createElement('div');
        propertyBox.classList.add('property-box');

        var propertyImage = document.createElement('img');
        propertyImage.src = property.image_url;
        propertyBox.appendChild(propertyImage);

        var propertyHeading = document.createElement('div');
        propertyHeading.classList.add('property-heading');
        propertyHeading.textContent = property.PROPERTYHEADING;
        propertyBox.appendChild(propertyHeading);

        var propertyDescription = document.createElement('div');
        propertyDescription.classList.add('property-description');
        propertyDescription.textContent = property.PROPERTYNAME;
        propertyBox.appendChild(propertyDescription);

        propertyList.appendChild(propertyBox);

        propertyBox.addEventListener('click', function () {
            window.location.href = '/individual_property?id=' + property.PROPERTYID;
        });

    });

    var clearfix = document.createElement('div');
    clearfix.classList.add('clearfix');
    propertyList.appendChild(clearfix);
}


// Function to populate bedrooms based on selected city
async function populateBedrooms(city) {
    var bedroomsSelect = document.getElementById('numBedrooms');
    bedroomsSelect.innerHTML = '';

    var option = document.createElement('option');
    option.value = '';
    option.textContent = 'Select No of Bedrooms';
    bedroomsSelect.appendChild(option);

    data = await fetch('/api/bedrooms?city=' + (city || 'nocity'), {
        method: 'GET'
    });
    bedrooms = await data.json();

    bedrooms.forEach(bedroom => {
        var option = document.createElement('option');
        option.value = bedroom.NUMBEDROOMS;
        option.textContent = bedroom.NUMBEDROOMS + ' Bedrooms';
        bedroomsSelect.appendChild(option);
    });
}
