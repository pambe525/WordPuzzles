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
    allOption.value = "Date(option)";
    selector.appendChild(whatsNewOption);
    selector.appendChild(allOption);
}

function loadReleaseSelector() {
    const selector = document.getElementById('release-options');
    const releases = getReleases().sort().reverse();
    releases.forEach(option => {
        const newOption = document.createElement("option");
        newOption.textContent = option;
        newOption.value = option;
        selector.appendChild(newOption);
    })
}

function showFeatures() {
    const release = document.getElementById('release-options').selectedOptions[0].text;
    const showOption = document.getElementById("feature-filter").selectedOptions[0].value;
    // const allFeatures = document.getElementsByClassName("feature");
    const allFeatures = document.querySelectorAll('[data-release]');
    for (let i = 0; i < allFeatures.length; i++) {
        if (isVisibleFeature(allFeatures[i], showOption, release)) allFeatures[i].style.display = "block";
        else allFeatures[i].style.display = "none";
    }
}

function isVisibleFeature(feature, showOption, target_release) {
    const featureReleases = feature.getAttribute("data-release").split(" ");
    if (showOption === '0') return featureReleases.includes(target_release);
    for (let i = 0; i < featureReleases.length; i++) {
        if (featureReleases[i] <= target_release) return true;
    }
    return false;
}

function getReleases() {
    const featureDivs = document.querySelectorAll('[data-release]');
    const releases_options = []
    for (let i = 0; i < featureDivs.length; i++) {
        const div = featureDivs[i];
        if (div.hasAttribute("data-release")) {
            const releases = div.getAttribute('data-release').split(" ");
            releases.forEach( (release) => {
                if (!releases_options.includes(release)) releases_options.push(release);
            })
        }
    }
    return releases_options;
}
