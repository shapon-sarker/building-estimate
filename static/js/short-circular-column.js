document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calculatorForm');
    const resultsSection = document.getElementById('results');
    const materialsTableBody = document.getElementById('materialsTableBody');
    const reinforcementTableBody = document.getElementById('reinforcementTableBody');
    const totalAmountElement = document.getElementById('totalAmount');

    // Update RCC ratio total
    function updateRccRatioTotal() {
        const type1 = parseFloat(document.getElementById('type1').value) || 0;
        const type2 = parseFloat(document.getElementById('type2').value) || 0;
        const type3 = parseFloat(document.getElementById('type3').value) || 0;
        const total = type1 + type2 + type3;
        document.getElementById('totalRatio').textContent = total.toFixed(2);
    }

    // Add event listeners for RCC ratio inputs
    document.getElementById('type1').addEventListener('input', updateRccRatioTotal);
    document.getElementById('type2').addEventListener('input', updateRccRatioTotal);
    document.getElementById('type3').addEventListener('input', updateRccRatioTotal);

    // Format number with commas and decimal places
    function formatNumber(number, decimals = 2) {
        return number.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    // Collect form data
    function getFormData() {
        const formData = {
            column_nos: [],
            column_dia: [],
            clear_cover: [],
            height: [],
            type1: parseFloat(document.getElementById('type1').value) || 0,
            type2: parseFloat(document.getElementById('type2').value) || 0,
            type3: parseFloat(document.getElementById('type3').value) || 0,
            large_dia_size: [],
            large_dia_nos: [],
            small_dia_size: [],
            small_dia_nos: [],
            dev_length: [],
            spiral_dia: [],
            spiral_spacing: [],
            hook_length: [],
            spiral_length1: [],
            spiral_length2: [],
            cement_rate: parseFloat(document.getElementById('cement_rate').value) || 0,
            sand_rate: parseFloat(document.getElementById('sand_rate').value) || 0,
            stone_rate: parseFloat(document.getElementById('stone_rate').value) || 0,
            brick_rate: parseFloat(document.getElementById('brick_rate').value) || 0,
            rebar_rate: parseFloat(document.getElementById('rebar_rate').value) || 0,
            formwork_rate: parseFloat(document.getElementById('formwork_rate').value) || 0,
            casting_rate: parseFloat(document.getElementById('casting_rate').value) || 0,
            material_wastage: parseFloat(document.getElementById('material_wastage').value) || 0
        };

        // Collect array data
        const arrayFields = [
            'column_nos', 'column_dia', 'clear_cover', 'height',
            'large_dia_size', 'large_dia_nos', 'small_dia_size', 'small_dia_nos',
            'dev_length', 'spiral_dia', 'spiral_spacing', 'hook_length',
            'spiral_length1', 'spiral_length2'
        ];

        arrayFields.forEach(field => {
            const inputs = form.querySelectorAll(`input[name="${field}[]"]`);
            inputs.forEach(input => {
                formData[field].push(parseFloat(input.value) || 0);
            });
        });

        return formData;
    }

    // Update results in the UI
    function updateResults(data) {
        if (!data || typeof data !== 'object') {
            console.error('Invalid data received from server');
            alert('Invalid data received from server. Please try again.');
            return;
        }

        // Update materials table
        materialsTableBody.innerHTML = '';
        const materials = [
            { key: 'cement', label: 'Cement (Bag)' },
            { key: 'sand', label: 'Sand (CFT)' },
            { key: 'stone', label: 'Stone/Brick Chips (CFT)' },
            { key: 'rebar', label: 'Rebar (Ton)' },
            { key: 'formwork', label: 'Formwork (SFT)' },
            { key: 'casting', label: 'Casting (CFT)' }
        ];

        if (data.materials) {
            materials.forEach(material => {
                const materialData = data.materials[material.key];
                if (materialData) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${material.label}</td>
                        <td>${formatNumber(materialData.quantity || 0)}</td>
                        <td>${material.key === 'rebar' ? formatNumber(data.materials.material_wastage || 0) : ''}</td>
                        <td>${formatNumber(materialData.wastage_quantity || 0)}</td>
                        <td>${formatNumber(materialData.rate || 0)}</td>
                        <td>${formatNumber(materialData.amount || 0)}</td>
                    `;
                    materialsTableBody.appendChild(row);
                }
            });
        }

        // Update total amount
        if (data.total_amount !== undefined) {
            totalAmountElement.textContent = formatNumber(data.total_amount);
        } else {
            totalAmountElement.textContent = '0.00';
        }

        // Update reinforcement table
        reinforcementTableBody.innerHTML = '';
        
        // Add reinforcement details
        let totalRebar = 0;
        
        if (data.rebar_details && typeof data.rebar_details === 'object') {
            for (const [size, quantity] of Object.entries(data.rebar_details)) {
                if (quantity > 0) {
                    const quantityInTons = quantity / 1000;  // Convert kg to tons
                    totalRebar += quantityInTons;
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>Φ${size}</td>
                        <td>${formatNumber(quantityInTons)}</td>
                    `;
                    reinforcementTableBody.appendChild(row);
                }
            }

            // Add total row
            if (totalRebar > 0) {
                const totalRow = document.createElement('tr');
                totalRow.innerHTML = `
                    <td><strong>Total</strong></td>
                    <td><strong>${formatNumber(totalRebar)}</strong></td>
                `;
                reinforcementTableBody.appendChild(totalRow);
            }
        }

        // Show results section with animation
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.classList.add('show');
        }, 10);
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.classList.add('loading');
        submitButton.textContent = 'Calculating...';

        try {
            const formData = getFormData();
            console.log('Sending data:', formData); // Debug log

            const response = await fetch('/calculate-short-circular-column', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Received data:', data); // Debug log

            if (data.error) {
                throw new Error(data.error);
            }

            updateResults(data);
        } catch (error) {
            console.error('Error details:', error);
            alert(`Calculation error: ${error.message || 'Please try again.'}`);
        } finally {
            // Reset loading state
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
            submitButton.textContent = originalText;
        }
    });

    // Handle form reset
    form.addEventListener('reset', function() {
        resultsSection.classList.remove('show');
        setTimeout(() => {
            resultsSection.style.display = 'none';
            materialsTableBody.innerHTML = '';
            reinforcementTableBody.innerHTML = '';
            totalAmountElement.textContent = '0.00';
        }, 300);
    });
}); 