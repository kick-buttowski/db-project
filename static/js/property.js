document.addEventListener('DOMContentLoaded', async function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const propertyId = urlParams.get('id');

    data = await fetch('/api/fetch_ind_property?id=' + propertyId, {
        method: 'GET'
    });
    propertyDetails = await data.json();

    data = await fetch('/api/fetch_ind_property/features?id=' + propertyId, {
        method: 'GET'
    });
    propertyFeatures = await data.json();

    displayPropertyDetails(propertyDetails, propertyFeatures);
});

function displayPropertyDetails(propertyDetails, propertyFeatures) {
    var propertyImage = document.createElement('img');
    propertyImage.src = propertyDetails.IMG;
    propertyImage.style.width = "100%";
    
    var propertyHeading = document.createElement('h2');
    propertyHeading.textContent = propertyDetails.propertyHeading;

    var price = document.createElement('h3');
    price.textContent = '₹' + propertyDetails.purchase_price;

    var description = document.createElement('p');
    description.textContent = propertyDetails.description;

    var propertyType = document.createElement('p');
    propertyType.textContent = propertyDetails.propertyName + ", " + propertyDetails.propertyType;

    var propertyDet = document.createElement('p');
    propertyDet.textContent = propertyDetails.numBedrooms + " BHK, " + propertyDetails.numBathrooms + " BA, " + propertyDetails.numBalconies + " Balcony, " + propertyDetails.area + " SQFT";

    var propertyLocality = document.createElement('p');
    propertyLocality.textContent = propertyDetails.SocietyName + ", " + propertyDetails.locality + ", " + propertyDetails.city;

    var propertyDetailsContainer = document.querySelector('.property-details');
    propertyDetailsContainer.innerHTML = '';

    var propertyImageContainer = document.querySelector('.property-image');
    propertyImageContainer.innerHTML = '';

    var agent = document.createElement('h4');
    agent.textContent = "Agent: " + propertyDetails.firstName + " " + propertyDetails.lastName + ", " + propertyDetails.agencyName;

    var featuresElement = document.createElement('p');
    let features = "";
    propertyFeatures.forEach(feature => {
        features += feature.FEATURENAME + ", "
    });
    featuresElement.textContent = features;

    propertyImageContainer.appendChild(propertyImage);

    propertyDetailsContainer.appendChild(propertyHeading);
    propertyDetailsContainer.appendChild(price);
    propertyDetailsContainer.appendChild(description);
    propertyDetailsContainer.appendChild(propertyType);
    propertyDetailsContainer.appendChild(featuresElement);
    propertyDetailsContainer.appendChild(propertyDet);
    propertyDetailsContainer.appendChild(propertyLocality);

    propertyDetailsContainer.appendChild(agent);
}

