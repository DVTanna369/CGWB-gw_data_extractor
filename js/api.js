import * as ui from './ui.js';

const BASE_API_URL = 'http://127.0.0.1:5000';
const API_ENDPOINTS = {
    datasets: `${BASE_API_URL}/get-datasets`,
    states: `${BASE_API_URL}/get-states`,
    districts: `${BASE_API_URL}/get-districts`,
    rivers: `${BASE_API_URL}/get-rivers`,
    tributaries: `${BASE_API_URL}/get-tributaries`,
    agencies: `${BASE_API_URL}/get-agencies`,
    download: `${BASE_API_URL}/download-data`
};

async function postRequest(endpoint, payload = {}) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown server error occurred." }));
        throw new Error(errorData.message);
    }
    return response.json();
}

export async function loadDatasets() {
    return await postRequest(API_ENDPOINTS.datasets);
}

export async function loadStates() {
    const datasetCode = ui.elements.datasetSelect.value;
    if (!datasetCode) return [];
    return await postRequest(API_ENDPOINTS.states, { datasetCode });
}

export async function loadDistricts() {
    const stateCode = ui.elements.stateSelect.value;
    const datasetCode = ui.elements.datasetSelect.value;
    if (!stateCode || !datasetCode) return [];
    return await postRequest(API_ENDPOINTS.districts, { stateCode, datasetCode });
}

export async function loadRivers() {
    const datasetCode = ui.elements.datasetSelect.value;
    if (!datasetCode) return [];
    return await postRequest(API_ENDPOINTS.rivers, { datasetCode });
}

export async function loadTributaries() {
    const basinCode = ui.elements.riverSelect.value;
    const datasetCode = ui.elements.datasetSelect.value;
    if (!basinCode || !datasetCode) return [];
    return await postRequest(API_ENDPOINTS.tributaries, { basinCode, datasetCode });
}

export async function loadAgencies() {
    const category = ui.elements.categorySelect.value;
    const datasetcode = ui.elements.datasetSelect.value;
    const payload = { datasetcode, district_id: 0, tributaryid: 0, localriverid: 0 };

    if (category === 'admin') {
        const districtSelect = ui.elements.districtSelect;
        if (!districtSelect.value) return [];
        payload.district_id = districtSelect.options[districtSelect.selectedIndex].dataset.id;
    } else if (category === 'basin') {
        const tributarySelect = ui.elements.tributarySelect;
        if (!tributarySelect.value) return [];
        payload.tributaryid = tributarySelect.options[tributarySelect.selectedIndex].dataset.id;
    } else {
        return [];
    }
    
    return await postRequest(API_ENDPOINTS.agencies, payload);
}

export async function downloadData(formData) {
    const response = await fetch(API_ENDPOINTS.download, {
        method: 'POST',
        body: new URLSearchParams(formData)
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Server error during data download.');
    }
    return response.json();
}