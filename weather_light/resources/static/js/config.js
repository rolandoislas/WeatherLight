Config = function(){
    function defineColorInputs() {
        let colors = jsColorPicker('input.color', {
            customBG: '#fff',
            readOnly: true,
            init: function (elm, colors) {
                elm.style.backgroundColor = elm.value;
                elm.style.color = colors.rgbaMixCustom.luminance > 0.22 ? '#222' : '#ddd';
            }
        });
    }

    function reset() {
        let colors = document.getElementById("colors");
        while (colors.firstChild)
            colors.removeChild(colors.firstChild);
        let general = document.getElementById("general");
        while (general.firstChild)
            general.removeChild(general.firstChild);
    }

    function showMessage(message = "", error) {
        let messageElement = document.getElementById("message");
        messageElement.innerText = message;
        messageElement.setAttribute("style", error ? "background: #ffd4d4;" : "background: #e7e7e7;");
    }

    function error(message) {
        showMessage(message, true);
    }

    function loadConfig(completion) {
        showMessage("Loading");
        reset();
        let request = new XMLHttpRequest();
        request.addEventListener("loadend", function () {
            if (request.status === 200) {
                try {
                    let json = JSON.parse(request.response);
                    if (typeof(json) === "undefined" || json === null)
                        return error("Invalid JSON data received from API");
                    showMessage();
                    completion(json);
                }
                catch (e) {
                    console.log(e);
                    error("Failed to parse API JSON.");
                }
            }
            else {
                error("Failed to connect to API")
            }
        });
        request.open("GET", "/config", true);
        request.send();
    }

    function showCityChooser() {
        let chooser = document.getElementById("city-chooser");
        chooser.style.display = "block";
    }

    function closeCityChooser() {
        let chooser = document.getElementById("city-chooser");
        chooser.style.display = "none";
    }

    function populateConfigElements(json) {
        // Colors
        let colors = document.getElementById("colors");
        let colorNames = {
            "color_thunderstorm_no_rain": "Thunderstorm",
            "color_thunderstorm_rain": "Thunderstorm (Rain)",
            "color_drizzle": "Drizzle",
            "color_rain": "Rain",
            "color_rain_heavy": "Rain (Heavy)",
            "color_snow": "Snow",
            "color_atmosphere": "Atmosphere (Mist/Fog/Dust)",
            "color_clear": "Clear",
            "color_clouds": "Clouds"
        };
        let colorKeys = Object.keys(colorNames);
        for (let colorKeyIndex = 0; colorKeyIndex < colorKeys.length; colorKeyIndex++) {
            let colorKey = colorKeys[colorKeyIndex];
            let colorName = colorNames[colorKey];
            let color = document.createElement("label");
            color.setAttribute("data", colorKey);
            if (colorKeyIndex % 2 === 0)
                color.classList.add("row-blue");
            let colorText = document.createElement("span");
            colorText.innerText = colorName;
            colorText.classList.add("label-text");
            color.appendChild(colorText);
            let picker = document.createElement("input");
            picker.setAttribute("type", "text");
            if (colorKey in json) {
                let rgb = json[colorKey];
                picker.setAttribute("value", "rgb(" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")");
            }
            else {
                picker.setAttribute("value", "rgb(222, 222, 222)")
            }
            picker.classList.add("color");
            color.appendChild(picker);
            colors.appendChild(color);
            if (colorKeyIndex < colorKeys.length - 1)
                colors.appendChild(document.createElement("br"));
        }
        defineColorInputs();
        // General
        let general = document.getElementById("general");
        let cityId = document.createElement("label");
        cityId.setAttribute("data", "city_id");
        cityId.classList.add("row-blue");
        cityId.classList.add("clickable");
        cityId.addEventListener("click", showCityChooser);
        let text = document.createElement("span");
        text.innerText = "City";
        text.classList.add("label-text");
        cityId.appendChild(text);
        let input = document.createElement("input");
        input.setAttribute("id", "city-input");
        input.setAttribute("type", "text");
        input.setAttribute("readonly", "readonly");
        if ("city_name" in json) {
            input.setAttribute("value", json["city_name"]);
        }
        else if ("city_id" in json) {
            input.setAttribute("value", json["city_id"]);
        }
        if ("city_id" in json) {
            input.setAttribute("data", json["city_id"]);
        }
        input.classList.add("item");
        input.classList.add("clickable");
        input.addEventListener("click", showCityChooser);
        cityId.appendChild(input);
        general.appendChild(cityId);
        general.appendChild(document.createElement("br"));

        let forecastOffset = document.createElement("label");
        forecastOffset.setAttribute("data", "forecast_offset");
        text = document.createElement("span");
        text.innerText = "Forecast Offset (Hours)";
        text.classList.add("label-text");
        forecastOffset.appendChild(text);
        input = document.createElement("input");
        input.setAttribute("type", "text");
        input.setAttribute("pattern", "^([0-9]|1[0-9]|2[0-4])$");
        input.setAttribute("title", "A number between 0 and 24 (inclusive)");
        if ("forecast_offset" in json) {
            input.setAttribute("value", json["forecast_offset"] / 60.0 / 60.0);
        }
        input.classList.add("item");
        forecastOffset.appendChild(input);
        general.appendChild(forecastOffset);
    }

    function handleFormSubmit(event) {
        event.preventDefault();
        let config = {};
        // Populate colors
        let colors = document.getElementById("colors").getElementsByClassName("color");
        let rgbRegex = new RegExp("rgba?\\(([0-9]{1,3}),\\s?([0-9]{1,3}),\\s?([0-9]{1,3})\\s?[^)]*\\)");
        for (let colorIndex = 0; colorIndex < colors.length; colorIndex++) {
            let color = colors[colorIndex];
            let parent = color.parentElement;
            if (!parent.hasAttribute("data")) {
                console.debug("Color with index " + colorIndex + " missing data attribute");
                error("An error occurred submitting the form.");
                return;
            }
            let key = parent.getAttribute("data");
            let matches = color.value.match(rgbRegex);
            if (matches == null || typeof(matches) === "undefined") {
                console.debug("Color value does regex failed");
                error("An error occurred submitting the form.");
                return;
            }
            config[key] = [parseInt(matches[1]), parseInt(matches[2]), parseInt(matches[3])];
        }
        // Populate general
        let generalItems = document.getElementById("general").getElementsByClassName("item");
        for (let itemIndex = 0; itemIndex < generalItems.length; itemIndex++) {
            let item = generalItems[itemIndex];
            let parent = item.parentElement;
            if (!parent.hasAttribute("data")) {
                console.debug("General item with index " + itemIndex + " missing data attribute");
                error("An error occurred submitting the form.");
                return;
            }
            let key = parent.getAttribute("data");
            if (key === "city_id") {
                if (!item.hasAttribute("data") || item.getAttribute("data") === "") {
                    error("A city must be selected.");
                    return;
                }
                config[key] = item.getAttribute("data");
                config["city_name"] = item.value;
            }
            else if (key === "forecast_offset") {
                config[key] = parseInt(item.value) * 60 * 60;
            }
        }
        // Submit
        console.debug(config);
        showMessage("Saving");
        let request = new XMLHttpRequest();
        request.addEventListener("loadend", function () {
            if (request.status === 200) {
                showMessage("Saved")
            }
            else {
                error("Failed to submit form.")
            }
        });
        request.open("POST", "/config", true);
        request.setRequestHeader("Content-Type", "application/json");
        request.send(JSON.stringify(config));
    }

    function populateCityList(json) {
        let cityListElement = document.getElementById("city-list");
        let cityList = json["list"];
        for (let cityIndex = 0; cityIndex < cityList.length; cityIndex++) {
            let city = cityList[cityIndex];
            let id = city["id"];
            let name = city["name"];
            let country = city["sys"]["country"];
            let cityElement = document.createElement("span");
            cityElement.innerText = name + ", " + country;
            cityElement.setAttribute("data", id);
            if (cityIndex % 2 !== 0)
                cityElement.classList.add("row-blue");
            cityElement.classList.add("clickable");
            cityElement.classList.add("city");
            cityElement.addEventListener("click", function () {
                let cityInput = document.getElementById("city-input");
                cityInput.value = this.innerText;
                cityInput.setAttribute("data", this.getAttribute("data"));
                closeCityChooser();
            });
            cityListElement.appendChild(cityElement);
        }
    }

    function handleSearchSubmit(event) {
        event.preventDefault();
        // Reset list
        let cityListElement = document.getElementById("city-list");
        while (cityListElement.firstChild)
            cityListElement.removeChild(cityListElement.firstChild);
        // Do search
        let loadingImage = document.getElementById("loading-image");
        loadingImage.style.visibility = "visible";
        let query = document.getElementById("city-search").value;
        if (query === "")
            return;
        let request = new XMLHttpRequest();
        request.addEventListener("loadend", function () {
            if (request.status === 200) {
                try {
                    let json = JSON.parse(request.response);
                    if (typeof(json) === "undefined" || json === null)
                        return error("Invalid JSON data received from API");
                    showMessage();
                    populateCityList(json);
                }
                catch (e) {
                    console.log(e);
                    error("Failed to parse API JSON.");
                }
            }
            else {
                error("Failed to connect to API")
            }
            loadingImage.style.visibility = "hidden";
        });
        request.open("GET", "/search?query=" + encodeURI(query), true);
        request.send();
    }

    function handleReset() {
        let doReset = window.confirm("This will reset all settings to their defaults. Continue?");
        if (doReset) {
            reset();
            showMessage("Resetting");
            let request = new XMLHttpRequest();
            request.addEventListener("loadend", function () {
                loadConfig(populateConfigElements);
            });
            request.open("POST", "/config/reset", true);
            request.send();
        }
    }

    function main() {
        let cityChooser = document.getElementById("city-chooser");
        cityChooser.addEventListener("click", function (event) {
            if (event.target === cityChooser) {
                closeCityChooser();
            }
        });
        let citySearchForm = document.getElementById("city-search-form");
        citySearchForm.addEventListener("submit", handleSearchSubmit);
        let resetButton = document.getElementById("reset");
        resetButton.addEventListener("click", handleReset);
        let form = document.getElementById("main");
        form.addEventListener("submit", handleFormSubmit);
        loadConfig(populateConfigElements);
    }

    window.addEventListener("load", main)
};

Config();