function pageInit() {
    loadReleaseSelector();
    loadFilterSelector();
    showFeatures();
}

function loadFilterSelector() {
    const selector = document.getElementById('feature-filter');
    const whatsNewOption = document.createElement("option");
    const allOption = document.createElement("option");
    whatsNewOption.textContent = "What's New";
    whatsNewOption.value = '0';
    allOption.textContent = "All features";
    allOption.value =  "Date(option)";
    selector.appendChild(whatsNewOption);
    selector.appendChild(allOption);
}

function loadReleaseSelector() {
    const selector = document.getElementById('release-options');
    const releases = getReleases();
    releases.forEach(option => {
        const newOption = document.createElement("option");
        newOption.textContent = option;
        newOption.value =  Date(option);
        selector.appendChild(newOption);
    })
}

function showFeatures() {
    const release = document.getElementById('release-options').selectedOptions[0].text;
    const showOption = document.getElementById("feature-filter").selectedOptions[0].value;
    const allFeatures = document.getElementsByClassName("feature");
    for (let i = 0; i < allFeatures.length; i++) {
        if (isVisibleFeature(allFeatures[i], showOption, release)) allFeatures[i].style.display = "block";
        else allFeatures[i].style.display = "none";
    }
}

function isVisibleFeature(feature, showOption, release) {
    if (feature.hasAttribute("data-release")) {
        const featureRelease = feature.getAttribute("data-release");
        return (showOption === '0') ? featureRelease === release : featureRelease <= release;
    }
    return false;
}

function getReleases() {
    const featureDivs = document.getElementsByClassName("feature");
    const releases = []
    for (let i = 0; i < featureDivs.length; i++) {
        const div = featureDivs[i];
        if (div.hasAttribute("data-release")) {
            const release = div.getAttribute('data-release');
            if (!releases.includes(release)) releases.push(release);
        }
    }
    return releases;
}
