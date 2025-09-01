// --- Element References ---
export const elements = {
    datasetSelect: document.getElementById('datasetName'),
    categorySelect: document.getElementById('dataCategory'),
    adminView: document.getElementById('admin-view'),
    basinView: document.getElementById('basin-view'),
    stateSelect: document.getElementById('stateName'),
    districtSelect: document.getElementById('districtName'),
    riverSelect: document.getElementById('riverName'),
    tributarySelect: document.getElementById('tributaryName'),
    agencySelect: document.getElementById('agencyName'),
    form: document.getElementById('search-form'),
    submitBtn: document.getElementById('submit-btn'),
    btnText: document.getElementById('btn-text'),
    btnLoader: document.getElementById('btn-loader'),
    resultsContainer: document.getElementById('results-container'),
    statusMessage: document.getElementById('status-message'),
    resultsTableBody: document.getElementById('results-table-body'),
    downloadCsvBtn: document.getElementById('download-csv-btn'),
    districtHeader: document.getElementById('district-header')
};

let fullCsvData = '';

// --- UI Helper Functions ---
export function resetSelect(select, message, disabled = true) {
    select.innerHTML = `<option value="">${message}</option>`;
    select.disabled = disabled;
}

export function initializeUI() {
    flatpickr("#startdate", { dateFormat: "Y-m-d" });
    flatpickr("#enddate", { dateFormat: "Y-m-d" });
    resetSelect(elements.datasetSelect, 'Loading Datasets...');
    resetSelect(elements.categorySelect, 'Select Dataset First');
    resetSelect(elements.stateSelect, 'Select Category First');
    resetSelect(elements.districtSelect, 'Select State First');
    resetSelect(elements.riverSelect, 'Select Category First');
    resetSelect(elements.tributarySelect, 'Select River First');
    resetSelect(elements.agencySelect, 'Select Options First');
}

// --- Dropdown Population Functions ---
export function populateDatasets(datasets) {
    elements.datasetSelect.innerHTML = '<option value="">Select Dataset</option>';
    datasets.sort((a, b) => a.datasetdescription.localeCompare(b.datasetdescription));
    datasets.forEach(dataset => {
        const option = document.createElement('option');
        option.value = dataset.datasetcode;
        option.textContent = dataset.datasetdescription;
        elements.datasetSelect.appendChild(option);
    });
    elements.datasetSelect.disabled = false;
}

export function populateStates(states) {
    elements.stateSelect.innerHTML = '<option value="">Select State</option>';
    states.sort((a, b) => a.state.localeCompare(b.state));
    states.forEach(state => {
        const option = document.createElement('option');
        option.value = state.statecode;
        option.textContent = state.state;
        elements.stateSelect.appendChild(option);
    });
}

export function populateDistricts(districts) {
    elements.districtSelect.innerHTML = '<option value="">Select District</option>';
    districts.sort((a, b) => a.districtname.localeCompare(b.districtname));
    districts.forEach(district => {
        const option = document.createElement('option');
        const internalName = district.districtname;
        option.value = internalName;
        option.textContent = internalName;
        option.dataset.id = district.district_id;
        elements.districtSelect.appendChild(option);
    });
}

export function populateRivers(rivers) {
    elements.riverSelect.innerHTML = '<option value="">Select River</option>';
    rivers.sort((a, b) => a.basin.localeCompare(b.basin));
    rivers.forEach(river => {
        const option = document.createElement('option');
        option.value = river.basincode;
        option.textContent = river.basin;
        option.dataset.name = river.basin;
        elements.riverSelect.appendChild(option);
    });
}

export function populateTributaries(tributaries) {
    elements.tributarySelect.innerHTML = '<option value="">Select Tributary</option>';
    tributaries.sort((a, b) => a.tributary.localeCompare(b.tributary));
    tributaries.forEach(trib => {
        const option = document.createElement('option');
        option.value = trib.tributary;
        option.textContent = trib.tributary;
        option.dataset.id = trib.tributaryid;
        elements.tributarySelect.appendChild(option);
    });
}

export function populateAgencies(agencies) {
    const nationalAgencies = agencies.filter(agency => {
        const fullName = agency.agencyname;
        const match = fullName.match(/\(([^)]+)\)$/);
        const shortName = match ? match[1] : fullName;
        return shortName === 'CWC' || shortName === 'CGWB';
    });

    if (nationalAgencies.length > 0) {
        elements.agencySelect.innerHTML = '<option value="">Select Agency</option>';
        nationalAgencies.sort((a, b) => a.agencyname.localeCompare(b.agencyname));
        nationalAgencies.forEach(agency => {
            const option = document.createElement('option');
            const fullName = agency.agencyname;
            const match = fullName.match(/\(([^)]+)\)$/);
            const shortName = match ? match[1] : fullName;
            option.value = shortName;
            option.textContent = fullName;
            elements.agencySelect.appendChild(option);
        });
        elements.agencySelect.disabled = false;
    } else {
        resetSelect(elements.agencySelect, 'No national agency data available');
    }
}

// --- UI State Changers ---
export function handleDatasetChange() {
    const selectedOption = elements.datasetSelect.options[elements.datasetSelect.selectedIndex];
    if (!selectedOption || !selectedOption.text) {
        elements.categorySelect.disabled = true;
        return;
    }
    const isGroundwater = selectedOption.text.toLowerCase().includes('ground water level');
    if (elements.datasetSelect.value) {
        elements.categorySelect.innerHTML = '<option value="">Select Category</option><option value="admin">Admin</option>';
        if (!isGroundwater) {
            elements.categorySelect.innerHTML += '<option value="basin">Basin</option>';
        }
        elements.categorySelect.disabled = false;
    }
}

export function handleCategoryChange(category) {
    const isAdmin = category === 'admin';
    elements.adminView.classList.toggle('hidden', !isAdmin);
    elements.basinView.classList.toggle('hidden', isAdmin);
}

export function showLoadingState() {
    elements.submitBtn.disabled = true;
    elements.btnText.classList.add('hidden');
    if (elements.btnLoader) elements.btnLoader.classList.remove('hidden');
    elements.resultsContainer.classList.remove('hidden');
    elements.downloadCsvBtn.classList.add('hidden');
    elements.resultsTableBody.innerHTML = '';
    elements.statusMessage.textContent = 'Fetching data... This can take several minutes for large requests. Please be patient.';
    elements.statusMessage.className = 'mb-4 p-4 bg-blue-500/30 rounded-lg';
}

export function hideLoadingState() {
    elements.submitBtn.disabled = false;
    elements.btnText.classList.remove('hidden');
    if (elements.btnLoader) elements.btnLoader.classList.add('hidden');
}

export function getFormData() {
    const formData = new FormData();
    formData.append('startdate', document.getElementById('startdate').value);
    formData.append('enddate', document.getElementById('enddate').value);
    formData.append('agencyName', elements.agencySelect.value);
    
    // ✅ NEW: Read the selected download format from the radio buttons
    const downloadFormat = document.querySelector('input[name="downloadFormat"]:checked').value;
    formData.append('downloadFormat', downloadFormat);

    const category = elements.categorySelect.value;
    const selectedDatasetOption = elements.datasetSelect.options[elements.datasetSelect.selectedIndex];
    formData.append('dataCategory', category);
    formData.append('datasetName', selectedDatasetOption.textContent);

    if (category === 'admin') {
        const selectedStateText = elements.stateSelect.options[elements.stateSelect.selectedIndex].text;
        formData.append('stateName', selectedStateText);
        formData.append('districtName', elements.districtSelect.value);
    } else if (category === 'basin') {
        const selectedRiverOption = elements.riverSelect.options[elements.riverSelect.selectedIndex];
        formData.append('riverName', selectedRiverOption.dataset.name);
        formData.append('tributaryName', elements.tributarySelect.value);
    }
    return formData;
}

export function displayResults(data) {
    if (data.totalRecords > 0) {
        elements.statusMessage.textContent = `Success! Found ${data.totalRecords} records. Previewing first 100.`;
        elements.statusMessage.className = 'mb-4 p-4 bg-green-500/30 rounded-lg';
        elements.resultsTableBody.innerHTML = data.preview.map(row => `
            <tr class="border-b border-white/10 hover:bg-white/10">
                <td class="p-3">${row.stationCode || 'N/A'}</td>
                <td class="p-3">${row.dataTime || 'N/A'}</td>
                <td class="p-3">${row.dataValue || 'N/A'}</td>
                <td class="p-3">${row.latitude || 'N/A'}</td>
                <td class="p-3">${row.longitude || 'N/A'}</td>
            </tr>`).join('');
        fullCsvData = data.csvData;
        elements.downloadCsvBtn.dataset.filename = data.filename;
        elements.downloadCsvBtn.classList.remove('hidden');
    } else {
        elements.statusMessage.textContent = 'No data found for the selected criteria.';
        elements.statusMessage.className = 'mb-4 p-4 bg-yellow-500/30 rounded-lg';
        elements.resultsTableBody.innerHTML = '';
    }
}

export function displayError(message) {
    elements.statusMessage.textContent = `Error: ${message}`;
    elements.statusMessage.className = 'mb-4 p-4 bg-red-500/30 rounded-lg';
    elements.resultsTableBody.innerHTML = '';
}

export function handleCSVDownload() {
    if (!fullCsvData) return;
    const blob = new Blob([fullCsvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", elements.downloadCsvBtn.dataset.filename || "data_export.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export function handleFormReset() {
    elements.resultsContainer.classList.add('hidden');
    resetSelect(elements.categorySelect, 'Select Dataset First');
    resetSelect(elements.stateSelect, 'Select Category First');
    resetSelect(elements.districtSelect, 'Select State First');
    resetSelect(elements.riverSelect, 'Select Category First');
    resetSelect(elements.tributarySelect, 'Select River First');
    resetSelect(elements.agencySelect, 'Select Options First');
    elements.adminView.classList.remove('hidden');
    elements.basinView.classList.add('hidden');
}
