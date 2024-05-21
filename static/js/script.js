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
        
        await populateFeatureTypes(selectedCity);
        await populateBedrooms(selectedCity);
        await populatePropertyTypes(selectedCity);
        await populateBathrooms(selectedCity);
        await populateSocieties(selectedCity);
        await populateAgencies(selectedCity);
    });
    await populateFeatureTypes('');
    await populatePropertyTypes('');
    await populateBedrooms('');
    await populateBathrooms('');
});

// Function to populate property types based on selected city
async function populateFeatureTypes(city) {
    var featureSelect = document.getElementById('featureSelect');
    var addFeatureBtn = document.getElementById('addFeatureBtn');

    data = await fetch('/api/feature-names?city=' + (city || 'nocity'), {
        method: 'GET'
    });
    features = await data.json();

    featureSelect.innerHTML = ''
    
    var option = document.createElement('option');
    option.value = '';
    option.textContent = 'Select Feature';
    featureSelect.appendChild(option);

    features.forEach(function (feature) {
        var option = document.createElement('option');
        option.value = feature.FEATURENAME;
        option.textContent = feature.FEATURENAME;
        featureSelect.appendChild(option);
    });

    addFeatureBtn.addEventListener('click', function () {
        var selectedFeature = featureSelect.value;
        if (selectedFeature !== '') {
            addSelectedFeature(selectedFeature);
            featureSelect.value = '';
        }
    });
}

function addSelectedFeature(featureName) {
    var selectedFeaturesContainer = document.getElementById('selectedFeatures');

    var selectedFeatureBox = document.createElement('div');
    selectedFeatureBox.classList.add('selected-feature');

    var featureText = document.createElement('span');
    featureText.textContent = featureName;
    selectedFeatureBox.appendChild(featureText);

    var closeIcon = document.createElement('span');
    closeIcon.classList.add('close-icon');
    closeIcon.innerHTML = ' x';
    closeIcon.addEventListener('click', function () {
      selectedFeatureBox.remove();
    });
    selectedFeatureBox.appendChild(closeIcon);

    selectedFeaturesContainer.appendChild(selectedFeatureBox);
}

// Function to populate property types based on selected city
async function populatePropertyTypes(city) {
    var propertyTypes = document.getElementById('propertyTypes');
    propertyTypes.innerHTML = '';

    var option = document.createElement('option');
    option.value = '';
    option.textContent = 'Select Property Type';
    propertyTypes.appendChild(option);

    data = await fetch('/api/property-type?city=' + (city || 'nocity'), {
        method: 'GET'
    });
    bathrooms = await data.json();

    bathrooms.forEach(prop => {
        var option = document.createElement('option');
        option.value = prop.PROPERTYTYPE;
        option.textContent = prop.PROPERTYTYPE;
        propertyTypes.appendChild(option);
    });
}

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

function getSelectedFeatures() {
    var selectedFeatures = [];
    var featureElements = document.querySelectorAll('.selected-feature');
    featureElements.forEach(function(element) {
        selectedFeatures.push(element.textContent.trim());
    });
    return selectedFeatures;
}

async function applyFilters() {
    var minPrice = document.getElementById('minPrice').value;
    var maxPrice = document.getElementById('maxPrice').value;
    var city = document.getElementById('city').value;
    var bedrooms = document.getElementById('numBedrooms').value;
    var bathrooms = document.getElementById('numBathrooms').value;
    var society = document.getElementById('societyNames').value;
    var agency = document.getElementById('agencyNames').value;
    var propType = document.getElementById('propertyTypes').value;
    var selectedFeatures = getSelectedFeatures();
    var selectedFeaturesString = selectedFeatures.join(',');

    // Make AJAX request to fetch properties based on filters
    data = await fetch('/filter?minPrice=' + minPrice + 
                        '&maxPrice=' + maxPrice + 
                        '&city=' + city + 
                        '&bedrooms=' + (bedrooms == "" ? "": parseInt(bedrooms)) +
                        '&bathrooms=' + (bathrooms == "" ? "": parseInt(bathrooms)) +
                        '&agency=' + agency +
                        '&propType=' + propType +
                        '&selectedFeatures=' + selectedFeaturesString + 
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
        propertyImage.src = property.IMG;
        propertyBox.appendChild(propertyImage);

        var favIcon = document.createElement('img');
        favIcon.classList.add('favorite-icon')
        favIcon.src = property.FAVOURITE ? "/static/img/favorited.png": "/static/img/not_favorited.png";
        propertyBox.appendChild(favIcon);

        var priceHeading = document.createElement('div');
        priceHeading.classList.add('property-heading');
        priceHeading.textContent = '₹' + property.PURCHASE_PRICE + " | " + property.AREA + " sqft";
        propertyBox.appendChild(priceHeading);

        var propertyHeading = document.createElement('div');
        propertyHeading.classList.add('property-heading');
        propertyHeading.textContent = property.PROPERTYHEADING;
        propertyBox.appendChild(propertyHeading);

        var propertyDescription = document.createElement('div');
        propertyDescription.classList.add('property-description');
        propertyDescription.textContent = property.NUMBEDROOMS + " BHK | " + property.NUMBATHROOMS + " BA | " + property.SOCIETYNAME;
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
