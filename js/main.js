import * as api from './api.js';
import * as ui from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    // --- Initial Setup ---
    ui.initializeUI();
    handleLoadDatasets(); // Initial data load

    // --- Event Listeners ---
    ui.elements.datasetSelect.addEventListener('change', handleDatasetSelection);
    ui.elements.categorySelect.addEventListener('change', handleCategorySelection);
    ui.elements.stateSelect.addEventListener('change', handleStateSelection);
    ui.elements.riverSelect.addEventListener('change', handleRiverSelection);
    ui.elements.districtSelect.addEventListener('change', handleDistrictSelection);
    ui.elements.tributarySelect.addEventListener('change', handleTributarySelection);

    ui.elements.form.addEventListener('submit', handleFormSubmit);
    ui.elements.downloadCsvBtn.addEventListener('click', ui.handleCSVDownload);
    ui.elements.form.addEventListener('reset', ui.handleFormReset);
});

// --- Handler Functions ---

async function handleLoadDatasets() {
    ui.resetSelect(ui.elements.datasetSelect, 'Loading Datasets...', true);
    try {
        const datasets = await api.loadDatasets();
        ui.populateDatasets(datasets);
    } catch (error) {
        console.error("Failed to load datasets:", error);
        ui.resetSelect(ui.elements.datasetSelect, 'Could not load datasets', true);
    }
}

function handleDatasetSelection() {
    ui.handleDatasetChange();
    ui.resetSelect(ui.elements.stateSelect, 'Select Category First');
    ui.resetSelect(ui.elements.districtSelect, 'Select State First');
    ui.resetSelect(ui.elements.riverSelect, 'Select Category First');
    ui.resetSelect(ui.elements.tributarySelect, 'Select River First');
    ui.resetSelect(ui.elements.agencySelect, 'Select Options First');
}

async function handleCategorySelection() {
    const category = ui.elements.categorySelect.value;
    ui.handleCategoryChange(category);
    if (category === 'admin') {
        ui.resetSelect(ui.elements.stateSelect, 'Loading States...', false);
        try {
            const states = await api.loadStates();
            ui.populateStates(states);
        } catch (e) { ui.resetSelect(ui.elements.stateSelect, 'Could not load states'); }
    } else if (category === 'basin') {
        ui.resetSelect(ui.elements.riverSelect, 'Loading Rivers...', false);
        try {
            const rivers = await api.loadRivers();
            ui.populateRivers(rivers);
        } catch (e) { ui.resetSelect(ui.elements.riverSelect, 'Could not load rivers'); }
    }
}

async function handleStateSelection() {
    ui.resetSelect(ui.elements.districtSelect, 'Loading Districts...', false);
    try {
        const districts = await api.loadDistricts();
        ui.populateDistricts(districts);
    } catch (e) { ui.resetSelect(ui.elements.districtSelect, 'Could not load districts'); }
}

async function handleRiverSelection() {
    ui.resetSelect(ui.elements.tributarySelect, 'Loading Tributaries...', false);
    try {
        const tributaries = await api.loadTributaries();
        ui.populateTributaries(tributaries);
    } catch (e) { ui.resetSelect(ui.elements.tributarySelect, 'Could not load tributaries'); }
}

async function handleDistrictSelection() {
    ui.resetSelect(ui.elements.agencySelect, 'Loading Agencies...');
    try {
        const agencies = await api.loadAgencies();
        ui.populateAgencies(agencies);
    } catch(e) { ui.resetSelect(ui.elements.agencySelect, 'Could not load agencies'); }
}

async function handleTributarySelection() {
    ui.resetSelect(ui.elements.agencySelect, 'Loading Agencies...');
    try {
        const agencies = await api.loadAgencies();
        ui.populateAgencies(agencies);
    } catch(e) { ui.resetSelect(ui.elements.agencySelect, 'Could not load agencies'); }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    ui.showLoadingState();
    try {
        const formData = ui.getFormData();
        const data = await api.downloadData(formData);
        ui.displayResults(data);
    } catch (error) {
        console.error("Form submission error:", error);
        ui.displayError(error.message);
    } finally {
        ui.hideLoadingState();
    }
}