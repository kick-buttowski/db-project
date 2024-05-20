document.addEventListener('DOMContentLoaded', function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const propertyId = urlParams.get('id');

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/fetch_ind_property?id=' + propertyId, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
            var propertyDetails = JSON.parse(xhr.responseText);
            displayPropertyDetails(propertyDetails);
        }
    };
    xhr.send();
});

function displayPropertyDetails(propertyDetails) {
    var propertyDetailsContainer = document.getElementById('propertyDetails');
    propertyDetailsContainer.innerHTML = '';

    var propertyImage = document.createElement('img');
    propertyImage.src = propertyDetails.image_url;
    propertyImage.style.width = "100%";
    propertyDetailsContainer.appendChild(propertyImage);

    var propertyHeading = document.createElement('h2');
    propertyHeading.textContent = propertyDetails.propertyHeading;
    propertyDetailsContainer.appendChild(propertyHeading);

    var description = document.createElement('p');
    description.textContent = "Description: " + propertyDetails.description;
    propertyDetailsContainer.appendChild(description);

    var propertyType = document.createElement('p');
    propertyType.textContent = "Property Type: " + propertyDetails.propertyType;
    propertyDetailsContainer.appendChild(propertyType);

}
